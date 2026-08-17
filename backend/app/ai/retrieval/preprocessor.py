import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CandidatePreprocessor:
    @staticmethod
    def flatten_candidate(record: dict) -> str:
        try:
            profile = record.get("profile", {})
            title = profile.get("current_title", "")
            summary = profile.get("summary", "")
            skills = profile.get("skills", [])
            skills_str = ", ".join([s.get("name", s) if isinstance(s, dict) else str(s) for s in skills])
            experience = profile.get("career_history", [])
            exp_str_parts = []
            for role in experience:
                role_title = role.get("title", "")
                role_desc = role.get("description", "")
                exp_str_parts.append(f"{role_title}: {role_desc}")
            exp_str = " | ".join(exp_str_parts)
            text = f"Title: {title}. Skills: {skills_str}. Summary: {summary}. Experience: {exp_str}."
            return text.strip()
        except Exception as e:
            logger.error("Error flattening candidate: %s", e)
            return ""


class JDPreprocessor:
    @staticmethod
    def flatten_jd(jd_text: str) -> str:
        # Simple whitespace normalization
        cleaned = " ".join(jd_text.split())
        return cleaned
