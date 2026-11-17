# AGENTS.md — Asesor Pedagógico Inteligente

## 1. Identidad del proyecto

Estamos desarrollando una plataforma web denominada Asesor Pedagógico Inteligente para el proyecto final de Profundización I - Inteligencia Artificial de Ingeniería de Sistemas y Telecomunicaciones de la Universidad de Manizales.

El documento oficial del profesor es la fuente principal de requisitos y debe respetarse durante todo el desarrollo.

## 2. Objetivo

Construir una aplicación web funcional que permita cargar trabajos académicos, analizar sus evidencias mediante inteligencia artificial, evaluar el cumplimiento de objetivos, aplicar rúbricas de valoración y generar retroalimentaciones individuales.

La plataforma debe producir dos resultados principales:

1. Informes individuales de retroalimentación por cada actividad académica.
2. Una infografía global e interactiva que represente las temáticas y competencias desarrolladas durante los trabajos de la materia.

## 3. Método de evaluación obligatorio

Todas las evaluaciones deben contemplar tres dimensiones:

- VERIFICACIÓN: determinar si el trabajo cumplió el objetivo planteado, utilizando evidencias concretas.
- CUANTIFICACIÓN: valorar el trabajo mediante los criterios y ponderaciones de la rúbrica, generando una calificación entre 0,0 y 5,0 y un concepto argumentado.
- RECOMENDACIÓN: identificar debilidades, oportunidades de mejora y recomendaciones técnicas, conceptuales y metodológicas.

## 4. Fuentes académicas

Los documentos originales están en:

`source-material/`

Actualmente se contemplan:

- Primer corte: tres laboratorios y un parcial.
- Segundo corte: dos laboratorios.

No confundir los cortes académicos con las cohortes 1 y 2 mencionadas en el documento del profesor.

Nunca inventar objetivos, criterios, ponderaciones, resultados, competencias ni evidencias.

Cuando falte información, se debe indicar expresamente.

Toda conclusión derivada de los trabajos académicos debe identificar su archivo de origen y, cuando sea posible, su página, sección o fragmento correspondiente.

## 5. Reglas de desarrollo

- No comenzar la programación sin aprobación de la arquitectura y los requisitos.
- No modificar documentos académicos originales.
- No sobrescribir archivos sin autorización.
- No inventar funcionalidades ni tecnologías como decisiones definitivas.
- Justificar las propuestas técnicas.
- Mantener una arquitectura coherente.
- Evitar duplicación de componentes y lógica.
- Aplicar buenas prácticas de seguridad, validación y mantenibilidad.
- Documentar decisiones importantes.
- Escribir código legible y verificable.
- Ejecutar pruebas antes de dar una funcionalidad por terminada.

## 6. Inteligencia artificial

La IA debe utilizarse durante el análisis, diseño, desarrollo, pruebas, documentación y despliegue.

Las respuestas del modelo de evaluación deben ser estructuradas y validadas.

El modelo de IA nunca debe calcular libremente la nota final. El backend debe realizar el cálculo a partir de los porcentajes de la rúbrica.

Toda evaluación debe conservar trazabilidad de las evidencias, versión de la rúbrica, modelo utilizado y resultados de las verificaciones.

## 7. Trabajo con agentes

Cada agente debe tener una responsabilidad delimitada.

Antes de comenzar una tarea debe:

1. Identificar los documentos y requisitos relacionados.
2. Comprender las dependencias.
3. Informar su plan de trabajo.
4. Separar hechos de recomendaciones.
5. Entregar resultados verificables.

Los agentes no deben tomar decisiones arquitectónicas definitivas sin aprobación del responsable del proyecto.

Cuando existan hallazgos contradictorios, deben reportarlos.

## 8. Seguridad

- No subir trabajos académicos privados a repositorios públicos.
- No exponer claves API, contraseñas ni credenciales.
- No ejecutar archivos de estudiantes directamente en el sistema principal.
- Toda ejecución de código de terceros deberá estar aislada y restringida.
- Solicitar autorización antes de realizar operaciones destructivas o modificar información original.

## 9. Documentación

Mantener actualizados los requisitos, arquitectura, decisiones técnicas, pruebas y registro de herramientas de IA utilizadas.

Toda funcionalidad implementada debe relacionarse con uno o más requisitos del documento oficial del profesor.

## 10. Restricción inicial

Durante la etapa inicial únicamente se autoriza analizar, organizar, documentar y proponer.

No se autoriza desarrollar código de la aplicación hasta que se aprueben los requisitos y la arquitectura.