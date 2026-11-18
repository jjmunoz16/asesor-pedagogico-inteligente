"""Generador puro en Python de documentos PDF 1.4 multipágina con soporte español (WinAnsi)."""

import textwrap
from typing import Any


_CHAR_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "•": "*",
    "…": "...",
    "→": "->",
    "≥": ">=",
    "≤": "<=",
}


def _to_pdf_bytes(text: str) -> bytes:
    cleaned = text or ""
    for src, dst in _CHAR_REPLACEMENTS.items():
        cleaned = cleaned.replace(src, dst)
    encoded = cleaned.encode("cp1252", errors="replace")
    # Escapar caracteres especiales de literal string en PDF: \ ( )
    out = bytearray()
    for b in encoded:
        if b in (0x5C, 0x28, 0x29):
            out.append(0x5C)
        out.append(b)
    return bytes(out)


class _SimplePDFBuilder:
    """Constructor minimalista de PDF multipágina (A4/Letter 612x792 pt)."""

    PAGE_W = 612
    PAGE_H = 792
    MARGIN_X = 50
    TOP_Y = 740
    BOTTOM_Y = 56
    MAX_CHARS = 88

    def __init__(self, doc_title: str) -> None:
        self.doc_title = doc_title
        self.pages: list[list[bytes]] = []
        self.y = self.TOP_Y
        self._new_page()

    def _new_page(self) -> None:
        self.pages.append([])
        self.y = self.TOP_Y
        # Encabezado superior sutil
        header = _to_pdf_bytes(f"Asesor Pedagogico Inteligente | {self.doc_title[:68]}")
        self.pages[-1].append(
            b"BT /F2 8 Tf 0.42 0.45 0.52 rg 50 765 Td (" + header + b") Tj ET"
        )
        self.pages[-1].append(b"0.85 0.87 0.91 RG 0.6 w 50 757 m 562 757 l S")

    def _ensure_space(self, height: float) -> None:
        if self.y - height < self.BOTTOM_Y:
            self._new_page()

    def add_title(self, text: str) -> None:
        for line in textwrap.wrap(text, width=64) or [""]:
            self._ensure_space(20)
            self.pages[-1].append(
                b"BT /F1 15 Tf 0.12 0.16 0.28 rg "
                + f"{self.MARGIN_X} {self.y:.1f} Td (".encode("ascii")
                + _to_pdf_bytes(line)
                + b") Tj ET"
            )
            self.y -= 19
        self.y -= 4

    def add_heading(self, text: str) -> None:
        self.y -= 6
        self._ensure_space(22)
        self.pages[-1].append(
            b"BT /F1 11 Tf 0.22 0.25 0.62 rg "
            + f"{self.MARGIN_X} {self.y:.1f} Td (".encode("ascii")
            + _to_pdf_bytes(text)
            + b") Tj ET"
        )
        self.y -= 15

    def add_line(self, text: str, bold: bool = False, indent: int = 0) -> None:
        font = b"/F1" if bold else b"/F2"
        width = max(40, self.MAX_CHARS - indent // 4)
        wrapped = textwrap.wrap(text, width=width) or [""]
        for idx, line in enumerate(wrapped):
            self._ensure_space(13)
            x = self.MARGIN_X + indent + (8 if idx > 0 and text.lstrip().startswith("-") else 0)
            self.pages[-1].append(
                b"BT "
                + font
                + b" 9.5 Tf 0.15 0.18 0.24 rg "
                + f"{x} {self.y:.1f} Td (".encode("ascii")
                + _to_pdf_bytes(line)
                + b") Tj ET"
            )
            self.y -= 13

    def build(self) -> bytes:
        # Agregar pie de página con número de página
        total_pages = len(self.pages)
        for idx, cmds in enumerate(self.pages, start=1):
            footer = _to_pdf_bytes(
                f"Universidad de Manizales - Profundizacion I (IA) | Pagina {idx} de {total_pages}"
            )
            cmds.append(b"0.85 0.87 0.91 RG 0.5 w 50 42 m 562 42 l S")
            cmds.append(b"BT /F2 8 Tf 0.45 0.48 0.55 rg 50 28 Td (" + footer + b") Tj ET")

        objects: list[bytes] = []
        # 1: Catalog, 2: Pages, 3: Font Bold, 4: Font Regular
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        page_obj_nums: list[int] = []
        content_streams = [b"\n".join(cmds) for cmds in self.pages]

        # Pre-calcular IDs: páginas y contenidos empiezan en objeto 5
        next_id = 5
        page_ids = []
        content_ids = []
        for _ in content_streams:
            page_ids.append(next_id)
            content_ids.append(next_id + 1)
            next_id += 2

        kids_str = " ".join(f"{pid} 0 R" for pid in page_ids).encode("ascii")
        objects.append(b"<< /Type /Pages /Kids [ " + kids_str + b" ] /Count " + str(len(page_ids)).encode("ascii") + b" >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")

        for pid, cid, stream in zip(page_ids, content_ids, content_streams):
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.PAGE_W} {self.PAGE_H}] "
                f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {cid} 0 R >>"
            ).encode("ascii")
            objects.append(page_dict)
            content_obj = (
                f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
                + stream
                + b"\nendstream"
            )
            objects.append(content_obj)

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: list[int] = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{idx} 0 obj\n".encode("ascii"))
            out.extend(obj)
            out.extend(b"\nendobj\n")

        xref_pos = len(out)
        out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

        out.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_pos}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(out)


def render_individual_report_pdf(report: dict[str, Any]) -> bytes:
    """Genera un PDF real descargable para un informe individual de evaluación."""
    act = report["activity"]
    ver = report["dimension_verificacion"]
    quant = report["dimension_cuantificacion"]
    rec = report["dimension_recomendacion"]
    tr = report["traceability"]
    sb = report["verificacion_tecnica_sandbox"]

    pdf = _SimplePDFBuilder(f"Informe Evaluacion #{report['evaluation_id']}")
    pdf.add_title(f"Informe Individual - {act['title']}")
    pdf.add_line(f"Cohorte: {act['cohort']} | Grupo: {report['submission']['student_group_name']}", bold=True)
    pdf.add_line(
        f"Nota Final (calculo determinista backend 0.0-5.0): {quant['effective_final_score']:.2f} / 5.00 | Estado: {report['status']}",
        bold=True,
    )
    pdf.add_line(
        f"Rubrica: {tr['rubric_name']} (v{tr['rubric_version']}) | Motor IA: {tr['ai_provider']} / {tr['ai_model']}"
    )

    pdf.add_heading("1. VERIFICACION (Cumplimiento de Objetivo)")
    pdf.add_line(f"Objetivo planteado: {act['official_objective'] or 'No consta objetivo explicito.'}")
    pdf.add_line(f"Estado de cumplimiento: {ver['objetivo_cumplido']}", bold=True)
    pdf.add_line(f"Resumen: {ver['resumen_verificacion']}")
    if ver["evidencias_citadas"]:
        pdf.add_line("Evidencias citadas:", bold=True)
        for ev in ver["evidencias_citadas"]:
            pdf.add_line(f"- [{ev['archivo']} | {ev['ubicacion']}]: {ev['fragmento']}", indent=8)
    if ver["faltantes_detectados"]:
        pdf.add_line("Faltantes detectados:", bold=True)
        for f in ver["faltantes_detectados"]:
            pdf.add_line(f"- {f}", indent=8)

    pdf.add_heading("2. VERIFICACION TECNICA OBJETIVA (SANDBOX)")
    pdf.add_line(
        f"Ejecutado: {'Si' if sb['executed'] else 'No'} | Modo: {sb.get('sandbox_mode') or 'N/A'} | "
        f"Sintaxis valida: {sb.get('syntax_valid')}"
    )
    for finding in sb.get("static_findings") or []:
        pdf.add_line(f"- {finding}", indent=8)

    pdf.add_heading("3. CUANTIFICACION POR CRITERIO (RUBRICA 100%)")
    for c in quant["criteria"]:
        pdf.add_line(
            f"- {c['criterion_name']} ({c['weight_percent']} %): {c['effective_score']:.2f}/5.00 ({c['ai_level_label']})",
            bold=True,
        )
        pdf.add_line(c["justification"], indent=10)

    pdf.add_heading("4. RECOMENDACIONES DE MEJORA")
    for key, label in [
        ("fortalezas", "Fortalezas"),
        ("debilidades", "Debilidades"),
        ("mejoras_tecnicas", "Mejoras Tecnicas"),
        ("mejoras_conceptuales", "Mejoras Conceptuales"),
        ("mejoras_metodologicas", "Mejoras Metodologicas"),
    ]:
        items = rec.get(key, [])
        if items:
            pdf.add_line(f"{label}:", bold=True)
            for item in items:
                pdf.add_line(f"- {item}", indent=8)

    if report.get("teacher_reviews"):
        pdf.add_heading("5. REVISION Y APROBACION DOCENTE (HITL)")
        for rev in report["teacher_reviews"]:
            pdf.add_line(f"- Decision: {rev['decision']} | Fecha: {rev['reviewed_at']}", bold=True)
            if rev.get("comments"):
                pdf.add_line(f"Comentarios: {rev['comments']}", indent=8)

    return pdf.build()


def render_integrated_report_pdf(integrated: dict[str, Any]) -> bytes:
    """Genera un PDF real descargable para el Informe Integral del Aprendizaje."""
    pdf = _SimplePDFBuilder("Informe Integral del Aprendizaje")
    pdf.add_title("Informe Integral del Aprendizaje (Cohortes 1 y 2)")
    avg = integrated.get("global_average")
    avg_txt = f"{avg:.2f} / 5.00" if avg is not None else "Sin calificar"
    pdf.add_line(
        f"Promedio Global: {avg_txt} | Actividades evaluadas: {integrated['evaluated_activities']} de {integrated['total_activities']}",
        bold=True,
    )

    pdf.add_heading("1. EVOLUCION ENTRE COHORTES")
    for ce in integrated.get("cohort_evolution", []):
        cavg = f"{ce['average_score']:.2f}/5.00" if ce["average_score"] is not None else "Sin evaluar"
        pdf.add_line(
            f"- {ce['cohort_name']} ({ce['cohort_code']}): {cavg} ({ce['activities_evaluated']} actividades evaluadas)"
        )

    pdf.add_heading("2. DESEMPENO POR ACTIVIDAD")
    for act in integrated.get("activities", []):
        sc = f"{act['score']:.2f}/5.00" if act["score"] is not None else "Sin evaluar"
        pdf.add_line(
            f"- [{act['cohort_code']}] {act['title']} -> Nota: {sc} | Estado: {act['status']}"
        )

    pdf.add_heading("3. COMPETENCIAS Y NIVELES DE DOMINIO")
    for comp in integrated.get("competencies", []):
        pdf.add_line(
            f"- {comp['competency']}: {comp['average_score']:.2f}/5.00 ({comp['mastery_level']})"
        )

    pdf.add_heading("4. BRECHAS IDENTIFICADAS")
    for gap in integrated.get("identified_gaps", []) or ["Sin brechas criticas registradas."]:
        pdf.add_line(f"- {gap}", indent=6)

    pdf.add_heading("5. PLAN PERSONALIZADO DE FORTALECIMIENTO")
    for act in integrated.get("strengthening_plan", []) or ["Sin acciones pendientes registradas."]:
        pdf.add_line(f"- {act}", indent=6)

    return pdf.build()
