from sqlalchemy.orm import Session
from app.models.all_models import User
from app.core.security import hash_password, verify_password, create_access_token


def get_user_by_name(db: Session, name: str) -> User | None:
    """根据用户名查询用户"""
    return db.query(User).filter(User.name == name).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """根据邮箱查询用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """根据 user_id 查询用户"""
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str = "Student"
) -> User:
    """创建新用户，完全匹配 User 模型字段"""
    new_user = User(
        name=name,
        email=email,
        role=role,
        password_hash=hash_password(password),
        status="Active",
        credit_score=100
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_and_get_token(db: Session, email: str, password: str) -> str | None:
    # 1. 查找用户
    user = get_user_by_email(db, email)
    if not user:
        print(f"调试: 未找到邮箱为 {email} 的用户")
        return None
    print(f"调试: 已找到用户 {user.name}")
    
    # 2. 验证密码
    from app.core.security import verify_password
    if not verify_password(password, user.password_hash):
        print(f"调试: 密码验证失败")
        return None
    
    # 3. 生成 Token
    print(f"调试: 密码验证成功，正在生成 Token")
    from app.core.security import create_access_token
    token = create_access_token(
        data={"sub": str(user.user_id), "name": user.name}
    )
    return token
