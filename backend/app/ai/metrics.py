import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Singleton"""
    _instance = None

    def __init__(self):
        if MetricsCollector._instance is not None:
            raise Exception("Singleton")
        self.metrics: List[Dict] = []
        MetricsCollector._instance = self

    @classmethod
    def get_instance(cls) -> "MetricsCollector":
        if cls._instance is None:
            cls()
        return cls._instance

    def record_pipeline_run(
        self,
        run_id: str,
        total_time_ms: float,
        phase_timings: Dict[str, float],
        candidate_count: int,
    ) -> None:
        record = {
            "run_id": run_id,
            "total_time_ms": total_time_ms,
            "phase_timings": phase_timings,
            "candidate_count": candidate_count,
        }
        self.metrics.append(record)
        logger.info("Metrics Recorded for Run %s: %s", run_id, f"{total_time_ms:.2f}ms total.")

    def get_summary(self) -> Dict:
        if not self.metrics:
            return {"total_runs": 0, "avg_total_ms": 0.0}
        avg_total = sum(m["total_time_ms"] for m in self.metrics) / len(self.metrics)
        return {
            "total_runs": len(self.metrics),
            "avg_total_ms": avg_total,
        }
