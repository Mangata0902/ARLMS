import os
import json
import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter()
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ===== 模式配置 =====
MODE_PROMPTS = {
    "polish": """
你是一位专业的学术论文润色专家。
【任务】：对用户提供的论文段落进行语言润色。
【要求】：
1. 提升表达的流畅性、准确性与学术规范性
2. 严格保留原文的核心观点和数据，不得增删论点
3. 修正不通顺、口语化、重复啰嗦的表达
4. 直接输出润色后的完整文本，不需要解释修改原因
""",
    "reduce": """
你是一位专业的论文降重改写专家。
【任务】：对用户提供的论文段落进行同义改写，降低文字重复率。
【要求】：
1. 使用同义词替换、句式重组、主被动转换等方式改写
2. 保持原文的逻辑结构和核心含义不变
3. 改写后的文本应自然流畅，不得出现语义扭曲
4. 直接输出改写后的完整文本，不需要解释
""",
    "structure": """
你是一位资深学术论文结构优化专家。
【任务】：分析用户提供的论文内容，给出结构优化建议并提供修改版本。
【要求】：
1. 首先简要分析当前结构存在的问题（不超过5条）
2. 然后输出优化后的完整版本
3. 重点关注：段落逻辑顺序、论点论据对应关系、过渡句的使用
4. 格式：先输出【结构分析】，再输出【优化后全文】
""",
    "grammar": """
你是一位专业的学术写作语法检查专家。
【任务】：对用户提供的论文段落进行语法检查与修正。
【要求】：
1. 检查并修正语法错误、标点使用不规范、用词不当等问题
2. 对中文论文：重点检查句子成分缺失、标点符号滥用、中英文混排规范
3. 对英文论文：重点检查时态一致性、冠词使用、从句结构
4. 格式：先输出【问题列表】（逐条列出），再输出【修正后全文】
"""
}

STYLE_HINTS = {
    "academic":          "写作风格要求：严格遵循学术论文规范，用词正式，避免口语化表达。",
    "concise":           "写作风格要求：简洁清晰，逻辑紧凑，适合会议论文的表达方式。",
    "native_chinese":    "写作风格要求：符合中文母语者的表达习惯，自然流畅，避免翻译腔。",
    "english_academic":  "写作风格要求：使用标准英文学术表达，符合 SCI/SSCI 期刊写作规范。"
}


class RevisionRequest(BaseModel):
    content: str                          # 原文内容
    mode: str = "polish"                  # polish / reduce / structure / grammar
    style: str = "academic"               # 写作风格
    extra: Optional[str] = None           # 额外要求


@router.post("/revision/stream")
async def revision_stream(req: RevisionRequest):
    """
    论文修改流式接口
    - 不走 RAG 检索，专注于文本改写
    - 使用独立的 system prompt，与 chat.py 完全隔离
    """
    mode_prompt = MODE_PROMPTS.get(req.mode, MODE_PROMPTS["polish"])
    style_hint  = STYLE_HINTS.get(req.style, STYLE_HINTS["academic"])

    extra_hint = ""
    if req.extra and req.extra.strip():
        extra_hint = f"\n【用户额外要求】：{req.extra.strip()}"

    system_prompt = f"""
{mode_prompt}
{style_hint}
{extra_hint}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": f"请对以下内容进行修改：\n\n{req.content}"}
    ]

    def event_generator():
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            for chunk in stream:
                delta = ""
                try:
                    delta = chunk.choices[0].delta.content or ""
                except Exception:
                    delta = ""

                if delta:
                    yield f"data: {json.dumps({'content': delta}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"论文修改流式调用失败: {e}")
            yield f"data: {json.dumps({'error': 'AI 服务暂时不可用，请稍后重试'}, ensure_ascii=False)}\n\n"
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


@router.post("/revision")
async def revision_sync(req: RevisionRequest):
    """
    论文修改同步接口（非流式，备用）
    """
    mode_prompt = MODE_PROMPTS.get(req.mode, MODE_PROMPTS["polish"])
    style_hint  = STYLE_HINTS.get(req.style, STYLE_HINTS["academic"])

    extra_hint = ""
    if req.extra and req.extra.strip():
        extra_hint = f"\n【用户额外要求】：{req.extra.strip()}"

    system_prompt = f"{mode_prompt}\n{style_hint}{extra_hint}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": f"请对以下内容进行修改：\n\n{req.content}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        result = response.choices[0].message.content or ""
        return {"result": result, "mode": req.mode, "style": req.style}
    except Exception as e:
        logger.error(f"论文修改同步调用失败: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="AI 服务暂时不可用")