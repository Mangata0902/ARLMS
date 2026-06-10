import os
import fitz
import json
import uuid
import logging
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from openai import OpenAI

# --- RAG 依赖 ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.models.all_models import Material, SemanticTag, AIReadAnalytic

# 加载环境变量
load_dotenv()
logger = logging.getLogger(__name__)

# 1. 初始化本地 Embedding 模型
embeddings = HuggingFaceEmbeddings(model_name="./models")

# 2. 向量数据库存储根目录
CHROMA_DB_DIR = os.path.abspath(os.path.join("storage", "chroma_db"))
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# 3. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 提取全文（旧逻辑保留）"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF 提取失败: {str(e)}")
        return ""


def extract_pages_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    按页提取文本，为 metadata 提供 page 信息
    返回: [{"page": 1, "text": "..."}]
    """
    pages: List[Dict[str, Any]] = []
    try:
        doc = fitz.open(file_path)
        for i, page in enumerate(doc, start=1):
            txt = page.get_text() or ""
            txt = txt.strip()
            if txt:
                pages.append({"page": i, "text": txt})
        doc.close()
    except Exception as e:
        logger.error(f"按页提取失败: {str(e)}")
    return pages


def build_chunks_with_metadata(
    file_path: str,
    file_name: str,
    vector_collection_name: str,
    chunk_size: int = 600,
    chunk_overlap: int = 100
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    产出 texts + metadatas（一一对应）
    metadata 含 page/chunk_id/source/file_name/collection 等
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    pages = extract_pages_from_pdf(file_path)

    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    global_chunk_idx = 0
    for p in pages:
        page_no = p["page"]
        page_text = p["text"]

        page_chunks = text_splitter.split_text(page_text)
        for local_idx, chunk in enumerate(page_chunks, start=1):
            chunk = (chunk or "").strip()
            if not chunk:
                continue

            global_chunk_idx += 1
            chunk_id = f"{vector_collection_name}_p{page_no}_c{local_idx}"

            texts.append(chunk)
            metadatas.append({
                "source": file_path,               # 原始文件路径
                "file_name": file_name,            # 文件名
                "page": page_no,                   # 页码
                "chunk_id": chunk_id,              # 全局唯一 chunk id
                "chunk_index": global_chunk_idx,   # 全文顺序
                "collection": vector_collection_name
            })

    return texts, metadatas


async def run_ingestion_pipeline(
    file_path: str,
    file_name: str,
    user_requirement: str,
    mode: str,
    db: Session
):
    """
    核心封装逻辑：支持『诊断』与『导读』双模式 + RAG 向量入库（含 metadata）
    """
    # --- A. 提取全文（用于 AI 诊断/导读）---
    raw_text = extract_text_from_pdf(file_path)
    if not raw_text:
        raise Exception("无法从 PDF 中提取有效文字内容。")

    # --- B. RAG 核心逻辑：切片与向量化 ---
    vector_collection_name = f"doc_{uuid.uuid4().hex[:12]}"

    # 新：按页切片并附加 metadata
    texts, metadatas = build_chunks_with_metadata(
        file_path=file_path,
        file_name=file_name,
        vector_collection_name=vector_collection_name,
        chunk_size=600,
        chunk_overlap=100
    )

    # 兜底：万一按页失败，则降级到全文切片（仍写基础 metadata）
    if not texts:
        logger.warning("按页切片为空，降级到全文切片")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        chunks = text_splitter.split_text(raw_text)
        texts = []
        metadatas = []
        for i, c in enumerate(chunks, start=1):
            c = (c or "").strip()
            if not c:
                continue
            texts.append(c)
            metadatas.append({
                "source": file_path,
                "file_name": file_name,
                "page": None,
                "chunk_id": f"{vector_collection_name}_c{i}",
                "chunk_index": i,
                "collection": vector_collection_name
            })

    if not texts:
        raise Exception("切片失败：没有可入库的文本块。")

    # 创建向量存储（含 metadatas）
    Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name=vector_collection_name
    )

    # --- C. AI 诊断/导读逻辑 ---
    if mode == "diagnostic":
        system_role = "你是一个严厉且专业的学术论文评审专家。请针对学生提交的论文草稿进行深度诊断。"
        prompt_content = f"""
# Role
你现在是学术导师，正在评审学生的论文草稿。你需要指出逻辑漏洞、学术规范问题，并给出具体的分数。

# Mission
1. 评估论文的学术价值和逻辑严密性。
2. 给出 0-100 的综合评分。
3. 提供具体的修改意见。

# User Requirement
学生特别关注：{user_requirement if user_requirement else "请进行全面论文诊断"}
"""
    else:
        system_role = "你是一个博学且耐心的学术导师。请始终以 JSON 格式回答。"
        prompt_content = f"""
# Role
你是一个拥有顶级学术背景的“金牌导师”。你不仅能洞察论文最深层的逻辑，还能用直观易懂的语言把复杂概念讲清楚。

# User Requirement
用户特定要求：{user_requirement if user_requirement else "请进行深度文献导读"}
"""

    full_prompt = f"""{prompt_content}

# Output Format (强制使用以下 JSON 结构)
{{
  "title": "论文/书籍标题",
  "author": "作者信息",
  "summary": "300字以内核心摘要",
  "tags": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "methodology": "一句话总结研究方法",
  "mermaid_mindmap": "Mermaid 格式思维导图源码",
  "ai_score": 85,
  "recommendation": "具体的修改建议或深度阅读建议"
}}

待分析文本内容：
{raw_text[:30000]}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": full_prompt}
        ],
        response_format={"type": "json_object"}
    )

    ai_data = json.loads(response.choices[0].message.content)

    # --- D. 写入数据库 ---
    new_material = Material(
        title=ai_data.get("title", file_name),
        author=ai_data.get("author", "未知"),
        abstract_summary=ai_data.get("summary", ""),
        file_path=file_path,
        is_local=True,
        material_type="PDF Document",
        vector_index=vector_collection_name
    )
    db.add(new_material)
    db.flush()

    for tag_name in ai_data.get("tags", []):
        tag = SemanticTag(
            material_id=new_material.material_id,
            tag_name=tag_name,
            tag_type="AI_Generated",
            confidence=0.95
        )
        db.add(tag)

    analytic = AIReadAnalytic(
        material_id=new_material.material_id,
        user_id=1,
        mermaid_code=ai_data.get("mermaid_mindmap", ""),
        methodology_feat=ai_data.get("methodology", ""),
        knowledge_points=",".join(ai_data.get("tags", [])),
        ai_score=ai_data.get("ai_score"),
        recommendation=ai_data.get("recommendation", "建议深度阅读此文档")
    )
    db.add(analytic)

    db.commit()
    return new_material.material_id
