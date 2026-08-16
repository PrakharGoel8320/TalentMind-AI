import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

COMMON_SKILLS = {
    "python", "java", "kubernetes", "react", "fastapi", "sql", "machine learning",
    "docker", "aws", "gcp", "node.js", "c++", "go", "javascript", "typescript",
    "rust", "azure", "linux", "git", "ci/cd", "agile", "scrum", "tensorflow",
    "pytorch", "nlp", "graphql", "rest api", "nosql", "mongodb", "postgresql",
    "mysql", "redis", "kafka", "rabbitmq"
}

class FeatureExtractionService:
    """
    Extracts structural features like skill matching and experience scoring 
    from the candidate profiles prior to semantic ranking.
    """
    
    def extract_features(self, candidates: List[Dict[str, Any]], job_description_text: str) -> List[Dict[str, Any]]:
        """
        Parses skills and experience, generating structural sub-scores deterministically.
        """
        jd_lower = job_description_text.lower()
        # Simple extraction: check if skill is in JD text
        jd_skills = {skill for skill in COMMON_SKILLS if skill in jd_lower}
        
        for cand in candidates:
            profile = cand.get("profile", {})
            cand_skills_raw = profile.get("skills", [])
            
            # Ensure skills are extracted as strings
            cand_skills = []
            for s in cand_skills_raw:
                if isinstance(s, dict):
                    cand_skills.append(s.get("name", "").lower())
                elif isinstance(s, str):
                    cand_skills.append(s.lower())
            
            cand_skills_set = set(cand_skills)
            
            matched_skills = []
            missing_skills = []
            
            # Calculate match based on recognized JD skills
            if jd_skills:
                for req_skill in jd_skills:
                    if any(req_skill in c_skill for c_skill in cand_skills_set):
                        matched_skills.append(req_skill)
                    else:
                        missing_skills.append(req_skill)
                
                match_ratio = len(matched_skills) / len(jd_skills)
                skill_match_score = match_ratio * 100.0
            else:
                # Fallback if JD has no recognizable skills
                skill_match_score = 50.0
                
            cand["skill_match_score"] = skill_match_score
            cand["matched_skills"] = matched_skills
            cand["missing_skills"] = missing_skills
            
            # Experience Score Calculation
            exp_data = profile.get("experience", [])
            if exp_data and isinstance(exp_data, list):
                # 20 points per role, cap at 100
                cand["experience_score"] = min(len(exp_data) * 20.0, 100.0)
            else:
                # Fallback for missing experience
                cand["experience_score"] = 0.0
                
        return candidates
