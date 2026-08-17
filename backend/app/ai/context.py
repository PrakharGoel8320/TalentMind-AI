import time
import uuid
from typing import Dict, Any, List


class PipelineContext:
    def __init__(self, job_description_id: str, job_description_text: str):
        self.run_id = str(uuid.uuid4())
        self.job_description_id = job_description_id
        self.job_description_text = job_description_text
        self.retrieved_candidates: List[Dict[str, Any]] = []
        self.scored_candidates: List[Dict[str, Any]] = []
        self.final_candidates: List[Dict[str, Any]] = []
        self.start_time = time.perf_counter()
        self.phase_timings: Dict[str, float] = {}
        self.errors: List[str] = []
        self.flags: List[str] = []

    def record_phase(self, phase_name: str, duration_ms: float) -> None:
        self.phase_timings[phase_name] = duration_ms

    def add_error(self, error_msg: str) -> None:
        self.errors.append(error_msg)

    def get_total_duration_ms(self) -> float:
        return (time.perf_counter() - self.start_time) * 1000
