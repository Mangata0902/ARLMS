import os
import json
import re
import logging
from typing import Dict, Any
from fastapi import HTTPException
from openai import OpenAI

# 1. 初始化日志
logger = logging.getLogger(__name__)

# 2. DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def generate_research_plan_logic(major: str, topic: str) -> Dict[str, Any]:
    """
    根据专业和课题，调用 DeepSeek 生成论文大纲、研究计划和文献推荐。
    说明：此版本不依赖数据库文献内容，只基于 major + topic 生成。
    """

    major = (major or "").strip()
    topic = (topic or "").strip()

    if not major:
        raise HTTPException(status_code=400, detail="major 不能为空")
    if not topic:
        raise HTTPException(status_code=400, detail="topic 不能为空")

    # 系统角色
    system_role = (
        f"你是一位精通{major}领域的资深学术导师。"
        "你擅长为学生制定严谨、可执行、具有创新性的科研计划，"
        "并能推荐该领域经典与前沿文献。"
    )

    # 用户提示词（强约束 JSON）
    user_prompt = f"""
# 任务
请针对课题《{topic}》生成完整的学术研究计划。

# 输出要求
1. 必须严格输出 JSON，不要输出任何解释性文字。
2. JSON 顶层必须包含以下字段：
   - outline: 数组（至少5章；每章含 chapter, title, sections）
   - research_plan: 对象（包含 background, objectives, methods, timeline, expected_innovations, risks_and_alternatives）
   - recommended_refs: 数组（5篇；每篇含 title, author, year, reason）

# 细节要求
- outline.sections 至少 3 个子点。
- objectives 为 3-5 条可执行目标。
- timeline 至少覆盖 12 周，按“第X周：...”格式输出。
- recommended_refs 尽量给出真实、常见、可检索的论文信息。

# JSON 示例结构
{{
  "outline": [
    {{
      "chapter": "第一章",
      "title": "绪论",
      "sections": ["1.1 研究背景", "1.2 研究意义", "1.3 研究问题定义"]
    }}
  ],
  "research_plan": {{
    "background": "...",
    "objectives": ["...", "...", "..."],
    "methods": "...",
    "timeline": ["第1周：...", "第2周：..."],
    "expected_innovations": ["...", "..."],
    "risks_and_alternatives": ["风险A：...；备选方案：..."]
  }},
  "recommended_refs": [
    {{
      "title": "...",
      "author": "...",
      "year": "2023",
      "reason": "..."
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content or ""
        json_str = _extract_json_content(raw_content)
        parsed_data = json.loads(json_str)

        # 结构兜底，避免前端取字段时报错
        parsed_data = _normalize_plan_json(parsed_data)

        return parsed_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 返回内容不是有效 JSON，请稍后重试")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成研究计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 生成研究计划失败: {str(e)}")


def _extract_json_content(text: str) -> str:
    """
    从 AI 回复中提取 JSON 字符串并清洗。
    """
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def _normalize_plan_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    对 AI 返回结构做最小兜底，保证接口稳定。
    """
    if not isinstance(data, dict):
        data = {}

    data.setdefault("outline", [])
    data.setdefault("research_plan", {})
    data.setdefault("recommended_refs", [])

    if not isinstance(data["outline"], list):
        data["outline"] = []
    if not isinstance(data["recommended_refs"], list):
        data["recommended_refs"] = []

    rp = data["research_plan"]
    if not isinstance(rp, dict):
        rp = {}

    rp.setdefault("background", "")
    rp.setdefault("objectives", [])
    rp.setdefault("methods", "")
    rp.setdefault("timeline", [])
    rp.setdefault("expected_innovations", [])
    rp.setdefault("risks_and_alternatives", [])

    if not isinstance(rp["objectives"], list):
        rp["objectives"] = []
    if not isinstance(rp["timeline"], list):
        rp["timeline"] = []
    if not isinstance(rp["expected_innovations"], list):
        rp["expected_innovations"] = []
    if not isinstance(rp["risks_and_alternatives"], list):
        rp["risks_and_alternatives"] = []

    data["research_plan"] = rp
    return data
