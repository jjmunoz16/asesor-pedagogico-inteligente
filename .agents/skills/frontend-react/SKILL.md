---
name: frontend-react
description: >-
  Convenciones para el frontend en React + TypeScript + Vite + Tailwind CSS + @xyflow/react del proyecto Asesor Pedagógico Inteligente.
---

# Frontend React — Asesor Pedagógico Inteligente

1. **Alineación UX/UI:** Seguir exactamente las 8 vistas y flujos definidos en `docs/diseno/DISENO_UX_UI.md`.
2. **Separación visual obligatoria:** Distinguir claramente con badges/estilos entre `Evidencia verificada` (citas de archivos), `Borrador IA` (modelo usado) y `Aprobada por Docente` (HITL), además de mostrar el aviso explícito cuando falten datos en las evidencias.
3. **Mapa mental interactivo:** Usar `@xyflow/react` con filtros por cohorte y nivel de dominio, panel lateral de evidencias reales y exportación SVG/PNG/JSON.
4. **Impresión PDF limpia:** Mantener estilos `@media print` para el Informe Individual y el Informe Integral sin menús laterales ni ruido visual.
5. **Seguridad:** No almacenar claves de proveedores IA en el frontend ni en `localStorage`.
