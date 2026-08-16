import csv
import logging
from typing import List, Dict, Any
from io import StringIO

from app.ai.fusion.engine import FusionEngine
from app.ai.fusion.config import config

logger = logging.getLogger(__name__)

class FusionService:
    """
    Service layer for final ranking fusion.
    Handles duplicate detection, tie breaking, top-k selection, and export.
    """
    
    def __init__(self):
        self.engine = FusionEngine()
        self.top_k = config.engine.get("top_k_selection", 100)
        
    def _deduplicate_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicates based on candidate_id."""
        seen = set()
        deduped = []
        for cand in candidates:
            c_id = cand.get("candidate_id")
            if c_id not in seen:
                seen.add(c_id)
                deduped.append(cand)
        return deduped

    def rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fuses scores for all candidates, deduplicates, breaks ties, and returns Top-K.
        """
        if not candidates:
            return []
            
        deduped = self._deduplicate_candidates(candidates)
        
        for cand in deduped:
            # Extract scores (assuming they've been appended by upstream services)
            # NOTE: RankingService (cross-encoder) stores its score as "semantic_score".
            # We map it here to "cross_encoder_score" for the FusionEngine.
            scores = {
                "cross_encoder_score": cand.get("cross_encoder_score", cand.get("semantic_score", 0.0)),
                "embedding_score": cand.get("embedding_score", 0.0),
                "skill_match_score": cand.get("skill_match_score", 0.0),
                "experience_score": cand.get("experience_score", 0.0),
                "behavior_score": cand.get("behavioral_score", 0.0)  # Map from behavioral engine output
            }
            # Store normalized cross_encoder_score on candidate for downstream use and Match persistence
            cand["cross_encoder_score"] = scores["cross_encoder_score"]
            
            final_score, confidence, flags = self.engine.fuse_scores(cand, scores)
            
            cand["final_score"] = final_score
            cand["fusion_confidence"] = confidence
            cand["flags"] = flags
            
        # Sort candidates
        # Primary: final_score (DESC)
        # Tie Breaker 1: cross_encoder_score (DESC)
        # Tie Breaker 2: experience_score (DESC)
        sorted_candidates = sorted(
            deduped,
            key=lambda x: (
                x.get("final_score", 0.0), 
                x.get("cross_encoder_score", 0.0),
                x.get("experience_score", 0.0)
            ),
            reverse=True
        )
        
        # Select Top-K
        return sorted_candidates[:self.top_k]

    def export_to_csv(self, candidates: List[Dict[str, Any]]) -> str:
        """
        Exports the ranked candidate list to a CSV string.
        """
        if not candidates:
            return ""
            
        output = StringIO()
        fieldnames = [
            "candidate_id", "final_score", "cross_encoder_score", 
            "embedding_score", "skill_match_score", "experience_score", 
            "behavioral_score", "fusion_confidence", "flags"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for cand in candidates:
            row = {
                "candidate_id": cand.get("candidate_id", ""),
                "final_score": cand.get("final_score", ""),
                "cross_encoder_score": cand.get("cross_encoder_score", ""),
                "embedding_score": cand.get("embedding_score", ""),
                "skill_match_score": cand.get("skill_match_score", ""),
                "experience_score": cand.get("experience_score", ""),
                "behavioral_score": cand.get("behavioral_score", ""),
                "fusion_confidence": cand.get("fusion_confidence", ""),
                "flags": "|".join(cand.get("flags", []))
            }
            writer.writerow(row)
            
        return output.getvalue()
        
    def generate_eval_metrics(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates summary statistics for the ranking run.
        """
        if not candidates:
            return {}
            
        scores = [c.get("final_score", 0) for c in candidates]
        avg_score = sum(scores) / len(scores)
        
        flagged = [c for c in candidates if len(c.get("flags", [])) > 0]
        
        return {
            "total_ranked": len(candidates),
            "average_score": round(avg_score, 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "flagged_candidates": len(flagged)
        }
