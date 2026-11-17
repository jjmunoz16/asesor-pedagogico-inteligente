"""Modelos relacionales SQLModel alineados con docs/arquitectura/ARQUITECTURA_SISTEMA.md."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class ActivityType(str, Enum):
    LAB = "lab"
    EXAM = "exam"
    COLLOQUIUM = "colloquium"


class FileCategory(str, Enum):
    REPORT_PDF = "report_pdf"
    REPORT_DOCX = "report_docx"
    MARKDOWN = "markdown"
    SOURCE_CODE = "source_code"
    DATA_TABLE = "data_table"
    IMAGE_DIAGRAM = "image_diagram"
    VIDEO = "video"
    ARCHIVE = "archive"


class ExtractionStatus(str, Enum):
    EXTRACTED = "extracted"
    PARTIAL_METADATA_ONLY = "partial_metadata_only"
    UNSUPPORTED = "unsupported"


class EvaluationStatus(str, Enum):
    DRAFT_AI = "draft_ai"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ObjectiveStatus(str, Enum):
    CUMPLIDO = "cumplido"
    PARCIAL = "parcial"
    NO_CUMPLIDO = "no_cumplido"
    NO_VERIFICABLE = "no_verificable"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    full_name: str
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)


class Cohort(SQLModel, table=True):
    __tablename__ = "cohorts"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)  # C1, C2
    name: str
    order_index: int = Field(default=1)

    activities: list["Activity"] = Relationship(back_populates="cohort")


class Activity(SQLModel, table=True):
    __tablename__ = "activities"

    id: Optional[int] = Field(default=None, primary_key=True)
    cohort_id: int = Field(foreign_key="cohorts.id", index=True)
    slug: str = Field(index=True, unique=True)
    title: str
    activity_type: ActivityType = Field(default=ActivityType.LAB)
    official_objective: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    objective_source: Optional[str] = Field(default=None)
    description: str = Field(default="", sa_column=Column(Text))
    active_rubric_version_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)

    cohort: Optional[Cohort] = Relationship(back_populates="activities")
    submissions: list["Submission"] = Relationship(back_populates="activity")


class Rubric(SQLModel, table=True):
    __tablename__ = "rubrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id", index=True)
    name: str
    is_template_proposal: bool = Field(default=True)
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=utc_now)

    versions: list["RubricVersion"] = Relationship(back_populates="rubric")


class RubricVersion(SQLModel, table=True):
    __tablename__ = "rubric_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    rubric_id: int = Field(foreign_key="rubrics.id", index=True)
    version_number: int = Field(default=1)
    is_valid: bool = Field(default=False)
    notes: str = Field(default="")
    created_at: datetime = Field(default_factory=utc_now)

    rubric: Optional[Rubric] = Relationship(back_populates="versions")
    criteria: list["RubricCriterion"] = Relationship(back_populates="rubric_version")


class RubricCriterion(SQLModel, table=True):
    __tablename__ = "rubric_criteria"

    id: Optional[int] = Field(default=None, primary_key=True)
    rubric_version_id: int = Field(foreign_key="rubric_versions.id", index=True)
    code: str = Field(index=True)  # ej. CRIT-1
    competency_name: str
    criterion_name: str
    description: str = Field(sa_column=Column(Text))
    weight_percent: float
    performance_levels_json: str = Field(default="{}", sa_column=Column(Text))

    rubric_version: Optional[RubricVersion] = Relationship(back_populates="criteria")


class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id", index=True)
    student_group_name: str
    owner_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    repo_url: Optional[str] = Field(default=None)
    notes: str = Field(default="", sa_column=Column(Text))
    is_preloaded_portfolio: bool = Field(default=False)
    submitted_at: datetime = Field(default_factory=utc_now)

    activity: Optional[Activity] = Relationship(back_populates="submissions")
    evidence_files: list["EvidenceFile"] = Relationship(back_populates="submission")
    code_checks: list["CodeCheckResult"] = Relationship(back_populates="submission")
    evaluations: list["Evaluation"] = Relationship(back_populates="submission")


class EvidenceFile(SQLModel, table=True):
    __tablename__ = "evidence_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submissions.id", index=True)
    filename: str
    relative_path: str
    mime_type: str = Field(default="application/octet-stream")
    file_category: FileCategory = Field(default=FileCategory.ARCHIVE)
    size_bytes: int = Field(default=0)
    sha256_hash: str
    storage_uri: str = Field(default="")
    extracted_text_summary: str = Field(default="", sa_column=Column(Text))
    extraction_status: ExtractionStatus = Field(default=ExtractionStatus.PARTIAL_METADATA_ONLY)

    submission: Optional[Submission] = Relationship(back_populates="evidence_files")


class CodeCheckResult(SQLModel, table=True):
    __tablename__ = "code_check_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submissions.id", index=True)
    sandbox_mode: str = Field(default="static_only")
    syntax_valid: bool = Field(default=True)
    files_checked_json: str = Field(default="[]", sa_column=Column(Text))
    static_findings_json: str = Field(default="[]", sa_column=Column(Text))
    unit_tests_passed: Optional[int] = Field(default=None)
    unit_tests_total: Optional[int] = Field(default=None)
    execution_time_ms: int = Field(default=0)
    executed_at: datetime = Field(default_factory=utc_now)

    submission: Optional[Submission] = Relationship(back_populates="code_checks")


class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submissions.id", index=True)
    rubric_version_id: int = Field(foreign_key="rubric_versions.id", index=True)
    status: EvaluationStatus = Field(default=EvaluationStatus.DRAFT_AI)
    ai_provider: str
    ai_model: str
    prompt_version: str = Field(default="v1.0")
    objective_met: ObjectiveStatus = Field(default=ObjectiveStatus.NO_VERIFICABLE)
    verification_summary: str = Field(default="", sa_column=Column(Text))
    cited_evidences_json: str = Field(default="[]", sa_column=Column(Text))
    missing_items_json: str = Field(default="[]", sa_column=Column(Text))
    recommendations_json: str = Field(default="{}", sa_column=Column(Text))
    calculated_score_ai: float = Field(default=0.0)
    final_score_approved: Optional[float] = Field(default=None)
    raw_validated_payload_json: str = Field(default="{}", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=utc_now)

    submission: Optional[Submission] = Relationship(back_populates="evaluations")
    criterion_evaluations: list["CriterionEvaluation"] = Relationship(back_populates="evaluation")
    teacher_reviews: list["TeacherReview"] = Relationship(back_populates="evaluation")


class CriterionEvaluation(SQLModel, table=True):
    __tablename__ = "criterion_evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluations.id", index=True)
    rubric_criterion_id: int = Field(foreign_key="rubric_criteria.id", index=True)
    ai_level_label: str
    ai_criterion_score: float
    teacher_criterion_score: Optional[float] = Field(default=None)
    cited_evidences_json: str = Field(default="[]", sa_column=Column(Text))
    justification: str = Field(default="", sa_column=Column(Text))

    evaluation: Optional[Evaluation] = Relationship(back_populates="criterion_evaluations")


class TeacherReview(SQLModel, table=True):
    __tablename__ = "teacher_reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluations.id", index=True)
    teacher_id: int = Field(foreign_key="users.id")
    decision: str  # approved | adjusted | rejected
    comments: str = Field(default="", sa_column=Column(Text))
    score_diff_json: str = Field(default="{}", sa_column=Column(Text))
    reviewed_at: datetime = Field(default_factory=utc_now)

    evaluation: Optional[Evaluation] = Relationship(back_populates="teacher_reviews")


class TopicNode(SQLModel, table=True):
    __tablename__ = "topic_nodes"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_key: str = Field(index=True, unique=True)
    label: str
    category: str
    description: str = Field(default="", sa_column=Column(Text))
    mastery_level: str = Field(default="por_profundizar")
    mastery_score: float = Field(default=0.0)
    related_activity_slugs_json: str = Field(default="[]", sa_column=Column(Text))
    evidences_json: str = Field(default="[]", sa_column=Column(Text))
    gaps_to_strengthen_json: str = Field(default="[]", sa_column=Column(Text))
    pos_x: float = Field(default=0.0)
    pos_y: float = Field(default=0.0)


class TopicEdge(SQLModel, table=True):
    __tablename__ = "topic_edges"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_key: str = Field(index=True)
    target_key: str = Field(index=True)
    relation_label: str = Field(default="")


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    actor_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str
    entity_type: str
    entity_id: str
    metadata_json: str = Field(default="{}", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=utc_now)


class RuntimeAIConfig(SQLModel, table=True):
    """Configuración activa de proveedor IA (sin almacenar secretos/API keys en BD)."""

    __tablename__ = "runtime_ai_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    active_provider: str = Field(default="gemini")
    active_model: str = Field(default="gemini-2.5-flash")
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: datetime = Field(default_factory=utc_now)
