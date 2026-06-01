import json
import subprocess
import sys
from pathlib import Path
from app.core.config import get_settings


class WestMonthSkillAdapter:
    name = "westmonth-catalog-analyzer"

    def match(self, query: str) -> dict:
        settings = get_settings()
        tool = Path(settings.skill_catalog_tool_path)
        if not tool.exists():
            return self._fallback(query, "Skill 脚本未找到，已使用保守本地匹配占位。")

        try:
            proc = subprocess.run(
                [sys.executable, str(tool), "match", "--query", query],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
            if proc.returncode != 0:
                return self._fallback(query, proc.stderr.strip() or "Skill 返回非零状态。")
            return {"raw": proc.stdout, "catalog_match_score": 72, "confidence": "medium"}
        except Exception as exc:  # pragma: no cover - protective integration boundary
            return self._fallback(query, str(exc))

    def _fallback(self, query: str, reason: str) -> dict:
        score = 80 if any(token in query.lower() for token in ["clean", "brush", "car", "organizer"]) else 55
        return {
            "raw": reason,
            "catalog_match_score": score,
            "confidence": "low",
            "suggested_sku": None,
        }
