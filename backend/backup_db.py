import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Carregar .env
load_dotenv(Path(__file__).parent / ".env")

# Pasta de backup com data/hora
backup_dir = Path("backup") / datetime.now().strftime("%Y-%m-%d_%H-%M")
backup_dir.mkdir(parents=True, exist_ok=True)


async def backup_database():
    print("📦 Iniciando backup do banco...")

    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    collections = await db.list_collection_names()

    for collection_name in collections:
        print(f"🔄 Backup da coleção: {collection_name}")

        collection = db[collection_name]
        documents = await collection.find().to_list(length=None)

        # Converter ObjectId para string
        for doc in documents:
            doc["_id"] = str(doc["_id"])

        file_path = backup_dir / f"{collection_name}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)

        print(f"✅ {collection_name} salvo ({len(documents)} registros)")

    client.close()

    print("\n🎯 BACKUP CONCLUÍDO COM SUCESSO!")


if __name__ == "__main__":
    asyncio.run(backup_database()) 