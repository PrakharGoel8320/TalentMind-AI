import enum

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

class PipelineStage(str, enum.Enum):
    SOURCED = "SOURCED"
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"

class ActionStatus(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXECUTED = "EXECUTED"

class ActionType(str, enum.Enum):
    EMAIL_CANDIDATE = "EMAIL_CANDIDATE"
