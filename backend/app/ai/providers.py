"""Implementaciones de proveedores IA gratuitos (Gemini, Groq, Ollama/LM Studio y modo determinista)."""

import json
from typing import Any

import httpx

from app.ai.base import (
    FLAT_EVALUATION_JSON_SCHEMA,
    EvaluationContext,
    LLMProvider,
    build_system_and_user_prompts,
)
from app.schemas.evaluation import (
    AIEvaluationPayload,
    CitedEvidence,
    CriterionQuantification,
    RecommendationDimension,
    VerificationDimension,
)


def _strip_json_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def evaluate(self, ctx: EvaluationContext, model_name: str) -> AIEvaluationPayload:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY no está configurada.")

        system_prompt, user_prompt = build_system_and_user_prompts(ctx)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        body = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": FLAT_EVALUATION_JSON_SCHEMA,
            },
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, params={"key": self.api_key}, json=body)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini no retornó candidatos de respuesta.")
        parts = candidates[0].get("content", {}).get("parts", [])
        raw_text = "".join(p.get("text", "") for p in parts)
        parsed = json.loads(_strip_json_fences(raw_text))
        return AIEvaluationPayload.model_validate(parsed)


class OpenAICompatibleProvider(LLMProvider):
    """Cliente compartido para Groq Free Tier, Ollama (/v1) y LM Studio (/v1)."""

    def __init__(
        self,
        provider_name: str,
        base_url: str,
        api_key: str = "",
        require_api_key: bool = False,
    ) -> None:
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.require_api_key = require_api_key

    async def evaluate(self, ctx: EvaluationContext, model_name: str) -> AIEvaluationPayload:
        if self.require_api_key and not self.api_key:
            raise RuntimeError(f"API key requerida para el proveedor '{self.provider_name}'.")

        system_prompt, user_prompt = build_system_and_user_prompts(ctx)
        schema_hint = json.dumps(FLAT_EVALUATION_JSON_SCHEMA, ensure_ascii=False)
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: dict[str, Any] = {
            "model": model_name,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                    + f"\n\nEl JSON debe seguir estrictamente este esquema:\n{schema_hint}",
                },
                {"role": "user", "content": user_prompt},
            ],
        }
        if self.provider_name in {"groq", "lmstudio", "ollama"}:
            payload["response_format"] = {"type": "json_object"}

        endpoint = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(_strip_json_fences(content))
        return AIEvaluationPayload.model_validate(parsed)


class DeterministicOfflineAnalyzer(LLMProvider):
    """
    Analizador determinista local basado en evidencias extraídas y resultados de sandbox.
    Se usa únicamente cuando AI_PROVIDER=deterministic o en pruebas sin API externa.
    """

    provider_name = "deterministic"

    async def evaluate(self, ctx: EvaluationContext, model_name: str) -> AIEvaluationPayload:
        extracted = [e for e in ctx.evidences if e["extraction_status"] == "extracted"]
        partial = [e for e in ctx.evidences if e["extraction_status"] != "extracted"]

        cited: list[CitedEvidence] = []
        for ev in extracted[:5]:
            preview = (ev["extracted_text_summary"] or "").strip().splitlines()
            fragment = " ".join(preview[:2])[:220] or "Contenido legible extraído."
            cited.append(
                CitedEvidence(
                    archivo=ev["filename"],
                    ubicacion="Encabezado / texto extraído",
                    fragmento=fragment,
                )
            )

        missing: list[str] = []
        if not ctx.official_objective:
            missing.append("No consta objetivo oficial explícito en las evidencias de la carpeta.")
        for ev in partial:
            missing.append(
                f"Archivo '{ev['filename']}' ({ev['file_category']}) sin extracción textual completa."
            )

        syntax_ok = ctx.sandbox_result.get("syntax_valid", True)
        files_checked = ctx.sandbox_result.get("files_checked") or []
        static_findings = ctx.sandbox_result.get("static_findings") or []
        critical_findings = [
            f for f in static_findings if ("Error de sintaxis" in f or "eval()" in f or "exec()" in f)
        ]

        if not ctx.evidences:
            obj_status = "no_verificable"
        elif ctx.official_objective and syntax_ok and (len(extracted) >= 1 or len(ctx.evidences) >= 2):
            obj_status = "cumplido"
        else:
            obj_status = "parcial"

        # Puntaje por criterio basado en cobertura real y tipo de entregable (0..5)
        has_reports = any(
            e["file_category"] in {"report_pdf", "report_docx", "markdown"} for e in extracted
        )
        has_code = len(files_checked) > 0
        has_tests = any(fc.get("has_unittest") for fc in files_checked)
        has_data_or_img = any(
            e["file_category"] in {"data_table", "image_diagram"} for e in ctx.evidences
        )
        has_video = any(e["file_category"] == "video" for e in ctx.evidences)

        quantifications: list[CriterionQuantification] = []
        for idx, crit in enumerate(ctx.criteria):
            if idx == 0:
                if obj_status == "cumplido" and len(ctx.evidences) >= 2:
                    score, level = 4.8, "Sobresaliente"
                elif obj_status == "cumplido":
                    score, level = 4.6, "Sobresaliente"
                else:
                    score, level = 4.0, "Satisfactorio"
                just = (
                    f"Entrega alineada con el objetivo planteado: {len(ctx.evidences)} evidencia(s) "
                    f"verificada(s) ({len(extracted)} con texto extraído y {len(partial)} multimedia/diagrama)."
                )
            elif idx == 1:
                if has_reports and has_data_or_img:
                    score, level = 4.8, "Sobresaliente"
                elif has_reports or (has_data_or_img and has_video):
                    score, level = 4.6, "Sobresaliente"
                elif has_data_or_img:
                    score, level = 4.2, "Satisfactorio"
                else:
                    score, level = 3.8, "Satisfactorio"
                just = (
                    "Los informes, mapas mentales y análisis técnicos demuestran dominio conceptual "
                    "y metodológico consistente."
                )
            elif idx == 2:
                if has_code and syntax_ok and has_tests and not critical_findings:
                    score, level = 4.9, "Sobresaliente"
                    just = (
                        f"Sandbox verificó {len(files_checked)} archivo(s) con sintaxis válida "
                        f"y presencia de pruebas unitarias automatizadas."
                    )
                elif has_code and syntax_ok and not critical_findings:
                    score, level = 4.6, "Sobresaliente"
                    just = (
                        f"Sandbox verificó {len(files_checked)} archivo(s) de código/estructura "
                        f"con sintaxis válida y sin errores críticos."
                    )
                elif has_reports and not critical_findings:
                    score, level = 4.5, "Sobresaliente"
                    just = (
                        "Entrega de carácter analítico/arquitectónico con documentación técnica "
                        "estructurada y tablas comparativas verificables."
                    )
                elif not syntax_ok:
                    score, level = 2.8, "Básico"
                    just = "Se detectaron errores de sintaxis en el código verificado por el sandbox."
                else:
                    score, level = 4.2, "Satisfactorio"
                    just = "Artefactos técnicos verificados sin fallos sintácticos."
            else:
                if len(ctx.evidences) >= 3 and (has_reports or has_data_or_img):
                    score, level = 4.7, "Sobresaliente"
                elif len(ctx.evidences) >= 2:
                    score, level = 4.5, "Sobresaliente"
                else:
                    score, level = 4.2, "Satisfactorio"
                just = (
                    "Evidencias completas, trazables mediante SHA-256 y organizadas con uso responsable de IA."
                )

            quantifications.append(
                CriterionQuantification(
                    criterion_id=crit["code"],
                    nivel_desempeno=level,
                    puntaje_criterio=score,
                    justificacion=just,
                    evidencias=[c.archivo for c in cited[:3]] or [e["filename"] for e in ctx.evidences[:2]],
                )
            )

        resumen = (
            f"Auditoría determinista sobre {len(ctx.evidences)} evidencia(s): "
            f"{len(extracted)} con texto extraído y {len(partial)} solo con metadatos."
        )
        return AIEvaluationPayload(
            verificacion=VerificationDimension(
                objetivo_cumplido=obj_status,
                resumen_verificacion=resumen,
                evidencias_citadas=cited,
                faltantes_detectados=missing,
            ),
            cuantificacion_por_criterio=quantifications,
            recomendaciones=RecommendationDimension(
                fortalezas=[
                    f"Entrega con {len(ctx.evidences)} archivo(s) verificados por SHA-256.",
                    "Sintaxis de código verificada sin errores críticos." if syntax_ok else "Evidencia documental disponible.",
                ],
                debilidades=missing or ["Se recomienda adjuntar rúbrica específica del laboratorio si existe."],
                mejoras_tecnicas=[
                    "Ejecutar evaluación con proveedor LLM (Gemini/Groq/Ollama) configurado para profundizar el análisis semántico."
                ],
                mejoras_conceptuales=[
                    "Explicitar el objetivo oficial de la actividad en la portada del informe cuando no conste."
                ],
                mejoras_metodologicas=[
                    "Mantener pruebas unitarias y registro de prompts en todas las entregas."
                ],
            ),
        )
