import os
import shutil
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

# 导入数据库依赖
from app.core.database import get_db
# 导入模型
from app.models.all_models import Material, AIReadAnalytic
# 导入核心 Service
from app.services.ingestion_service import run_ingestion_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_academic_document(
    file: UploadFile = File(...),
    mode: str = Form("reading", description="模式：diagnostic(诊断自己论文) 或 reading(导读外部文献)"),
    requirement: str = Form(None, description="用户对学术导师的特定解析要求"),
    db: Session = Depends(get_db)
):
    """
    学术文档入库接口：支持『学生论文诊断』和『权威文献导读』双模式
    """
    # --- 1. 基础校验 ---
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="目前仅支持 PDF 格式。")

    # --- 2. 准备存储路径 ---
    # 建议使用绝对路径防止相对路径混淆，或者确保 backend 目录下有 storage 文件夹
    upload_dir = os.path.join(os.getcwd(), "storage", "pdfs")
    os.makedirs(upload_dir, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    # --- 3. 保存文件 ---
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"文件保存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        await file.close() # 显式关闭上传流

    # --- 4. 调用 AI 流水线 ---
    try:
        # 确保你的 ingestion_service.py 中的 run_ingestion_pipeline 已经接收 mode 参数
        material_id = await run_ingestion_pipeline(
            file_path=file_path,
            file_name=file.filename,
            user_requirement=requirement,
            mode=mode,
            db=db
        )
        
        return {
            "status": "success",
            "data": {
                "material_id": material_id,
                "mode": mode,
                "message": f"已按【{'学术诊断' if mode=='diagnostic' else '文献导读'}】模式处理完成"
            }
        }

    except Exception as e:
        logger.error(f"AI 处理流水线失败: {str(e)}", exc_info=True)
        if os.path.exists(file_path): 
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"AI处理失败: {str(e)}")

@router.get("/materials/{m_id}")
async def get_material_detail(m_id: int, db: Session = Depends(get_db)):
    """
    获取指定文档的 AI 深度解析详情
    """
    material = db.query(Material).filter(Material.material_id == m_id).first()
    if not material:
        raise HTTPException(status_code=404, detail=f"找不到 ID 为 {m_id} 的文档记录。")
    
    analytics = db.query(AIReadAnalytic).filter(AIReadAnalytic.material_id == m_id).first()
    
    # 安全转换 AI 评分
    safe_score = None
    if analytics and analytics.ai_score is not None:
        try:
            safe_score = float(analytics.ai_score)
        except (ValueError, TypeError):
            safe_score = 0.0

    return {
        "status": "success",
        "data": {
            "base_info": {
                "id": material.material_id,
                "title": material.title,
                "author": material.author,
                "abstract": material.abstract_summary,
                "type": material.material_type
            },
            "ai_analysis": {
                "knowledge_points": analytics.knowledge_points if analytics else None,
                "methodology": analytics.methodology_feat if analytics else None,
                "mermaid_diagram": analytics.mermaid_code if analytics else None,
                "recommendation": analytics.recommendation if analytics else None,
                "ai_score": safe_score
            }
        }
    }
