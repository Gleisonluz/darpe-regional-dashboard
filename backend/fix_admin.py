import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

# Carregar variáveis de ambiente
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

print("MONGO_URL:", os.getenv("MONGO_URL"))
print("DB_NAME:", os.getenv("DB_NAME"))

async def fix_admin_account():

    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]

    print("🔧 Promovendo usuário a ADMIN...")

    whatsapp = "41995660981"

    # USERS
    result_users = await db.users.update_one(
        {"whatsapp": whatsapp},
        {
            "$set": {
                "nome_completo": "Gleison Luz",
                "status": "ATIVO",
                "funcoes_darpe": ["Secretário Regional"],
                "ultimo_atendimento": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )

    # COLABORADORES
    result_colab = await db.colaboradores.update_one(
        {"whatsapp": whatsapp},
        {
            "$set": {
                "nome_completo": "Gleison Luz",
                "status": "ATIVO",
                "cargo_base": "Atendente",
                "cargos_ministerio": ["Secretário Regional"],
                "comum_congregacao": "Bairro dos Municípios - Balneário Camboriú - SC",
                "ultimo_atendimento": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )

    print("✅ USERS atualizado:", result_users.modified_count)
    print("✅ COLABORADORES atualizado:", result_colab.modified_count)

    # Verificar o status atual
    admin = await db.users.find_one(
        {"whatsapp": whatsapp},
        {"_id": 0, "whatsapp": 1, "nome_completo": 1, "status": 1, "funcoes_darpe": 1}
    )

    if admin:
        print(f"\n📋 Status da conta:")
        print(f"   WhatsApp: {admin['whatsapp']}")
        print(f"   Nome: {admin['nome_completo']}")
        print(f"   Funções: {admin.get('funcoes_darpe', [])}")
        print(f"   Status: {admin['status']}")

        if admin['status'] == 'ATIVO':
            print(f"\n✨ Conta administrativa está ativa e pronta para aprovar usuários!")
        else:
            print(f"\n⚠️  ATENÇÃO: Conta ainda está com status: {admin['status']}")
    else:
        print(f"\n❌ Conta {whatsapp} não encontrada no banco de dados")

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