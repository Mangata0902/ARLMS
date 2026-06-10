import json
import re
from typing import Optional, Dict, Any

# 约定：AI 在回复中输出如下代码块
# ```json
# {"evolution": {...}}
# ```

JSON_BLOCK_RE = re.compile(r"```json\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)

def parse_evolution_block(text: str) -> Optional[Dict[str, Any]]:
    """
    从 AI 回复中提取 evolution JSON。
    返回:
      {"should_update": bool, "reason": str, "changes": {...}}
    或 None
    """
    if not text:
        return None

    # 1) 优先取 ```json ... ```
    m = JSON_BLOCK_RE.search(text)
    candidate = None
    if m:
        candidate = m.group(1)
    else:
        # 2) 兜底：尝试全文就是 JSON
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
