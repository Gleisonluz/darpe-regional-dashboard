import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

# Carregar variáveis de ambiente
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

async def fix_admin_account():
    # Conectar ao MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔧 Corrigindo conta de administrador...")
    
    # Buscar e atualizar a conta admin pelo WhatsApp
    admin_whatsapp = "+5547999990001"
    
    result = await db.users.update_one(
        {"whatsapp": admin_whatsapp},
        {
            "$set": {
                "status": "ativo",
                "ultimo_atendimento": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ Conta {admin_whatsapp} reativada e desbloqueada com sucesso!")
    else:
        print(f"ℹ️  Conta {admin_whatsapp} já estava ativa")
    
    # Verificar o status atual
    admin = await db.users.find_one(
        {"whatsapp": admin_whatsapp}, 
        {"_id": 0, "whatsapp": 1, "nome_completo": 1, "status": 1, "funcoes_darpe": 1}
    )
    
    if admin:
        print(f"\n📋 Status da conta:")
        print(f"   WhatsApp: {admin['whatsapp']}")
        print(f"   Nome: {admin['nome_completo']}")
        print(f"   Funções: {admin.get('funcoes_darpe', [])}")
        print(f"   Status: {admin['status']}")
        
        if admin['status'] == 'ativo':
            print(f"\n✨ Conta administrativa está ativa e pronta para aprovar usuários!")
        else:
            print(f"\n⚠️  ATENÇÃO: Conta ainda está com status: {admin['status']}")
    else:
        print(f"\n❌ Conta {admin_whatsapp} não encontrada no banco de dados")
    
    # Listar usuários pendentes
    pending_users = await db.users.find(
        {"status": "pendente"}, 
        {"_id": 0, "whatsapp": 1, "nome_completo": 1}
    ).to_list(None)
    
    if pending_users:
        print(f"\n👥 Usuários pendentes de aprovação ({len(pending_users)}):")
        for user in pending_users:
            print(f"   - {user['nome_completo']} ({user.get('whatsapp', 'N/A')})")
    else:
        print(f"\n✓ Nenhum usuário pendente de aprovação")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_account())
