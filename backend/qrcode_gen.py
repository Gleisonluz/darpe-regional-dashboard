import qrcode
import io
import base64
from typing import Dict

def generate_qr_code(data: Dict) -> str:
    """
    Gera um QR code como string base64
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    
    # Criar string com dados do usuário
    qr_data = f"DARPE-ITJ|{data.get('id')}|{data.get('nome_completo')}|{data.get('status')}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
