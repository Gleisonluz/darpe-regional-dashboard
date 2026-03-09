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
        "email": "admin@darpe.org",
        "senha": admin_password,
        "nome_completo": "Administrador DARPE",
        "role": "secretario_regional",
        "status": "ativo",
        "cidade": "Itajaí",
        "unidades": [],
        "ultimo_atendimento": None,
        "foto_url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Verificar se admin já existe
    existing_admin = await db.users.find_one({"email": admin_user["email"]})
    if not existing_admin:
        await db.users.insert_one(admin_user)
        print("✅ Usuário admin criado: admin@darpe.org / admin123")
    else:
        print("ℹ️  Usuário admin já existe")
    
    # Limpar unidades fictícias antigas
    await db.units.delete_many({})
    print("✅ Unidades fictícias removidas - sistema pronto para dados reais")
    
    print("\n✨ Seed concluído com sucesso!")
    print("\n📝 Credenciais de acesso:")
    print("   Email: admin@darpe.org")
    print("   Senha: admin123")
    print("   Role: Secretário Regional (acesso total)")
    print("\n⚠️  Sistema limpo - adicione unidades reais do DARPE pela interface administrativa\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
