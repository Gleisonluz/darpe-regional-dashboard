import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone
from passlib.context import CryptContext

# Carregar variáveis de ambiente
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    # Conectar ao MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🌱 Iniciando seed do banco de dados...")
    
    # Criar usuário admin
    admin_password = pwd_context.hash("admin123")
    admin_user = {
        "id": "admin-001",
        "whatsapp": "+5547999990001",  # Formato normalizado
        "senha": admin_password,
        "nome_completo": "Administrador DARPE",
        "funcoes_darpe": ["Secretário Regional"],
        "status": "ativo",
        "cidade": "Itajaí",
        "localidade": "DARPE Regional Itajaí",
        "unidades": [],
        "ultimo_atendimento": datetime.now(timezone.utc).isoformat(),
        "foto_url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Verificar se admin já existe
    existing_admin = await db.users.find_one({"whatsapp": admin_user["whatsapp"]})
    if not existing_admin:
        await db.users.insert_one(admin_user)
        print("✅ Usuário admin criado: +5547999990001 / admin123")
    else:
        # Atualizar para garantir que está ativo
        await db.users.update_one(
            {"whatsapp": admin_user["whatsapp"]},
            {"$set": {
                "status": "ativo",
                "funcoes_darpe": ["Secretário Regional"],
                "ultimo_atendimento": datetime.now(timezone.utc).isoformat()
            }}
        )
        print("ℹ️  Usuário admin já existe - status atualizado para ativo")
    
    # Limpar unidades fictícias antigas
    await db.units.delete_many({})
    print("✅ Unidades fictícias removidas - sistema pronto para dados reais")
    
    print("\n✨ Seed concluído com sucesso!")
    print("\n📝 Credenciais de acesso:")
    print("   WhatsApp: +5547999990001 (aceita também: +55 47 99999-0001, (47)99999-0001, etc.)")
    print("   Senha: admin123")
    print("   Funções: Secretário Regional (acesso total)")
    print("\n⚠️  Sistema limpo - adicione unidades reais do DARPE pela interface administrativa\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
