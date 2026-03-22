from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path

router = APIRouter()

PDF_DIR = Path("reports")
PDF_DIR.mkdir(exist_ok=True)

@router.get("/mission-reports/regional-summary/pdf")
def generate_regional_summary_pdf():

    file_path = PDF_DIR / "relatorio_regional.pdf"

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    margin_x = 2.2 * cm

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(
        width / 2,
        height - 2.5 * cm,
        "RELATÓRIO GERAL DAS REUNIÕES DE EVANGELIZAÇÃO"
    )

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(
        width / 2,
        height - 3.2 * cm,
        "DARPE – REGIONAL ITAJAÍ – SC"
    )

    pdf.setStrokeColor(colors.HexColor("#94A3B8"))
    pdf.line(margin_x, height - 3.6 * cm, width - margin_x, height - 3.6 * cm)

    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        width / 2,
        1.5 * cm,
        f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    pdf.save()

    return FileResponse(
        path=str(file_path),
        filename="relatorio_regional.pdf",
        media_type="application/pdf"
    )
