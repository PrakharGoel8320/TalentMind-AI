from app.repositories.base import CRUDBase
from app.models.user import User
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.job import Job
from app.models.pipeline_entry import PipelineEntry
from app.models.audit_log import AuditLog
from app.models.feedback import RecruiterFeedback
from app.models.prediction import Prediction
from app.models.dataset_version import DatasetVersion
from app.models.model_version import ModelVersion


class UserRepository(CRUDBase[User, dict, dict]):
    pass


class CandidateRepository(CRUDBase[Candidate, dict, dict]):
    pass


class ResumeRepository(CRUDBase[Resume, dict, dict]):
    pass


class JobRepository(CRUDBase[Job, dict, dict]):
    pass


class PipelineEntryRepository(CRUDBase[PipelineEntry, dict, dict]):
    pass


class AuditLogRepository(CRUDBase[AuditLog, dict, dict]):
    pass


class FeedbackRepository(CRUDBase[RecruiterFeedback, dict, dict]):
    pass


class PredictionRepository(CRUDBase[Prediction, dict, dict]):
    pass


class DatasetVersionRepository(CRUDBase[DatasetVersion, dict, dict]):
    pass


class ModelVersionRepository(CRUDBase[ModelVersion, dict, dict]):
    pass


# Singleton instances
user_repo = UserRepository(User)
candidate_repo = CandidateRepository(Candidate)
resume_repo = ResumeRepository(Resume)
job_repo = JobRepository(Job)
pipeline_entry_repo = PipelineEntryRepository(PipelineEntry)
audit_log_repo = AuditLogRepository(AuditLog)
feedback_repo = FeedbackRepository(RecruiterFeedback)
prediction_repo = PredictionRepository(Prediction)
dataset_version_repo = DatasetVersionRepository(DatasetVersion)
model_version_repo = ModelVersionRepository(ModelVersion)
