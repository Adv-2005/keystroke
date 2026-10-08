from __future__ import annotations

from keystroke.schemas import (
    KeystrokeEvent,
    KeystrokeEventBatch,
    QualityCode,
)
from keystroke.sequence import events_to_timing_sequence


def test_synthetic_batch_converts_to_canonical_sequence(synthetic_batch) -> None:
    sequence = events_to_timing_sequence(
        synthetic_batch,
        pause_threshold_ms=1000.0,
    )

    assert sequence.key_codes == ("KeyA", "KeyB", "Backspace")
    assert sequence.hold_durations_ms == (60.0, 70.0, 70.0)
    assert sequence.keydown_to_keydown_ms == (40.0, 1260.0)
    assert sequence.keyup_to_keydown_ms == (-20.0, 1190.0)
    assert sequence.correction_indices == (2,)
    assert sequence.valid_event_count == 6
    assert sequence.pause_markers[0].after_key_index == 1
    assert sequence.pause_markers[0].duration_ms == 1260.0
    assert QualityCode.LONG_PAUSE in {issue.code for issue in sequence.quality_issues}


def test_repeat_and_malformed_pairs_are_flagged_not_fabricated() -> None:
    session_id = "session_quality_001"
    batch = KeystrokeEventBatch(
        session_id=session_id,
        events=(
            KeystrokeEvent(
                session_id=session_id,
                code="KeyA",
                event_type="keydown",
                timestamp_ms=10,
                repeat=False,
            ),
            KeystrokeEvent(
                session_id=session_id,
                code="KeyA",
                event_type="keydown",
                timestamp_ms=20,
                repeat=True,
            ),
            KeystrokeEvent(
                session_id=session_id,
                code="KeyA",
                event_type="keyup",
                timestamp_ms=60,
                repeat=False,
            ),
            KeystrokeEvent(
                session_id=session_id,
                code="KeyB",
                event_type="keyup",
                timestamp_ms=70,
                repeat=False,
            ),
            KeystrokeEvent(
                session_id=session_id,
                code="KeyC",
                event_type="keydown",
                timestamp_ms=80,
                repeat=False,
            ),
        ),
    )

    sequence = events_to_timing_sequence(batch, pause_threshold_ms=1000)

    assert sequence.key_codes == ("KeyA",)
    assert sequence.hold_durations_ms == (50.0,)
    assert sequence.valid_event_count == 2
    assert {issue.code for issue in sequence.quality_issues} == {
        QualityCode.AUTO_REPEAT_IGNORED,
        QualityCode.UNMATCHED_KEYUP,
        QualityCode.MISSING_KEYUP,
    }
