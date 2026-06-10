import os
import logging
import json
import re
from typing import Optional, Dict, Any, Tuple, List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.all_models import Material, AIReadAnalytic, Conversation, ResearchProject, ChatSession, Document
from datetime import datetime

from openai import OpenAI

# --- RAG 相关导入 ---
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

router = APIRouter()
logger = logging.getLogger(__name__)

# =========================
# 自进化开关（环境变量）
# =========================
def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(default)).strip().lower()
    return v in {"1", "true", "yes", "on"}

AUTO_EVOLUTION_ENABLED = _env_bool("AUTO_EVOLUTION_ENABLED", False)
REQUIRE_CONFIRM = _env_bool("REQUIRE_CONFIRM", True)

# 允许更新字段白名单（监管）
ALLOWED_EVOLUTION_FIELDS = {"outline", "research_plan", "status", "topic", "major"}

# JSON代码块提取
JSON_BLOCK_RE = re.compile(r"```json\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)

# 初始化 OpenAI/DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 确保与 ingestion_service.py 中的路径完全一致
embeddings = HuggingFaceEmbeddings(model_name="./models")

# 向量数据库存储根目录
CHROMA_DB_DIR = os.path.abspath(os.path.join("storage", "chroma_db"))


# =========================
# Pydantic 模型
# =========================
class ChatRequest(BaseModel):
    user_message: str
    session_id: str
    project_id: Optional[int] = None
    material_id: Optional[int] = None
    focus_type: Optional[str] = None   # chapter / section / plan_key
    focus_value: Optional[str] = None  # 第三章 / 3.3 / timeline
    multi_doc_limit: Optional[int] = 5
    per_doc_k: Optional[int] = 3


class SessionCreateRequest(BaseModel):
    title: Optional[str] = "新对话"
    project_id: Optional[int] = None
    active_file_id: Optional[int] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    active_file_id: Optional[int] = None
    clear_file: Optional[bool] = False


# =========================
# 会话管理路由（历史记录）
# =========================

@router.post("/sessions")
async def create_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    try:
        active_file_id = req.active_file_id
        
        # 校验：只在有 ID 时才去查表
        if active_file_id:
            mat = db.query(Material).filter(Material.material_id == active_file_id).first()
            if not mat:
                active_file_id = None # 文献不存在则置空
        
        # 创建对象
        new_session = ChatSession(
            title=req.title,
            active_file_id=active_file_id,
            created_at=datetime.utcnow()
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return {"session_id": new_session.id}
        
    except Exception as e:
        db.rollback() # 发生错误回滚事务
        print(f"DEBUG: 创建会话发生错误: {str(e)}")
        # 打印详细堆栈
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail="创建对话失败")


@router.get("/sessions")
async def list_sessions(
    project_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取历史会话列表，用于侧边栏展示历史记录"""
    query = db.query(ChatSession)
    sessions = query.order_by(ChatSession.created_at.desc()).limit(limit).all()
    result = []
    for s in sessions:
        last_msg = (
            db.query(Conversation)
            .filter(Conversation.session_id == str(s.id))
            .order_by(Conversation.created_at.desc())
            .first()
        )
        result.append({
            "session_id": str(s.id),
            "id": s.id,
            "title": s.title,
            "active_file_id": s.active_file_id,
            "created_at": s.created_at,
            "last_message": last_msg.message[:50] if last_msg else "",
            "last_role": last_msg.role if last_msg else ""
        })
    return {"total": len(result), "data": result}


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取单个会话详情（含绑定文献信息）"""
    try:
        sid = int(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id 必须为数字")

    session = db.query(ChatSession).filter(ChatSession.id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    material_info = None
    if session.active_file_id:
        mat = db.query(Material).filter(Material.material_id == session.active_file_id).first()
        if mat:
            material_info = {
                "material_id": mat.material_id,
                "title": mat.title,
                "file_type": getattr(mat, "file_type", None)
            }

    return {
        "session_id": str(session.id),
        "id": session.id,
        "title": session.title,
        "active_file_id": session.active_file_id,
        "material_info": material_info,
        "created_at": session.created_at
    }


@router.patch("/sessions/{session_id}")
async def update_session(
    session_id: str,
    req: SessionUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        sid = int(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id 必须为数字")

    session = db.query(ChatSession).filter(ChatSession.id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    if req.title is not None:
        session.title = req.title
    if req.clear_file:
        session.active_file_id = None
    elif req.active_file_id is not None:
        mat = db.query(Material).filter(Material.material_id == req.active_file_id).first()
        if not mat:
            raise HTTPException(status_code=404, detail=f"文献 {req.active_file_id} 不存在")
        session.active_file_id = req.active_file_id

    db.commit()
    db.refresh(session)
    return {
        "session_id": str(session.id),
        "title": session.title,
        "active_file_id": session.active_file_id,
        "updated": True
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """删除会话及其所有消息记录"""
    try:
        sid = int(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="session_id 必须为数字")

    session = db.query(ChatSession).filter(ChatSession.id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    db.query(Conversation).filter(Conversation.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"deleted": True, "session_id": session_id}


# =========================
# 历史消息路由
# =========================

@router.get("/history")
async def get_chat_history(
    session_id: str,
    material_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Conversation).filter(Conversation.session_id == session_id)

    if material_id is not None:
        query = query.filter(Conversation.material_id == material_id)

    history = query.order_by(Conversation.created_at.asc()).all()

    result = []
    for msg in history:
        result.append({
            "role": msg.role,
            "content": msg.message,
            "created_at": msg.created_at
        })

    return {"total": len(result), "data": result}


# =========================
# 自进化相关函数
# =========================

def _parse_evolution_block(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    m = JSON_BLOCK_RE.search(text)
    candidate = None
    if m:
        candidate = m.group(1)
    else:
        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            candidate = stripped

    if not candidate:
        return None

    try:
        obj = json.loads(candidate)
    except Exception:
        return None

    evo = obj.get("evolution")
    if not isinstance(evo, dict):
        return None

    should_update = bool(evo.get("should_update", False))
    reason = str(evo.get("reason", "")).strip()
    changes = evo.get("changes", {})

    if not isinstance(changes, dict):
        changes = {}

    return {
        "should_update": should_update,
        "reason": reason,
        "changes": changes
    }


def _guard_evolution(changes: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    if not changes:
        return False, "changes 为空", {}

    sanitized = {}
    dropped = []

    for k, v in changes.items():
        if k not in ALLOWED_EVOLUTION_FIELDS:
            dropped.append(k)
            continue

        try:
            raw = json.dumps(v, ensure_ascii=False)
            if len(raw) > 20000:
                dropped.append(k)
                continue
        except Exception:
            dropped.append(k)
            continue

        sanitized[k] = v

    if not sanitized:
        return False, f"无合法可更新字段，已丢弃: {dropped}", {}

    return True, f"guard通过，丢弃字段: {dropped}" if dropped else "guard通过", sanitized


def _apply_evolution_to_project(
    db: Session,
    project_id: int,
    changes: Dict[str, Any]
) -> Tuple[bool, str, Dict[str, Any]]:
    project = db.query(ResearchProject).filter(ResearchProject.project_id == project_id).first()
    if not project:
        return False, "project not found", {}

    applied = {}
    for k, v in changes.items():
        setattr(project, k, v)
        applied[k] = v

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return True, "updated", applied
    except Exception as e:
        db.rollback()
        logger.error(f"项目自动进化落库失败: {e}")
        return False, f"db error: {e}", {}


def _maybe_handle_evolution(
    db: Session,
    req: ChatRequest,
    ai_response: str
) -> Dict[str, Any]:
    result = {
        "switch": {
            "AUTO_EVOLUTION_ENABLED": AUTO_EVOLUTION_ENABLED,
            "REQUIRE_CONFIRM": REQUIRE_CONFIRM
        },
        "detected": False,
        "should_update": False,
        "reason": "",
        "guard_ok": False,
        "applied": False,
        "message": "",
        "proposed_changes": {},
        "applied_fields": []
    }

    if req.project_id is None:
        result["message"] = "无 project_id，跳过自动进化"
        return result

    evo = _parse_evolution_block(ai_response)
    if not evo:
        result["message"] = "未检测到 evolution JSON"
        return result

    result["detected"] = True
    result["should_update"] = bool(evo.get("should_update"))
    result["reason"] = evo.get("reason", "")
    result["proposed_changes"] = evo.get("changes", {}) or {}

    if not result["should_update"]:
        result["message"] = "模型判定无需更新"
        return result

    if not AUTO_EVOLUTION_ENABLED:
        result["message"] = "AUTO_EVOLUTION_ENABLED=false，已拦截自动落库"
        return result

    guard_ok, guard_msg, sanitized = _guard_evolution(result["proposed_changes"])
    result["guard_ok"] = guard_ok
    if not guard_ok:
        result["message"] = f"监管拦截: {guard_msg}"
        return result

    if REQUIRE_CONFIRM:
        result["message"] = "REQUIRE_CONFIRM=true，返回建议，不自动落库"
        result["proposed_changes"] = sanitized
        return result

    ok, msg, applied = _apply_evolution_to_project(db, req.project_id, sanitized)
    result["applied"] = ok
    result["message"] = msg
    result["applied_fields"] = list(applied.keys()) if ok else []
    return result


# =========================
# RAG 检索函数
# =========================

def _build_sources_and_context(material: Material, user_query: str) -> Tuple[List[Dict[str, Any]], str]:
    sources: List[Dict[str, Any]] = []
    rag_context = ""

    vector_col_name = getattr(material, "vector_index", None)
    if not vector_col_name:
        return sources, rag_context

    vector_db = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name=vector_col_name
    )

    docs_scores = []
    try:
        docs_scores = vector_db.similarity_search_with_relevance_scores(user_query, k=5)
    except Exception as e:
        logger.warning(f"relevance_scores 检索失败，降级到普通检索: {e}")
        docs = vector_db.similarity_search(user_query, k=5)
        docs_scores = [(d, None) for d in docs]

    context_blocks = []
    for idx, (doc, score) in enumerate(docs_scores, start=1):
        text = (doc.page_content or "").strip()
        metadata = doc.metadata if isinstance(doc.metadata, dict) else {}

        source_item = {
            "index": idx,
            "material_id": material.material_id,
            "material_title": material.title,
            "text": text,
            "relevance_score": float(score) if score is not None else None,
            "raw_score": float(score) if score is not None else None,
            "metadata": metadata
        }
        sources.append(source_item)

        context_blocks.append(
            f"[{idx}] 标题: {material.title}\n"
            f"片段: {text}\n"
            f"metadata: {json.dumps(metadata, ensure_ascii=False)}"
        )

    if context_blocks:
        rag_context = "\n\n【可引用证据片段（请按编号引用）】\n" + "\n\n---\n\n".join(context_blocks)

    return sources, rag_context


def _build_project_multi_sources_and_context(
    db: Session,
    project_id: int,
    user_query: str,
    max_materials: int = 5,
    per_material_k: int = 3
) -> Tuple[List[Dict[str, Any]], str]:
    sources: List[Dict[str, Any]] = []
    context_blocks: List[str] = []

    max_materials = max(1, min(max_materials, 8))
    per_material_k = max(1, min(per_material_k, 5))

    materials = (
        db.query(Material)
        .filter(
            Material.project_id == project_id,
            Material.vector_index.isnot(None)
        )
        .order_by(Material.material_id.desc())
        .limit(max_materials)
        .all()
    )

    if not materials:
        return [], ""

    global_idx = 0
    for m in materials:
        try:
            vector_db = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=embeddings,
                collection_name=m.vector_index
            )

            try:
                docs_scores = vector_db.similarity_search_with_relevance_scores(user_query, k=per_material_k)
            except Exception as e:
                logger.warning(f"多源检索降级 material_id={m.material_id}: {e}")
                docs = vector_db.similarity_search(user_query, k=per_material_k)
                docs_scores = [(d, None) for d in docs]

            for doc, score in docs_scores:
                global_idx += 1
                text = (doc.page_content or "").strip()
                metadata = doc.metadata if isinstance(doc.metadata, dict) else {}

                sources.append({
                    "index": global_idx,
                    "material_id": m.material_id,
                    "material_title": m.title,
                    "text": text,
                    "relevance_score": float(score) if score is not None else None,
                    "raw_score": float(score) if score is not None else None,
                    "metadata": metadata
                })

                context_blocks.append(
                    f"[{global_idx}] 标题: {m.title}\n"
                    f"片段: {text}\n"
                    f"metadata: {json.dumps(metadata, ensure_ascii=False)}"
                )

        except Exception as e:
            logger.error(f"多源文献检索失败 material_id={m.material_id}: {e}")
            continue

    if not context_blocks:
        return [], ""

    rag_context = "\n\n【项目多文献可引用证据片段（请按编号引用）】\n" + "\n\n---\n\n".join(context_blocks)
    return sources, rag_context


# =========================
# 核心上下文准备（含上下文隔离逻辑）
# =========================

def _prepare_chat_context(req: ChatRequest, db: Session):
    """
    上下文隔离优先级：
      1. ChatSession.active_file_id（会话绑定文献，最高优先级）
      2. req.material_id（请求中显式传入）
      3. req.project_id（项目多文献兜底）
      4. 以上均无：纯通用对话模式（不报错）
    """
    # ===== Step 1: 从 ChatSession 获取绑定文献 =====
    session_bound_file_id: Optional[int] = None
    session_title: Optional[str] = None

    try:
        sid = int(req.session_id)
        session = db.query(ChatSession).filter(ChatSession.id == sid).first()
        if session:
            session_bound_file_id = session.active_file_id
            session_title = session.title
    except (ValueError, Exception) as e:
        logger.warning(f"ChatSession 查询失败，降级到 req.material_id: {e}")

    # ===== Step 2: 确定最终使用的 material_id =====
    if session_bound_file_id is not None:
        material_id = session_bound_file_id
        logger.info(f"[上下文隔离] session={req.session_id} 使用绑定文献 material_id={material_id}")
    else:
        material_id = req.material_id if (req.material_id is not None and req.material_id != 0) else None

    # ===== Step 3: 查询文献对象 =====
    material = None
    if material_id is not None:
        material = db.query(Material).filter(Material.material_id == material_id).first()
        if material:
            _ = db.query(AIReadAnalytic).filter(AIReadAnalytic.material_id == material_id).first()
        else:
            logger.warning(f"material_id={material_id} 在数据库中不存在，将降级处理")
            material_id = None

    # ===== Step 4: 无文献且无项目时，允许纯对话模式（不报错） =====  ← 修改点
    sources: List[Dict[str, Any]] = []
    rag_context = ""

    if not material and not req.project_id:
        # 通用对话模式：不关联文献或项目，AI 基于通用学术知识回答
        rag_context = "\n(提示：当前为通用对话模式，未关联具体文献或项目，AI将基于通用学术知识回答)"

    # ===== Step 5: RAG 检索 =====
    elif material:
        try:
            sources, rag_context = _build_sources_and_context(material, req.user_message)
        except Exception as e:
            logger.error(f"单文献 RAG 检索失败 material_id={material_id}: {e}")
            rag_context = "\n(提示：暂时无法从该文献中检索到细节，请稍后重试)"

    elif req.project_id is not None:
        try:
            multi_doc_limit = req.multi_doc_limit if req.multi_doc_limit is not None else 5
            per_doc_k = req.per_doc_k if req.per_doc_k is not None else 3
            sources, rag_context = _build_project_multi_sources_and_context(
                db=db,
                project_id=req.project_id,
                user_query=req.user_message,
                max_materials=multi_doc_limit,
                per_material_k=per_doc_k
            )
            if not sources:
                rag_context = "\n(提示：该项目下暂无可检索文献，或文献尚未建立向量索引)"
        except Exception as e:
            logger.error(f"项目多文献 RAG 检索失败: {e}")
            rag_context = "\n(提示：暂时无法从项目文献中检索到细节)"

    # ===== Step 6: 项目背景 + 焦点上下文 =====
    project_context = ""
    selected_focus_context = ""

    if req.project_id is not None:
        project = db.query(ResearchProject).filter(ResearchProject.project_id == req.project_id).first()
        if project:
            project_context = f"""
【当前研究项目背景】：
- 研究主题：{project.topic}
- 专业方向：{project.major}
- 完整大纲：{project.outline}
- 详细计划：{project.research_plan}
"""
            if req.focus_type and req.focus_value:
                curr_outline = project.outline if isinstance(project.outline, list) else json.loads(project.outline or "[]")
                curr_plan = project.research_plan if isinstance(project.research_plan, dict) else json.loads(project.research_plan or "{}")

                if req.focus_type == "chapter":
                    hit = [item for item in curr_outline if item.get("chapter") == req.focus_value]
                    if hit:
                        selected_focus_context = f"【重点关注章节内容】：{hit[0]}"

                elif req.focus_type == "section":
                    matched_detail = ""
                    for ch in curr_outline:
                        for sec in ch.get("sections", []):
                            if req.focus_value in sec:
                                matched_detail = f"属于 {ch.get('chapter')} {ch.get('title')} 下的：{sec}"
                                break
                    selected_focus_context = f"【重点关注小节详情】：{matched_detail if matched_detail else req.focus_value}"

                elif req.focus_type == "plan_key":
                    detail = curr_plan.get(req.focus_value, "未找到该项计划说明")
                    selected_focus_context = f"【重点关注计划细节 - {req.focus_value}】：{detail}"

    # ===== Step 7: 构建 System Prompt =====
    locked_doc_hint = ""
    if material:
        locked_doc_hint = f"\n【⚠️ 当前对话已锁定文献】：《{material.title}》\n- 你只能基于上述该文献的证据片段进行回答\n- 严禁引用或推断该文献以外的任何内容\n- 若该文献未覆盖用户问题，请明确说明\"证据不足/原文未覆盖\"\n"

    system_prompt = f"""
你是一位资深学术导师。你正在指导学生完成研究项目。
{locked_doc_hint}
{project_context}
{selected_focus_context}
{rag_context}

【你的任务】：
1. 针对学生提出的问题，结合上述项目背景给出深度指导。
2. 如果学生引用了特定章节或计划点（见"重点关注"部分），请针对该点的实施细节、理论支撑、潜在难点给出至少3条具体建议。
3. 语气要专业且具有启发性，像真正的导师一样思考。
4. 当提供的是"项目多文献证据"时，请优先输出：
   - 共同点（共识）
   - 冲突点（分歧）
   - 互补点（可整合之处）
   并给出"对当前项目可执行"的整合建议。

【引用规则（必须遵守）】：
1. 若使用了"可引用证据片段"，每条关键结论后必须加引用编号，如 [1]、[2]。
2. 只能引用给定片段编号，不得编造来源。
3. 若证据不足，明确写"证据不足/原文未覆盖"。

【项目自动进化输出协议（必须遵守）】：
- 在回答末尾追加一个 JSON 代码块：
```json
{{
  "evolution": {{
    "should_update": false,
    "reason": "",
    "changes": {{}}
  }}
}}
```
- 如果你明确建议更新项目，则把 should_update 设为 true，并在 changes 中仅使用以下字段：
  outline, research_plan, status, topic, major
"""

    # ===== Step 8: 历史消息 =====
    history_query = db.query(Conversation).filter(Conversation.session_id == req.session_id)
    history_records = history_query.order_by(Conversation.created_at.desc()).limit(6).all()
    history_records.reverse()

    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in history_records:
        messages_payload.append({"role": msg.role, "content": msg.message})
    messages_payload.append({"role": "user", "content": req.user_message})

    return {
        "material_id": material_id,
        "messages_payload": messages_payload,
        "sources": sources
    }


# =========================
# 消息保存
# =========================

def _save_chat_messages(db: Session, req: ChatRequest, material_id: Optional[int], ai_response: str):
    try:
        new_chat = Conversation(
            user_id=1,
            material_id=material_id,
            message=req.user_message,
            role="user",
            session_id=req.session_id
        )
        ai_chat = Conversation(
            user_id=1,
            material_id=material_id,
            message=ai_response,
            role="assistant",
            session_id=req.session_id
        )
        db.add(new_chat)
        db.add(ai_chat)
        db.commit()

        try:
            sid = int(req.session_id)
            session = db.query(ChatSession).filter(ChatSession.id == sid).first()
            if session and session.title == "新对话":
                session.title = req.user_message[:20] + ("..." if len(req.user_message) > 20 else "")
                db.commit()
        except Exception:
            pass

    except Exception as e:
        db.rollback()
        logger.error(f"对话记录保存失败: {e}")


# =========================
# 核心对话逻辑
# =========================

def _run_chat_logic(req: ChatRequest, db: Session):
    prep = _prepare_chat_context(req, db)
    material_id = prep["material_id"]
    messages_payload = prep["messages_payload"]
    sources = prep["sources"]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages_payload
        )
        ai_response = response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"DeepSeek API 调用失败: {e}")
        raise HTTPException(status_code=500, detail="AI 导师暂时离线，请稍后再试")

    # 处理进化逻辑
    evolution = _maybe_handle_evolution(db, req, ai_response)
    
    # 保存原始记录（包含 JSON 块）
    _save_chat_messages(db, req, material_id, ai_response)

    # 剔除 JSON 块，只返回纯净的回复给前端
    clean_response = JSON_BLOCK_RE.sub('', ai_response).strip()

    return {
        "response": clean_response,
        "sources": sources,
        "context_used": req.project_id is not None,
        "focus_used": True if (req.focus_type and req.focus_value) else False,
        "evolution": evolution
    }



# =========================
# 路由
# =========================

@router.post("/chat")
async def chat_with_mentor(
    req: ChatRequest = Body(...),
    db: Session = Depends(get_db)
):
    return _run_chat_logic(req, db)


@router.post("/chat/stream")
async def chat_with_mentor_stream(
    req: ChatRequest = Body(...),
    db: Session = Depends(get_db)
):
    prep = _prepare_chat_context(req, db)
    material_id = prep["material_id"]
    messages_payload = prep["messages_payload"]
    sources = prep["sources"]

    def event_generator():
        full_content = ""
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_payload,
                stream=True
            )

                        # 用于存储流式接收到的完整内容
            for chunk in stream:
                delta = ""
                try:
                    delta = chunk.choices[0].delta.content or ""
                except Exception:
                    delta = ""

                if delta:
                    full_content += delta
                    
                    # 改进过滤逻辑：
                    # 只有当 full_content 还没有检测到 JSON 块的开始，且当前 delta 不是 JSON 块的一部分时才发送
                    # 如果检测到 ```json，我们直接停止向前端发送（通过 break 或者简单的判断）
                    if "```json" in full_content:
                        continue # 已经进入 JSON 块，跳过后续发送
                    
                    # 额外保护：如果 delta 里包含 ```，防止它刚好切断显示
                    # 我们只发送不含 ``` 的部分（或者简单处理）
                    clean_delta = delta.replace("```", "")
                    if clean_delta:
                        yield f"data: {json.dumps({'content': clean_delta}, ensure_ascii=False)}\n\n"

                    else:
                        # 如果已经进入 JSON 块，则不再推送到前端
                        pass

            # 流结束后，处理进化逻辑和保存
            evolution = _maybe_handle_evolution(db, req, full_content)
            _save_chat_messages(db, req, material_id, full_content)

            yield f"data: {json.dumps({'meta': {'sources': sources, 'evolution': evolution}}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"流式调用失败: {e}")
            err = {"error": "AI 导师暂时离线，请稍后再试"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )



@router.post("/chat/{material_id}")
async def chat_with_mentor_legacy(
    material_id: int,
    user_message: str = Body(...),
    session_id: str = Body(...),
    project_id: Optional[int] = Query(None, description="可选：研究项目ID"),
    focus_type: Optional[str] = Query(None, description="可选：chapter/section/plan_key"),
    focus_value: Optional[str] = Query(None, description="可选：如 第三章、3.3、timeline"),
    db: Session = Depends(get_db)
):
    req = ChatRequest(
        user_message=user_message,
        session_id=session_id,
        project_id=project_id,
        material_id=material_id,
        focus_type=focus_type,
        focus_value=focus_value
    )
    return _run_chat_logic(req, db)