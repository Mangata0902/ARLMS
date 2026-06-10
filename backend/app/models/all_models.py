from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, Numeric, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import Boolean

# 1. Categories
class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    materials = relationship("Material", back_populates="category")

# 2. Users
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    contact_details = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="Active")
    credit_score = Column(Integer, default=100)

# 3. Materials
class Material(Base):
    __tablename__ = "materials"
    material_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(500))
    material_type = Column(String(50))
    isbn_doi = Column(String(50), unique=True)
    publish_year = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    # 新增：关联研究项目（多源按项目检索必须）
    project_id = Column(Integer, ForeignKey("research_projects.project_id", ondelete="SET NULL"), nullable=True, index=True)

    abstract_summary = Column(Text)
    doi_link = Column(String(255))
    file_path = Column(String(500))
    is_local = Column(Boolean, default=True)
    vector_index = Column(String(100), nullable=True)

    category = relationship("Category", back_populates="materials")
    # 可选：如果你有 ResearchProject.materials 反向关系，可打开下面这行
    # project = relationship("ResearchProject", back_populates="materials")


# 4. Materials_Items
class MaterialItem(Base):
    __tablename__ = "materials_items"
    item_id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.material_id", ondelete="CASCADE"), nullable=False)
    barcode = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="Available")
    location_shelf = Column(String(50))
    acquired_date = Column(Date)
    content_chunk = Column(Text)
    # embedding_vector 在 SQL 中是 BYTEA，Python 中用 LargeBinary 或直接跳过测试
    
# 5. Loans
class Loan(Base):
    __tablename__ = "loans"
    loan_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("materials_items.item_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    loan_date = Column(DateTime, server_default=func.now())
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(String(20), default="Borrowed")
    reading_priority = Column(Integer, default=0)

# 6. Fines
class Fine(Base):
    __tablename__ = "fines"
    fine_id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="Unpaid")
    issued_at = Column(DateTime, server_default=func.now())

# 7. Reservations
class Reservation(Base):
    __tablename__ = "reservations"
    reservation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)
    reserved_date = Column(DateTime, server_default=func.now())
    expiry_date = Column(Date)
    status = Column(String(20), default="Pending")

# 8. AI_Read_Analytics
class AIReadAnalytic(Base):
    __tablename__ = "ai_read_analytics"
    analytic_id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reading_duration = Column(Integer)
    ai_score = Column(Numeric(5, 2))
    recommendation = Column(Text)
    analyzed_at = Column(DateTime, server_default=func.now())
    knowledge_points = Column(JSON)
    methodology_feat = Column(Text)
    mermaid_code = Column(Text)
    memo = Column(Text, nullable=True)  


# 9. Semantic_Tags
class SemanticTag(Base):
    __tablename__ = "semantic_tags"
    tag_id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_type = Column(String(50))
    confidence = Column(Numeric(4, 3))

# 10. Conversations
class Conversation(Base):
    __tablename__ = "conversations"
    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.material_id"),nullable=True)
    message = Column(Text, nullable=False)
    role = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    session_id = Column(String(36), nullable=False)
    context_summary = Column(Text)

# 11. User_Interests
class UserInterest(Base):
    __tablename__ = "user_interests"
    interest_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_name = Column(String(100))
    weight = Column(Numeric(3, 2))
    updated_at = Column(DateTime, server_default=func.now())

# 12. MentorStudent
class MentorStudent(Base):
    __tablename__ = "mentor_student"
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())
    
    # 建立关系，方便查询：mentor.students 或 student.mentors
    mentor = relationship("User", foreign_keys=[mentor_id])
    student = relationship("User", foreign_keys=[student_id])

# 13. Research_Projects (研究项目表)
class ResearchProject(Base):
    __tablename__ = "research_projects"
    project_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    major = Column(String(100))        # 专业，如：计算机科学、金融学
    topic = Column(String(255))        # 具体研究方向/题目
    outline = Column(JSON)             # 存储生成的大纲结构
    recommended_refs = Column(JSON)    # 存储推荐的文献列表
    research_plan = Column(JSON) 
    status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

class AIDetectionRecord(Base):
    __tablename__ = "ai_detection_records"

    record_id    = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    original_text= Column(Text, nullable=False)           # 用户提交的原文
    ai_score     = Column(Float, nullable=False)          # AI检测率 0.0~1.0
    result_detail= Column(JSON, nullable=True)            # DeepSeek返回的详细结果
    created_at   = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="detection_records")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="新对话")
    created_at = Column(DateTime, default=func.now())
    # 关联当前对话绑定的文件ID (可选)
    active_file_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_type = Column(String)  # 'reference' 或 'revision'
    content_path = Column(String) # 存储向量数据库索引路径或文件路径
    created_at = Column(DateTime, default=func.now())
