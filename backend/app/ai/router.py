"""Enrutador de modelos intercambiables (Gemini Free, Groq Free, Ollama, LM Studio, Determinista)."""

from app.ai.base import EvaluationContext, LLMProvider
from app.ai.providers import (
    DeterministicOfflineAnalyzer,
    GeminiProvider,
    OpenAICompatibleProvider,
)
from app.core.config import Settings, get_settings
from app.schemas.evaluation import AIEvaluationPayload


class ModelRouter:
    """Selecciona el proveedor IA activo sin acoplar la lógica de evaluación a un único modelo."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def resolve_provider(
        self, provider_name: str, model_override: str | None = None
    ) -> tuple[LLMProvider, str]:
        name = provider_name.lower().strip()

        if name == "gemini":
            return (
                GeminiProvider(api_key=self.settings.gemini_api_key),
                model_override or self.settings.gemini_model,
            )
        if name == "groq":
            return (
                OpenAICompatibleProvider(
                    provider_name="groq",
                    base_url="https://api.groq.com/openai/v1",
                    api_key=self.settings.groq_api_key,
                    require_api_key=True,
                ),
                model_override or self.settings.groq_model,
            )
        if name == "ollama":
            base = self.settings.ollama_base_url.rstrip("/")
            if not base.endswith("/v1"):
                base = f"{base}/v1"
            return (
                OpenAICompatibleProvider(provider_name="ollama", base_url=base),
                model_override or self.settings.ollama_model,
            )
        if name == "lmstudio":
            return (
                OpenAICompatibleProvider(
                    provider_name="lmstudio", base_url=self.settings.lmstudio_base_url
                ),
                model_override or self.settings.lmstudio_model,
            )
        if name == "deterministic":
            return DeterministicOfflineAnalyzer(), "evidence-auditor-v1"

        raise ValueError(f"Proveedor IA no soportado: '{provider_name}'.")

    async def evaluate_with_provider(
        self,
        ctx: EvaluationContext,
        provider_name: str,
        model_override: str | None = None,
    ) -> tuple[str, str, AIEvaluationPayload]:
        provider, model_name = self.resolve_provider(provider_name, model_override)
        payload = await provider.evaluate(ctx, model_name)
        return provider.provider_name, model_name, payload

    def list_provider_statuses(self) -> list[dict[str, str | bool]]:
        return [
            {
                "provider": "gemini",
                "label": "Google Gemini API (Free Tier)",
                "configured": bool(self.settings.gemini_api_key),
                "default_model": self.settings.gemini_model,
                "mode": "cloud_free",
            },
            {
                "provider": "groq",
                "label": "Groq API (Free Tier)",
                "configured": bool(self.settings.groq_api_key),
                "default_model": self.settings.groq_model,
                "mode": "cloud_free",
            },
            {
                "provider": "ollama",
                "label": "Ollama (Local)",
                "configured": True,
                "default_model": self.settings.ollama_model,
                "mode": "local",
            },
            {
                "provider": "lmstudio",
                "label": "LM Studio (Local)",
                "configured": True,
                "default_model": self.settings.lmstudio_model,
                "mode": "local",
            },
            {
                "provider": "deterministic",
                "label": "Auditor Determinista Offline (Sin API externa)",
                "configured": True,
                "default_model": "evidence-auditor-v1",
                "mode": "offline_deterministic",
            },
        ]
