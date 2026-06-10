import os
import json
import httpx
import fitz                          # pymupdf，解析 PDF
from docx import Document            # python-docx，解析 Word
from io import BytesIO
from sqlalchemy.orm import Session
from app.models.all_models import AIDetectionRecord
from dotenv import load_dotenv

load_dotenv()

# ========== DeepSeek API 配置（从 .env 读取）==========
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL   = "deepseek-chat"

# 每次送给 DeepSeek 检测的最大字符数（避免超出 token 限制）
MAX_CHARS_PER_CHUNK = 3000
# 最多取前几个分块进行检测（论文太长时取前段+中段+后段）
MAX_CHUNKS = 3


# ========== 文件解析：提取纯文本 ==========
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 字节流中提取全部文本"""
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """从 Word(.docx) 字节流中提取全部文本"""
    doc = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    """根据文件名后缀自动选择解析方式"""
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".doc"):
        # .doc 是旧格式，python-docx 不支持，尝试当纯文本读
        try:
            return file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            raise ValueError("不支持 .doc 旧格式，请将文件另存为 .docx 后重新上传")
    elif name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError(f"不支持的文件格式：{filename}，请上传 PDF、DOCX 或 TXT 文件")


# ========== 文本分块（论文太长时分段检测）==========
def split_text_into_chunks(text: str, chunk_size: int = MAX_CHARS_PER_CHUNK) -> list[str]:
    """将长文本按字符数切分成若干块"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def sample_chunks(chunks: list[str], max_chunks: int = MAX_CHUNKS) -> list[str]:
    """
    从所有分块中采样：取开头、中间、结尾，
    保证对论文整体有代表性。
    """
    if len(chunks) <= max_chunks:
        return chunks
    indices = [0, len(chunks) // 2, len(chunks) - 1]
    return [chunks[i] for i in indices]


# ========== 单块检测 ==========
def detect_single_chunk(text: str) -> dict:
    """对单个文本块调用 DeepSeek API 进行检测并获取降重建议"""
    if not DEEPSEEK_API_KEY:
        raise ValueError("未配置 DEEPSEEK_API_KEY，请检查 .env 文件")

    # 升级后的 Prompt：要求它给出检测结果 + 降重建议
    prompt = f"""你是一个专业的学术论文审查与润色专家。请分析以下文本片段，判断其AI生成概率，并给出具体的降重（去AI化）建议。

待检测文本：
{text}

请严格按以下JSON格式返回，不要有任何多余文字：
{{
  "ai_score": 0.85, 
  "reasoning": "简述为什么像AI（50字以内）",
  "conclusion": "风险等级结论",
  "rewrite_suggestions": [
    {{
      "original": "文中像AI的原始句子1",
      "suggestion": "修改建议：为什么要改，怎么改",
      "revised_version": "参考改写后的句子（更具人类表达习惯）"
    }},
    {{
      "original": "文中像AI的原始句子2",
      "suggestion": "修改建议...",
      "revised_version": "参考改写..."
    }}
  ],
  "overall_advice": "针对整段话的去AI化总体建议（如：增加个人观点、改变句式结构等）"
}}"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # 稍微提高一点温度，让改写建议更自然
        "max_tokens": 1000   # 建议内容较多，增加 token 限制
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
            response.raise_for_status()

        data = response.json()
        raw_content = data["choices"][0]["message"]["content"].strip()

        # 清理 markdown 代码块
        if raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:]

        result = json.loads(raw_content)
        result["ai_score"] = max(0.0, min(1.0, float(result["ai_score"])))
        return result

    except Exception as e:
        # 如果解析失败或报错，返回一个基础结构，保证程序不崩溃
        return {
            "ai_score": 0.5,
            "reasoning": f"检测异常: {str(e)}",
            "conclusion": "未知",
            "rewrite_suggestions": [],
            "overall_advice": "无法生成建议"
        }


# ========== 论文整体检测（多块聚合）==========
def detect_ai_content(file_bytes: bytes, filename: str) -> dict:
    """
    完整论文检测入口：
    1. 提取文本
    2. 分块采样
    3. 逐块调用 DeepSeek
    4. 聚合结果，返回综合评分
    """
    # 1. 提取文本
    full_text = extract_text(file_bytes, filename)
    if len(full_text) < 100:
        raise ValueError("文件内容过少（不足100字），无法进行有效检测")

    # 2. 分块采样
    all_chunks  = split_text_into_chunks(full_text)
    sampled     = sample_chunks(all_chunks)

    # 3. 逐块检测
    chunk_results = []
    for chunk in sampled:
        res = detect_single_chunk(chunk)
        chunk_results.append(res)

    # 4. 聚合：取平均分，合并理由
    avg_score  = sum(r["ai_score"] for r in chunk_results) / len(chunk_results)
    reasonings = "；".join(r.get("reasoning", "") for r in chunk_results)
    conclusion = chunk_results[-1].get("conclusion", "")  # 取最后一块的结论

    return {
        "ai_score":      round(avg_score, 4),
        "reasoning":     reasonings,
        "conclusion":    conclusion,
        "chunks_checked": len(sampled),
        "total_chunks":   len(all_chunks),
        "total_chars":    len(full_text),
        "chunk_details":  chunk_results   # 每块的详细结果
    }


# ========== 保存检测记录 ==========
def save_detection_record(
    db: Session,
    user_id: int,
    original_text: str,
    ai_score: float,
    result_detail: dict
) -> AIDetectionRecord:
    record = AIDetectionRecord(
        user_id=user_id,
        original_text=original_text,
        ai_score=ai_score,
        result_detail=result_detail
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ========== 查询用户历史记录 ==========
def get_user_detection_history(db: Session, user_id: int, limit: int = 20) -> list:
    return (
        db.query(AIDetectionRecord)
        .filter(AIDetectionRecord.user_id == user_id)
        .order_by(AIDetectionRecord.created_at.desc())
        .limit(limit)
        .all()
    )
