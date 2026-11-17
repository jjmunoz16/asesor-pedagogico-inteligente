---
name: ai-evaluation-harness
description: >-
  Reglas para el harness de evaluación académica en 3 dimensiones, enrutamiento de modelos gratuitos y validación Pydantic/JSON Schema.
---

# AI Evaluation Harness — Asesor Pedagógico Inteligente

1. **Patrón:** "Modelo intercambiable, harness permanente". Los proveedores (`Gemini Free`, `Groq Free`, `Ollama/LM Studio`) implementan una interfaz común en `backend/app/ai/`.
2. **Método obligatorio (`AGENTS.md` §3):** Toda evaluación debe producir exactamente:
   - `verificacion`: cumplimiento del objetivo + citas explícitas (`archivo`, `ubicacion`, `fragmento`) + `faltantes_detectados`.
   - `cuantificacion_por_criterio`: nivel y puntaje por `criterion_id` con evidencias (el backend verifica rangos y calcula la nota final).
   - `recomendaciones`: `fortalezas`, `debilidades`, `mejoras_tecnicas`, `mejoras_conceptuales`, `mejoras_metodologicas`.
3. **Esquema compatible con Gemini:** Enviar un JSON Schema plano sin `minimum`/`maximum` al proveedor; validar rangos, IDs de criterios y nombres reales de archivo en Pydantic después de recibir la respuesta.
4. **No alucinación:** Si un archivo no pudo extraerse (ej. video o binario), informarlo en el contexto al modelo y prohibir inventar citas o métricas.
