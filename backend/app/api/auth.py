from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.services.auth_service import (
    get_user_by_name,
    get_user_by_email,
    create_user,
    login_and_get_token
)
from app.utils.dependencies import get_db, get_current_user
from app.models.all_models import User

router = APIRouter()


# ────────────────────────────────────────
# 请求体 Schema
# ────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "Student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    contact_details: Optional[str] = None
    date_of_birth: Optional[str] = None  # 格式: "YYYY-MM-DD"

# 定义更新资料的请求体
class UserUpdate(BaseModel):
    name: Optional[str] = None
    contact_details: Optional[str] = None
    date_of_birth: Optional[str] = None

# ────────────────────────────────────────
# 接口
# ────────────────────────────────────────

@router.post("/register", summary="用户注册")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户，用户名和邮箱不能重复"""
    if get_user_by_name(db, body.name):
        raise HTTPException(status_code=400, detail="用户名已被占用")
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = create_user(
        db=db,
        name=body.name,
        email=body.email,
        password=body.password,
        role=body.role
    )
    return {
        "message": "注册成功",
        "user_id": user.user_id,
        "name": user.name,
        "role": user.role
    }


@router.post("/login", summary="用户登录")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """登录成功后返回 JWT Token，前端需保存此 Token"""
    print(f"尝试登录: 邮箱={body.email}, 密码={body.password}") # 加这行
    token = login_and_get_token(db, body.email, body.password)
    if not token:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """需要登录，前端请求时 Header 携带 Authorization: Bearer <token>"""
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "contact_details": current_user.contact_details,
        "date_of_birth": current_user.date_of_birth,
        "credit_score": current_user.credit_score,
        "status": current_user.status,
        "created_at": current_user.created_at
    }


@router.put("/me", summary="更新个人信息")
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新联系方式和生日"""
    if body.contact_details is not None:
        current_user.contact_details = body.contact_details
    if body.date_of_birth is not None:
        from datetime import date
        current_user.date_of_birth = date.fromisoformat(body.date_of_birth)
    db.commit()
    db.refresh(current_user)
    return {"message": "个人信息更新成功"}


@router.put("/me/password", summary="修改密码")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密码，需要验证旧密码"""
    from app.core.security import verify_password, hash_password
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "密码修改成功"}

@router.put("/update-me", summary="修改个人资料")
def update_user_info(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户在个人中心修改自己的姓名、联系方式等信息
    """
    if body.name:
        current_user.name = body.name
    if body.contact_details:
        current_user.contact_details = body.contact_details
    if body.date_of_birth:
        current_user.date_of_birth = body.date_of_birth
    
    db.commit()
    db.refresh(current_user)
    return {"message": "资料更新成功", "user": {
        "name": current_user.name,
        "contact_details": current_user.contact_details
    }}