from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from security import get_current_user
import base64
import uuid
import os
from pathlib import Path

def create_upload_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/upload", tags=["upload"])
    
    # Criar diretório de uploads se não existir
    UPLOAD_DIR = Path("/app/backend/uploads")
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    @router.post("/photo")
    async def upload_photo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Apenas imagens são permitidas")
        
        # Ler arquivo
        contents = await file.read()
        
        # Verificar tamanho (max 5MB)
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 5MB")
        
        # Converter para base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        image_url = f"data:{file.content_type};base64,{base64_image}"
        
        # Atualizar foto do usuário
        await db.users.update_one(
            {"id": current_user["sub"]},
            {"$set": {"foto_url": image_url}}
        )
        
        return {"foto_url": image_url, "message": "Foto enviada com sucesso"}
    
    return router
