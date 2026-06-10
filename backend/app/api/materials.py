from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from app.core.database import get_db
from app.models.all_models import Material, AIReadAnalytic, SemanticTag, Conversation

router = APIRouter()

# 1. 获取文献列表接口
@router.get("/")
async def get_materials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取所有已上传的文献列表
    """
    materials = db.query(Material).order_by(Material.created_at.desc()).offset(skip).limit(limit).all()
    
    # 格式化返回数据
    result = []
    for m in materials:
        result.append({
            "material_id": m.material_id,
            "title": m.title,
            "author": m.author,
            "material_type": m.material_type,
            "created_at": m.created_at,
            "is_local": m.is_local
        })
    return {"total": len(result), "data": result}

# 2. 删除文献接口
@router.delete("/{material_id}")
async def delete_material(material_id: int, db: Session = Depends(get_db)):
    """
    删除文献，同时清理物理文件、向量库和关联的数据库记录
    """
    # 1. 查找数据库记录
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="未找到该文献")

    # 2. 删除本地 PDF 物理文件
    if material.file_path and os.path.exists(material.file_path):
        try:
            os.remove(material.file_path)
        except Exception as e:
            print(f"删除PDF文件失败: {e}")

    # 3. 删除 ChromaDB 向量库文件夹
    if material.vector_index:
        vector_path = f"./storage/chroma_db/{material.vector_index}"
        if os.path.exists(vector_path):
            try:
                shutil.rmtree(vector_path)
            except Exception as e:
                print(f"删除向量库失败: {e}")

    # 4. 删除数据库中的关联记录 (防止外键约束报错)
    db.query(AIReadAnalytic).filter(AIReadAnalytic.material_id == material_id).delete()
    db.query(SemanticTag).filter(SemanticTag.material_id == material_id).delete()
    db.query(Conversation).filter(Conversation.material_id == material_id).delete()

    # 5. 删除主表记录并提交
    db.delete(material)
    db.commit()

    return {"message": f"文献 {material.title} 及其关联数据已彻底删除"}
