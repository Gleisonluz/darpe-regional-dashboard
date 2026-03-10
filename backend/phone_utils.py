import re

def normalize_phone(phone: str) -> str:
    """
    Normaliza números de telefone para o formato padrão +5547999990001
    
    Aceita formatos:
    - +55 47 99999-0001
    - +5547999990001
    - (47)99999-0001
    - 47999990001
    - 47 99999-0001
    
    Retorna: +5547999990001
    """
    if not phone:
        return phone
    
    # Remove todos os caracteres não numéricos exceto o + inicial
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Se não começar com +, adicionar código do país
    if not cleaned.startswith('+'):
        # Se começar com 55, adicionar apenas o +
        if cleaned.startswith('55'):
            cleaned = '+' + cleaned
        # Se não, adicionar +55
        else:
            cleaned = '+55' + cleaned
    
    return cleaned
