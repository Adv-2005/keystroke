from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from keystroke.schemas import (
    ArtifactMetadata,
    CalibrationReference,
    EnrollmentTemplate,
    FeatureWindow,
    KeystrokeEvent,
    KeystrokeEventBatch,
    ScoreResult,
    ScoreState,
)


def _feature_window() -> FeatureWindow:
    return FeatureWindow(
        feature_schema_version="classical-1",
        window_start_index=0,
        window_end_index=50,
        valid_event_count=100,
        feature_names=("hold_mean_ms", "overlap_rate"),
        values=(82.5, 0.12),
    )


def _artifact() -> ArtifactMetadata:
    return ArtifactMetadata(
        artifact_version="artifact-1",
        model_id="statistical-distance",
        model_version="1.0.0",
        preprocessing_version="1.0.0",
        feature_schema_version="classical-1",
        training_seed=731,
        dataset_manifest_id="synthetic-test-manifest",
        created_at=datetime(2026, 10, 8, tzinfo=UTC),
    )


def test_event_rejects_text_value_and_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="text"):
        KeystrokeEvent.model_validate(
            {
                "session_id": "session_0001",
                "code": "KeyA",
                "event_type": "keydown",
                "timestamp_ms": 12.5,
                "repeat": False,
                "text": "sensitive typed content",
            }
        )


def test_batch_rejects_mixed_sessions(synthetic_batch: KeystrokeEventBatch) -> None:
    payload = synthetic_batch.model_dump(mode="json")
    payload["events"][0]["session_id"] = "session_other_002"

    with pytest.raises(ValidationError, match="batch session"):
        KeystrokeEventBatch.model_validate(payload)


def test_batch_rejects_non_monotonic_timestamps(
    synthetic_batch: KeystrokeEventBatch,
) -> None:
    payload = synthetic_batch.model_dump(mode="json")
    payload["events"][1]["timestamp_ms"] = 50.0

    with pytest.raises(ValidationError, match="monotonic timestamp"):
        KeystrokeEventBatch.model_validate(payload)


def test_feature_template_and_score_contracts() -> None:
    feature_window = _feature_window()
    template = EnrollmentTemplate(
        user_id="subject_0001",
        artifact=_artifact(),
        enrollment_windows=(feature_window,),
        calibration=CalibrationReference(
            calibration_id="validation-calibration-1",
            method="validation-fitted-monotonic",
            operational_threshold=63.0,
            target_far=0.01,
        ),
    )
    score = ScoreResult(
        model_id=template.artifact.model_id,
        artifact_version=template.artifact.artifact_version,
        evidence_window_size=50,
        raw_score=-0.42,
        consistency_score=78.0,
        smoothed_score=74.5,
        state=ScoreState.NORMAL,
        operational_threshold=63.0,
    )

    assert template.enrollment_windows == (feature_window,)
    assert score.state is ScoreState.NORMAL


def test_non_scoring_state_rejects_numeric_scores() -> None:
    with pytest.raises(ValidationError, match="non-scoring states"):
        ScoreResult(
            model_id="statistical-distance",
            artifact_version="artifact-1",
            evidence_window_size=10,
            raw_score=0.5,
            consistency_score=None,
            smoothed_score=None,
            state=ScoreState.INSUFFICIENT_EVIDENCE,
            operational_threshold=63.0,
        )
