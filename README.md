# Asesor Pedagógico Inteligente

## 1. Descripción del proyecto

El **Asesor Pedagógico Inteligente** es un proyecto académico desarrollado en el marco de la asignatura **Profundización I – Inteligencia Artificial**, de Ingeniería de Sistemas y Telecomunicaciones.

Su propósito es desarrollar una plataforma que utilice técnicas de inteligencia artificial para analizar trabajos académicos a partir de sus objetivos, rúbricas de evaluación y evidencias entregadas por los estudiantes.

La plataforma busca proporcionar una evaluación estructurada, explicable y acompañada de recomendaciones que permitan identificar fortalezas, oportunidades de mejora y cumplimiento de los objetivos de aprendizaje.

## 2. Objetivo general

Diseñar y desarrollar una solución inteligente que permita analizar actividades académicas, verificar el cumplimiento de sus objetivos, cuantificar sus resultados mediante criterios de evaluación y generar recomendaciones pedagógicas fundamentadas en las evidencias entregadas.

## 3. Funcionalidades principales previstas

La plataforma contempla dos funcionalidades centrales:

### 3.1. Evaluación y retroalimentación académica

- Registro de actividades académicas.
- Carga del objetivo de cada actividad.
- Incorporación de rúbricas de evaluación.
- Carga de trabajos y evidencias.
- Verificación del cumplimiento de los objetivos.
- Evaluación cuantitativa y cualitativa según la rúbrica.
- Generación de recomendaciones de mejora.
- Elaboración de informes individuales de retroalimentación.

### 3.2. Generación de infografía académica

- Identificación de las temáticas presentes en las actividades.
- Organización de los conocimientos abordados.
- Visualización de las relaciones entre temáticas y competencias.
- Generación de una representación visual del aprendizaje construido a partir de las actividades analizadas.

Las funcionalidades definitivas se ajustarán a los requerimientos del documento oficial del profesor.

## 4. Método de evaluación

El análisis académico se organiza alrededor de tres dimensiones:

| Dimensión | Descripción |
|---|---|
| Verificación | Determinar si el trabajo cumple con el objetivo planteado. |
| Cuantificación | Valorar el trabajo utilizando los criterios y ponderaciones de la rúbrica. |
| Recomendación | Proponer mejoras específicas y justificadas. |

Los resultados deben estar respaldados por evidencias verificables. La inteligencia artificial no debe inventar criterios, resultados ni información que no esté presente en los documentos.

## 5. Organización académica

El proyecto contempla seis actividades académicas distribuidas de la siguiente manera:

**Primer corte**
- Laboratorio 1.
- Laboratorio 2.
- Laboratorio 3.
- Primer parcial.

**Segundo corte**
- Laboratorio 4.
- Laboratorio 5.

La identificación y clasificación definitiva de las actividades se realizará a partir de los documentos originales y las instrucciones del profesor.

## 6. Tecnologías

La selección definitiva de tecnologías, frameworks, modelos de inteligencia artificial y herramientas de almacenamiento se realizará durante la fase de arquitectura.

No se considerará ninguna tecnología como decisión definitiva hasta que sea evaluada y aprobada.

## 7. Estructura del proyecto

```text
ProyectoFinalPI/
│
├── .agents/
│   ├── agents/
│   ├── rules/
│   └── skills/
│
├── ai-documentation/
│
├── backend/
│
├── docs/
│   ├── analisis-documento/
│   ├── arquitectura/
│   ├── decisiones-tecnicas/
│   ├── diseno/
│   └── especificaciones/
│
├── frontend/
│
├── source-material/
│   ├── primer-corte/
│   └── segundo-corte/
│
├── tests/
│
├── AGENTS.md
└── README.md
```

## 8. Metodología de desarrollo

El proyecto se desarrollará por fases:

1. Preparación del entorno y organización documental.
2. Análisis de los requerimientos académicos.
3. Definición de requisitos funcionales y no funcionales.
4. Diseño de arquitectura y modelo de datos.
5. Diseño de experiencia de usuario e interfaces.
6. Desarrollo del backend y frontend.
7. Integración de los componentes de inteligencia artificial.
8. Pruebas, validación y auditoría.
9. Documentación y presentación final.

El avance entre fases dependerá de la validación de los entregables de cada etapa.

## 9. Uso de inteligencia artificial

Se utilizarán herramientas y agentes de inteligencia artificial como apoyo para el análisis documental, diseño, desarrollo, revisión y pruebas.

Cada agente tendrá responsabilidades delimitadas. Sus resultados deberán ser revisados y validados antes de incorporarse como decisiones o componentes definitivos del proyecto.

## 10. Principios de calidad y seguridad

- Respetar los requerimientos oficiales del profesor.
- Garantizar trazabilidad entre evaluaciones y evidencias.
- Evitar resultados o referencias académicas inventadas.
- Aplicar los criterios de las rúbricas de manera consistente.
- Separar las conclusiones verificables de las recomendaciones generadas por IA.
- Permitir revisión humana de los resultados.
- Proteger los documentos y datos académicos.
- No exponer credenciales ni claves de servicios externos.

## 11. Estado actual

**Fase actual:** preparación y reconocimiento del entorno de desarrollo.

El proyecto se encuentra en etapa de organización documental y definición de requisitos. Todavía no se ha iniciado la implementación funcional de la plataforma.

## 12. Documento de referencia

El documento oficial proporcionado por el profesor constituye la fuente principal de requisitos y orientaciones académicas del proyecto. Las decisiones de diseño y desarrollo deberán ser coherentes con dicho documento.