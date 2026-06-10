from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.all_models import ResearchProject
from app.services.research_service import generate_research_plan_logic

router = APIRouter()


# ---------- 1) 请求/响应模型 ----------

class ResearchPlanRequest(BaseModel):
    major: str = Field(..., description="专业方向")
    topic: str = Field(..., description="课题/研究方向")
    user_id: int = Field(..., description="用户ID")


class ResearchPlanResponse(BaseModel):
    status: str
    project_id: int
    major: str
    topic: str
    outline: Any
    recommended_refs: Any
    research_plan: Optional[Any] = None


# ---------- 2) 路由 ----------

@router.post("/generate-plan", response_model=ResearchPlanResponse)
async def create_research_plan(
    request: ResearchPlanRequest,
    db: Session = Depends(get_db)
):
    """
    根据 major + topic 生成研究计划，并保存到 ResearchProject。
    """
    try:
        # A) 调用 Service（注意：当前 service 是同步 def，不要 await）
        plan_data = generate_research_plan_logic(request.major, request.topic)

        outline = plan_data.get("outline", [])
        recommended_refs = plan_data.get("recommended_refs", [])
        research_plan = plan_data.get("research_plan", {})

        # B) 保存数据库
        # 兼容两种模型情况：
        # 1) ResearchProject 有 research_plan 字段
        # 2) 没有该字段（则仅保存 outline/recommended_refs）
        new_project = ResearchProject(
            user_id=request.user_id,
            major=request.major,
            topic=request.topic,
            outline=outline,
            recommended_refs=recommended_refs,
            status="planning"
        )

        if hasattr(ResearchProject, "research_plan"):
            setattr(new_project, "research_plan", research_plan)

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        # C) 返回前端
        return {
            "status": "success",
            "project_id": new_project.project_id,
            "major": new_project.major,
            "topic": new_project.topic,
            "outline": new_project.outline,
            "recommended_refs": new_project.recommended_refs,
            "research_plan": getattr(new_project, "research_plan", research_plan)
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成研究计划失败: {str(e)}")


@router.get("/project/{project_id}")
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    """
    获取某个研究项目详情（大纲、文献推荐、研究计划等）
    """
    project = db.query(ResearchProject).filter(ResearchProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目未找到")

    return {
        "project_id": project.project_id,
        "user_id": project.user_id,
        "major": project.major,
        "topic": project.topic,
        "outline": project.outline,
        "recommended_refs": project.recommended_refs,
        "research_plan": getattr(project, "research_plan", None),
        "status": project.status
    }
