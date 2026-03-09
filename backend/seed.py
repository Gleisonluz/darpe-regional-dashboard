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
    
    # Criar algumas unidades de exemplo
    unidades_exemplo = [
        {
            "id": "unit-001",
            "nome": "Centro de Evangelização Itajaí Centro",
            "cidade": "Itajaí",
            "dia_semana": "quarta",
            "horario": "19:30",
            "tipo_atividade": "Evangelização",
            "endereco": "Rua das Flores, 123 - Centro",
            "responsaveis": ["admin-001"],
            "ativo": True,
            "observacoes": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "unit-002",
            "nome": "Grupo de Estudo Balneário Camboriú",
            "cidade": "Balneário Camboriú",
            "dia_semana": "quinta",
            "horario": "20:00",
            "tipo_atividade": "Estudo",
            "endereco": "Av. Atlântica, 456",
            "responsaveis": ["admin-001"],
            "ativo": True,
            "observacoes": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "unit-003",
            "nome": "Casa Espírita Navegantes",
            "cidade": "Navegantes",
            "dia_semana": "domingo",
            "horario": "10:00",
            "tipo_atividade": "Culto Gospel",
            "endereco": "Rua Principal, 789",
            "responsaveis": [],
            "ativo": True,
            "observacoes": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "unit-004",
            "nome": "Reunião Pública Brusque",
            "cidade": "Brusque",
            "dia_semana": "segunda",
            "horario": "19:00",
            "tipo_atividade": "Palestra",
            "endereco": "Rua dos Imigrantes, 321",
            "responsaveis": [],
            "ativo": True,
            "observacoes": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "unit-005",
            "nome": "Centro Espírita Blumenau",
            "cidade": "Blumenau",
            "dia_semana": "sexta",
            "horario": "20:30",
            "tipo_atividade": "Evangelização",
            "endereco": "Rua XV de Novembro, 555",
            "responsaveis": [],
            "ativo": True,
            "observacoes": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Inserir unidades
    for unidade in unidades_exemplo:
        existing = await db.units.find_one({"id": unidade["id"]})
        if not existing:
            await db.units.insert_one(unidade)
            print(f"✅ Unidade criada: {unidade['nome']}")
        else:
            print(f"ℹ️  Unidade já existe: {unidade['nome']}")
    
    # Atualizar unidades do admin
    await db.users.update_one(
        {"id": "admin-001"},
        {"$set": {"unidades": ["unit-001", "unit-002"]}}
    )
    
    print("\n✨ Seed concluído com sucesso!")
    print("\n📝 Credenciais de acesso:")
    print("   Email: admin@darpe.org")
    print("   Senha: admin123")
    print("   Role: Secretário Regional (acesso total)\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
