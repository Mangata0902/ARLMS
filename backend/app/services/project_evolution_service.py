from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.all_models import ResearchProject

# 只允许更新这些字段，防止 AI 乱改
ALLOWED_FIELDS = {"outline", "research_plan", "status", "topic", "major"}

def apply_project_evolution(
    db: Session,
    project_id: int,
    changes: Dict[str, Any]
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    返回: (ok, message, applied_changes)
    """
    project = db.query(ResearchProject).filter(ResearchProject.project_id == project_id).first()
    if not project:
        return False, "project not found", {}

    applied = {}
    for k, v in changes.items():
        if k in ALLOWED_FIELDS:
            setattr(project, k, v)
            applied[k] = v

    if not applied:
        return False, "no valid fields to update", {}

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return True, "updated", applied
    except Exception as e:
        db.rollback()
        return False, f"db error: {e}", {}
