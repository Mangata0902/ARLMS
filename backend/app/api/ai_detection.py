from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user
from app.models.all_models import User
from app.services.ai_service import (
    detect_ai_content,
    save_detection_record,
    get_user_detection_history
)

router = APIRouter()

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
# 最大文件大小：20MB
MAX_FILE_SIZE = 20 * 1024 * 1024


# ========== 工具函数：风险等级 ==========
def get_risk_level(score: float) -> str:
    if score < 0.3:
        return "低风险 ✅"
    elif score < 0.6:
        return "中等风险 ⚠️"
    elif score < 0.8:
        return "高风险 🔴"
    else:
        return "极高风险 🚨"


# ========== POST /detect（文件上传）==========
@router.post("/detect", summary="上传论文文件进行AI检测")
async def detect_paper(
    file: UploadFile = File(..., description="上传论文文件，支持 PDF / DOCX / DOC / TXT"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传完整论文文件，支持 PDF、DOCX、DOC、TXT 格式。
    系统会自动提取文本，分段调用 DeepSeek 进行 AI 检测，返回综合评分。
    需要登录（Bearer Token）。
    """
    # 1. 校验文件格式
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 '{ext}'，请上传 PDF、DOCX 或 TXT 文件"
        )

    # 2. 读取文件内容
    file_bytes = await file.read()

    # 3. 校验文件大小
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大（{len(file_bytes)//1024//1024}MB），最大支持 20MB"
        )

    # 4. 调用检测服务
    try:
        result = detect_ai_content(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 5. 保存记录（original_text 只存前500字，节省数据库空间）
    preview_text = result.get("reasoning", "")[:500]
    record = save_detection_record(
        db=db,
        user_id=current_user.user_id,
        original_text=preview_text,
        ai_score=result["ai_score"],
        result_detail=result
    )

    # 6. 返回结果
    return {
        "record_id":      record.record_id,
        "filename":       filename,
        "ai_score":       result["ai_score"],
        "percentage":     f"{result['ai_score'] * 100:.1f}%",
        "level":          get_risk_level(result["ai_score"]),
        "reasoning":      result["reasoning"],
        "conclusion":     result["conclusion"],
        "chunks_checked": result["chunks_checked"],
        "total_chunks":   result["total_chunks"],
        "total_chars":    result["total_chars"],
        "chunk_details":  result["chunk_details"]
    }


# ========== GET /history ==========
@router.get("/history", summary="查看我的检测历史")
def get_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户最近的检测记录，需要登录。"""
    records = get_user_detection_history(db, current_user.user_id, limit)
    return [
        {
            "record_id":  r.record_id,
            "ai_score":   r.ai_score,
            "percentage": f"{r.ai_score * 100:.1f}%",
            "level":      get_risk_level(r.ai_score),
            "conclusion": r.result_detail.get("conclusion", "") if r.result_detail else "",
            "created_at": r.created_at,
        }
        for r in records
    ]
