"""Versioned canonical data contracts shared by research and serving code."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "1.0.0"
SchemaVersion = Literal["1.0.0"]

FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
NonNegativeFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
UnitFloat = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
ConsistencyScore = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]
KeyCode = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9]{0,63}$")]
PseudonymousId = Annotated[
    str,
    Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]+$"),
]


class CanonicalModel(BaseModel):
    """Strict, immutable base for persisted or transmitted domain objects."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class EventType(str, Enum):
    KEYDOWN = "keydown"
    KEYUP = "keyup"


class QualityCode(str, Enum):
    AUTO_REPEAT_IGNORED = "auto_repeat_ignored"
    DUPLICATE_KEYDOWN = "duplicate_keydown"
    UNMATCHED_KEYUP = "unmatched_keyup"
    MISSING_KEYUP = "missing_keyup"
    LONG_PAUSE = "long_pause"


class QualitySeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    REJECT = "reject"


class KeystrokeEvent(CanonicalModel):
    """One browser timing event; intentionally excludes typed text values."""

    schema_version: SchemaVersion = SCHEMA_VERSION
    session_id: PseudonymousId
    code: KeyCode
    event_type: EventType
    timestamp_ms: NonNegativeFloat
    repeat: bool = False


class KeystrokeEventBatch(CanonicalModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    session_id: PseudonymousId
    events: tuple[KeystrokeEvent, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_batch(self) -> KeystrokeEventBatch:
        if any(event.session_id != self.session_id for event in self.events):
            raise ValueError("all events must belong to the batch session")

        timestamps = [event.timestamp_ms for event in self.events]
        if timestamps != sorted(timestamps):
            raise ValueError("events must be ordered by monotonic timestamp")
        return self


class QualityIssue(CanonicalModel):
    code: QualityCode
    severity: QualitySeverity
    event_index: int | None = Field(default=None, ge=0)
    key_code: KeyCode | None = None


class PauseMarker(CanonicalModel):
    after_key_index: int = Field(ge=0)
    duration_ms: NonNegativeFloat


class TimingSequence(CanonicalModel):
    """Paired timing data derived from an ordered event batch."""

    schema_version: SchemaVersion = SCHEMA_VERSION
    session_id: PseudonymousId
    key_codes: tuple[KeyCode, ...]
    keydown_timestamps_ms: tuple[NonNegativeFloat, ...]
    keyup_timestamps_ms: tuple[NonNegativeFloat, ...]
    hold_durations_ms: tuple[NonNegativeFloat, ...]
    keydown_to_keydown_ms: tuple[NonNegativeFloat, ...]
    keyup_to_keydown_ms: tuple[FiniteFloat, ...]
    pause_markers: tuple[PauseMarker, ...] = ()
    correction_indices: tuple[int, ...] = ()
    quality_issues: tuple[QualityIssue, ...] = ()
    valid_event_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_shapes(self) -> TimingSequence:
        key_count = len(self.key_codes)
        per_key_lengths = {
            len(self.keydown_timestamps_ms),
            len(self.keyup_timestamps_ms),
            len(self.hold_durations_ms),
        }
        if per_key_lengths != {key_count}:
            raise ValueError("per-key timing arrays must match key_codes")

        expected_interval_count = max(0, key_count - 1)
        if len(self.keydown_to_keydown_ms) != expected_interval_count:
            raise ValueError("keydown intervals must contain one value per transition")
        if len(self.keyup_to_keydown_ms) != expected_interval_count:
            raise ValueError("keyup-to-keydown intervals must contain one value per transition")
        if self.valid_event_count != key_count * 2:
            raise ValueError("valid_event_count must count paired keydown and keyup events")
        if any(index >= key_count for index in self.correction_indices):
            raise ValueError("correction index is outside the sequence")
        if any(marker.after_key_index >= max(0, key_count - 1) for marker in self.pause_markers):
            raise ValueError("pause marker is outside the sequence")
        return self


class FeatureWindow(CanonicalModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    feature_schema_version: str = Field(min_length=1, max_length=64)
    window_start_index: int = Field(ge=0)
    window_end_index: int = Field(gt=0)
    valid_event_count: int = Field(ge=0)
    feature_names: tuple[str, ...]
    values: tuple[FiniteFloat, ...]
    quality_issues: tuple[QualityIssue, ...] = ()
    rejected: bool = False
    rejection_reason: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_window(self) -> FeatureWindow:
        if self.window_end_index <= self.window_start_index:
            raise ValueError("window_end_index must be after window_start_index")
        if len(self.feature_names) != len(self.values):
            raise ValueError("feature_names and values must have equal length")
        if len(set(self.feature_names)) != len(self.feature_names):
            raise ValueError("feature_names must be unique")
        if self.rejected != (self.rejection_reason is not None):
            raise ValueError("rejected windows must have exactly one rejection reason")
        return self


class ArtifactMetadata(CanonicalModel):
    artifact_version: str = Field(min_length=1, max_length=64)
    model_id: str = Field(min_length=1, max_length=64)
    model_version: str = Field(min_length=1, max_length=64)
    preprocessing_version: str = Field(min_length=1, max_length=64)
    feature_schema_version: str = Field(min_length=1, max_length=64)
    training_seed: int = Field(ge=0, le=2**32 - 1)
    dataset_manifest_id: str = Field(min_length=1, max_length=128)
    created_at: datetime

    @model_validator(mode="after")
    def require_timezone(self) -> ArtifactMetadata:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        return self


class CalibrationReference(CanonicalModel):
    calibration_id: str = Field(min_length=1, max_length=128)
    method: str = Field(min_length=1, max_length=64)
    operational_threshold: ConsistencyScore
    target_far: UnitFloat | None = None


class EnrollmentTemplate(CanonicalModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    user_id: PseudonymousId
    artifact: ArtifactMetadata
    enrollment_windows: tuple[FeatureWindow, ...] = ()
    embedding_centroid: tuple[FiniteFloat, ...] = ()
    calibration: CalibrationReference

    @model_validator(mode="after")
    def require_enrollment_representation(self) -> EnrollmentTemplate:
        if not self.enrollment_windows and not self.embedding_centroid:
            raise ValueError("an enrollment template requires windows or an embedding centroid")
        if any(window.rejected for window in self.enrollment_windows):
            raise ValueError("rejected feature windows cannot be enrolled")
        return self


class ScoreState(str, Enum):
    WARMING_UP = "warming_up"
    NORMAL = "normal"
    WARNING = "warning"
    REAUTHENTICATION_REQUESTED = "reauthentication_requested"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_QUALITY_INPUT = "low_quality_input"
    SYSTEM_ERROR = "system_error"


class ScoreResult(CanonicalModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    model_id: str = Field(min_length=1, max_length=64)
    artifact_version: str = Field(min_length=1, max_length=64)
    evidence_window_size: int = Field(ge=0)
    raw_score: FiniteFloat | None = None
    consistency_score: ConsistencyScore | None = None
    smoothed_score: ConsistencyScore | None = None
    state: ScoreState
    operational_threshold: ConsistencyScore
    quality_issues: tuple[QualityIssue, ...] = ()

    @model_validator(mode="after")
    def validate_score_availability(self) -> ScoreResult:
        unavailable_states = {
            ScoreState.WARMING_UP,
            ScoreState.INSUFFICIENT_EVIDENCE,
            ScoreState.LOW_QUALITY_INPUT,
            ScoreState.SYSTEM_ERROR,
        }
        scores = (self.raw_score, self.consistency_score, self.smoothed_score)
        if self.state in unavailable_states and any(score is not None for score in scores):
            raise ValueError("non-scoring states cannot contain scores")
        if self.state not in unavailable_states and any(score is None for score in scores):
            raise ValueError("scoring states require raw, calibrated, and smoothed scores")
        return self
