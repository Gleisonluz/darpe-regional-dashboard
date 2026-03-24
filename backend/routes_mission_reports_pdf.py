from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from pathlib import Path
from textwrap import wrap
from datetime import datetime

from backend.routes_mission_reports import mission_reports_db
router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "uploads" / "reports"
PDF_DIR.mkdir(parents=True, exist_ok=True)

LOGO_PATH = BASE_DIR / "assets" / "Logo_oficial_CCB.png"

# Paleta CCB
CCB_AZUL_ESCURO = colors.HexColor("#0F2A52")
CCB_AZUL_MEDIO  = colors.HexColor("#1B3A6B")
CCB_CINZA_HEADER= colors.HexColor("#F0F2F5")
CCB_CINZA_FUNDO = colors.HexColor("#E8ECF0")
CCB_CINZA_LINHA = colors.HexColor("#B0BCCF")
CCB_TEXTO       = colors.HexColor("#1A1A2E")
CCB_TEXTO_CLARO = colors.HexColor("#4A5568")


def draw_wrapped_text(pdf, text, x, y, max_chars=70, line_height=15):
    content = str(text).strip() if text is not None else ""
    if not content:
        content = "-"
    lines = wrap(content, width=max_chars)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_height
    return y


def draw_label_value(pdf, label, value, left_x, value_x, y):
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(CCB_AZUL_MEDIO)
    pdf.drawString(left_x, y, label)
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(CCB_TEXTO)
    return draw_wrapped_text(pdf, value, value_x, y, max_chars=55, line_height=16)


@router.get("/mission-reports/{report_id}/pdf")
def generate_mission_report_pdf(report_id: str):
    report = next((item for item in mission_reports_db if item["id"] == report_id), None)

    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")

    file_path = PDF_DIR / f"mission_report_{report_id}.pdf"
    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    margin_x = 2.2 * cm

    # Fundo do cabeçalho cinza claro
    header_height = 5.2 * cm
    pdf.setFillColor(CCB_CINZA_HEADER)
    pdf.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

    # Faixa azul escura no topo
    pdf.setFillColor(CCB_AZUL_ESCURO)
    pdf.rect(0, height - 0.5 * cm, width, 0.5 * cm, fill=1, stroke=0)

    # Faixa azul escura na base do cabeçalho
    pdf.setFillColor(CCB_AZUL_ESCURO)
    pdf.rect(0, height - header_height, width, 0.35 * cm, fill=1, stroke=0)

    # Logo centralizada (acima do título, sem fundo branco)
    if LOGO_PATH.exists():
        try:
            logo_w = 3.5 * cm
            logo_h = 1.8 * cm
            logo_x = (width - logo_w) / 2
            logo_y = height - 2.8 * cm
            pdf.drawImage(
                str(LOGO_PATH),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    # Título principal (abaixo da logo)
    pdf.setFillColor(CCB_AZUL_ESCURO)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 3.3 * cm, "DARPE – REGIONAL ITAJAÍ")

    # Subtítulo
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(CCB_TEXTO_CLARO)
    pdf.drawCentredString(width / 2, height - 3.95 * cm, "Departamento de Assistência Religiosa Para Evangelização")

    # ID discreto
    pdf.setFont("Helvetica", 7.5)
    pdf.setFillColor(CCB_CINZA_LINHA)
    pdf.drawCentredString(width / 2, height - 4.55 * cm, f"ID: {report.get('id', '-')}")

    # Título do relatório
    pdf.setFillColor(CCB_TEXTO)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(width / 2, height - 6.2 * cm, "RELATÓRIO DAS REUNIÕES DE EVANGELIZAÇÃO")

    # Linha divisória azul
    pdf.setStrokeColor(CCB_AZUL_MEDIO)
    pdf.setLineWidth(0.06 * cm)
    pdf.line(margin_x, height - 6.6 * cm, width - margin_x, height - 6.6 * cm)

    # Corpo
    y = height - 8.0 * cm
    left_x = margin_x
    value_x = margin_x + 5.5 * cm

    hinos = report.get("hinos", [])
    hinos_texto = ", ".join(str(h) for h in hinos) if hinos else "-"

    campos = [
        ("Cidade:",                   report.get("cidade", "-")),
        ("Local:",                    report.get("nome_local", "-")),
        ("Data do Serviço:",          report.get("data_servico", "-")),
        ("Atendente:",                report.get("atendente", "-")),
        ("Leitura da Palavra:",       report.get("leitura_palavra", "-")),
        ("Hinos:",                    hinos_texto),
        ("Horário de Início:",        report.get("hora_inicio", "-")),
        ("Horário de Término:",       report.get("hora_fim", "-")),
        ("Evangelizados Presentes:",  str(report.get("evangelizados_presentes", "-"))),
        ("Colaboradores Presentes:",  str(report.get("colaboradores_presentes", "-"))),
    ]

    # Caixa de fundo
    box_height = 12.5 * cm
    pdf.setStrokeColor(CCB_CINZA_LINHA)
    pdf.setFillColor(CCB_CINZA_FUNDO)
    pdf.roundRect(
        margin_x - 0.3 * cm,
        y - box_height + 0.4 * cm,
        width - (margin_x * 2) + 0.6 * cm,
        box_height,
        0.25 * cm,
        fill=1, stroke=1
    )

    for label, value in campos:
        y = draw_label_value(pdf, label, value, left_x, value_x, y)
        y -= 0.35 * cm

    # Observações
    y -= 0.3 * cm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(CCB_AZUL_MEDIO)
    pdf.drawString(left_x, y, "Observações:")
    y -= 0.7 * cm

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(CCB_TEXTO)
    y = draw_wrapped_text(pdf, report.get("observacoes", "-"), left_x, y, max_chars=95, line_height=16)

    # Rodapé
    pdf.setStrokeColor(CCB_AZUL_ESCURO)
    pdf.setLineWidth(0.05 * cm)
    pdf.line(margin_x, 2.8 * cm, width - margin_x, 2.8 * cm)

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(CCB_AZUL_MEDIO)
    pdf.drawString(margin_x, 2.2 * cm, "DARPE – REGIONAL ITAJAÍ – SC")
    pdf.drawRightString(width - margin_x, 2.2 * cm, "Congregação Cristã no Brasil")

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(CCB_TEXTO_CLARO)
    pdf.drawCentredString(width / 2, 1.5 * cm, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    pdf.save()

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/pdf"
    )
