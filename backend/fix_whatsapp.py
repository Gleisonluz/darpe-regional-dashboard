import asyncio
import re
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def normalizar(numero):
    digits = re.sub(r'\D', '', numero)

    if not digits.startswith("55"):
        digits = "55" + digits

    return "+" + digits

async def corrigir():
    usuarios = db.users.find()

    async for user in usuarios:
        if "whatsapp" in user:
            novo = normalizar(user["whatsapp"])

            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"whatsapp": novo}}
            )

            print(user["whatsapp"], " -> ", novo)

    print("Correção finalizada.")

asyncio.run(corrigir())
