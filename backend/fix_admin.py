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
    
    # Buscar e atualizar a conta admin
    admin_email = "admin@darpe.org"
    
    result = await db.users.update_one(
        {"email": admin_email},
        {
            "$set": {
                "status": "ativo",
                "ultimo_atendimento": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ Conta {admin_email} reativada e desbloqueada com sucesso!")
    else:
        print(f"ℹ️  Conta {admin_email} já estava ativa")
    
    # Verificar o status atual
    admin = await db.users.find_one({"email": admin_email}, {"_id": 0, "email": 1, "nome_completo": 1, "status": 1, "role": 1})
    
    if admin:
        print(f"\n📋 Status da conta:")
        print(f"   Email: {admin['email']}")
        print(f"   Nome: {admin['nome_completo']}")
        print(f"   Role: {admin['role']}")
        print(f"   Status: {admin['status']}")
        
        if admin['status'] == 'ativo':
            print(f"\n✨ Conta administrativa está ativa e pronta para aprovar usuários!")
        else:
            print(f"\n⚠️  ATENÇÃO: Conta ainda está com status: {admin['status']}")
    else:
        print(f"\n❌ Conta {admin_email} não encontrada no banco de dados")
    
    # Listar usuários pendentes
    pending_users = await db.users.find({"status": "pendente"}, {"_id": 0, "email": 1, "nome_completo": 1}).to_list(None)
    
    if pending_users:
        print(f"\n👥 Usuários pendentes de aprovação ({len(pending_users)}):")
        for user in pending_users:
            print(f"   - {user['nome_completo']} ({user['email']})")
    else:
        print(f"\n✓ Nenhum usuário pendente de aprovação")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_account())
