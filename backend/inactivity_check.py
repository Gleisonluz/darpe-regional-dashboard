from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.models import UserStatus
async def check_and_update_inactive_users(db: AsyncIOMotorDatabase):
    """
    Verifica usuários inativos (mais de 90 dias sem registrar presença)
    e atualiza o status para BLOQUEADO_INATIVIDADE
    
    IMPORTANTE: Administradores (Secretário Regional e Ancião Coordenador) 
    nunca são bloqueados por inatividade
    """
    threshold_date = datetime.now(timezone.utc) - timedelta(days=90)
    
    # Buscar usuários ativos que não registraram presença há mais de 90 dias
    # EXCLUINDO administradores (Secretário Regional e Ancião Coordenador)
    users = await db.users.find({
        "status": UserStatus.ATIVO.value,
        "funcoes_darpe": {
            "$nin": ["Secretário Regional", "Ancião Coordenador"]
        },  # Excluir admins
        "$or": [
            {"ultimo_atendimento": {"$lt": threshold_date.isoformat()}},
            {"ultimo_atendimento": None}
        ]
    }).to_list(None)
    
    blocked_users = []
    
    for user in users:
        # Atualizar status
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"status": UserStatus.BLOQUEADO_INATIVIDADE.value}}
        )
        
        # Criar notificação
        notification = {
            "id": f"notif_{user['id']}_{datetime.now(timezone.utc).timestamp()}",
            "user_id": user["id"],
            "titulo": "Conta Bloqueada por Inatividade",
            "mensagem": "Sua conta foi bloqueada automaticamente devido a mais de 90 dias sem registro de presença. Entre em contato com o Secretário Regional ou Ancião Coordenador para reativação.",
            "tipo": "warning",
            "lida": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)
        
        blocked_users.append(user["id"])
    
    return blocked_users
