import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient

async def fix():
    uri = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI")
    if not uri:
        print("ERRO: MONGO_URI nao encontrada")
        return

    db = AsyncIOMotorClient(uri)["darpe"]

    count = await db.users.count_documents({"senha": {"$exists": False}})
    print("Usuarios sem senha:", count)

    users = await db.users.find(
        {"senha": {"$exists": False}},
        {"_id": 0, "whatsapp": 1, "nome_completo": 1}
    ).to_list(None)

    for u in users:
        print(u)

asyncio.run(fix())