import re
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from app.core.state import EDAState


def build_pdf_report(state: EDAState) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    font_name = "Helvetica"
    font_size = 12
    line_height_cm = 0.7
    left_margin = 2 * cm
    right_margin = 2 * cm
    page_width, _ = A4
    max_width = page_width - left_margin - right_margin

    pdf.setFont(font_name, font_size)
    y = 28 * cm

    # Placeholder hook for future conditional report content.
    include_execution_order = state.show_execution_order

    def sanitize(text: str) -> str:
        return re.sub(r"\s*\(llm_error=[^)]*\)", "", text or "")

    def wrap_text(text: str) -> list[str]:
        if not text:
            return [""]

        words = text.split(" ")
        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if stringWidth(candidate, font_name, font_size) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                    current = word
                else:
                    token = word
                    chunk = ""
                    for ch in token:
                        next_chunk = f"{chunk}{ch}"
                        if stringWidth(next_chunk, font_name, font_size) <= max_width:
                            chunk = next_chunk
                        else:
                            lines.append(chunk)
                            chunk = ch
                    current = chunk

        if current:
            lines.append(current)
        return lines

    def write(line: str, step: float = line_height_cm) -> None:
        nonlocal y
        for wrapped in wrap_text(line):
            if y < 2 * cm:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = 28 * cm
            pdf.drawString(left_margin, y, wrapped)
            y -= step * cm

    write("Multi-Agent Statistical EDA Report", step=1.0)
    write(f"Dataset: {state.dataset_name}")
    write(f"Rows: {state.data_profile['shape']['rows']}  Cols: {state.data_profile['shape']['columns']}")
    write(" ")

    write("Cleaning Plan", step=0.8)
    plan = state.cleaning_plan
    if plan:
        write(f"fill_missing: {plan.fill_missing}")
        write(f"remove_outliers: {plan.remove_outliers}")
        write(f"outlier_columns: {', '.join(plan.outlier_columns) if plan.outlier_columns else 'None'}")
        write(f"type_conversions: {', '.join([f'{x.column}->{x.target_dtype}' for x in plan.type_conversions]) or 'None'}")
    write(" ")

    write("Insight Ledger", step=0.8)
    for idx, insight in enumerate(state.insight_ledger, start=1):
        write(f"{idx}. {insight.skeptic.verdict.value}: {sanitize(insight.hypothesis)}")
        write(f"Function: {insight.function_name}")
        stats = ", ".join(
            f"{key}={value}"
            for key, value in insight.result.statistics.items()
            if key in {"statistic", "p_value", "n", "r_squared", "cohen_d", "cramers_v"}
        )
        if stats:
            write(f"Stats: {stats}")
        write(f"Skeptic: {sanitize(insight.skeptic.reason)}")
        write(f"Narrative: {sanitize(insight.narrative)}")

    if include_execution_order:
        # Intentionally no PDF changes yet; this branch confirms flag plumbing.
        pass

    pdf.save()
    buffer.seek(0)
    return buffer.read()
