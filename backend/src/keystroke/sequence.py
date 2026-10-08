"""Canonical conversion from validated events to paired timing sequences."""

from __future__ import annotations

from dataclasses import dataclass

from keystroke.schemas import (
    EventType,
    KeystrokeEvent,
    KeystrokeEventBatch,
    PauseMarker,
    QualityCode,
    QualityIssue,
    QualitySeverity,
    TimingSequence,
)

CORRECTION_CODES = frozenset({"Backspace", "Delete"})


@dataclass(frozen=True, slots=True)
class _KeyPair:
    code: str
    down_timestamp_ms: float
    up_timestamp_ms: float
    down_event_index: int


def events_to_timing_sequence(
    batch: KeystrokeEventBatch,
    *,
    pause_threshold_ms: float,
) -> TimingSequence:
    """Pair valid events and retain explicit quality findings.

    Repeated keydown events and malformed pairs are excluded rather than given
    fabricated timings. Key pairs are ordered by keydown time, and negative
    keyup-to-next-keydown intervals are preserved for overlapping keys.
    """

    if pause_threshold_ms <= 0:
        raise ValueError("pause_threshold_ms must be positive")

    active: dict[str, tuple[int, KeystrokeEvent]] = {}
    pairs: list[_KeyPair] = []
    quality_issues: list[QualityIssue] = []

    for event_index, event in enumerate(batch.events):
        if event.repeat:
            quality_issues.append(
                QualityIssue(
                    code=QualityCode.AUTO_REPEAT_IGNORED,
                    severity=QualitySeverity.INFO,
                    event_index=event_index,
                    key_code=event.code,
                )
            )
            continue

        if event.event_type is EventType.KEYDOWN:
            if event.code in active:
                quality_issues.append(
                    QualityIssue(
                        code=QualityCode.DUPLICATE_KEYDOWN,
                        severity=QualitySeverity.WARNING,
                        event_index=event_index,
                        key_code=event.code,
                    )
                )
                continue
            active[event.code] = (event_index, event)
            continue

        matched = active.pop(event.code, None)
        if matched is None:
            quality_issues.append(
                QualityIssue(
                    code=QualityCode.UNMATCHED_KEYUP,
                    severity=QualitySeverity.WARNING,
                    event_index=event_index,
                    key_code=event.code,
                )
            )
            continue

        down_event_index, down_event = matched
        pairs.append(
            _KeyPair(
                code=event.code,
                down_timestamp_ms=down_event.timestamp_ms,
                up_timestamp_ms=event.timestamp_ms,
                down_event_index=down_event_index,
            )
        )

    for code, (event_index, _) in active.items():
        quality_issues.append(
            QualityIssue(
                code=QualityCode.MISSING_KEYUP,
                severity=QualitySeverity.WARNING,
                event_index=event_index,
                key_code=code,
            )
        )

    pairs.sort(key=lambda pair: (pair.down_timestamp_ms, pair.down_event_index))
    keydown_intervals = tuple(
        current.down_timestamp_ms - previous.down_timestamp_ms
        for previous, current in zip(pairs, pairs[1:], strict=False)
    )
    up_down_intervals = tuple(
        current.down_timestamp_ms - previous.up_timestamp_ms
        for previous, current in zip(pairs, pairs[1:], strict=False)
    )
    pause_markers = tuple(
        PauseMarker(after_key_index=index, duration_ms=duration)
        for index, duration in enumerate(keydown_intervals)
        if duration >= pause_threshold_ms
    )

    if pause_markers:
        quality_issues.append(
            QualityIssue(
                code=QualityCode.LONG_PAUSE,
                severity=QualitySeverity.INFO,
            )
        )

    return TimingSequence(
        session_id=batch.session_id,
        key_codes=tuple(pair.code for pair in pairs),
        keydown_timestamps_ms=tuple(pair.down_timestamp_ms for pair in pairs),
        keyup_timestamps_ms=tuple(pair.up_timestamp_ms for pair in pairs),
        hold_durations_ms=tuple(
            pair.up_timestamp_ms - pair.down_timestamp_ms for pair in pairs
        ),
        keydown_to_keydown_ms=keydown_intervals,
        keyup_to_keydown_ms=up_down_intervals,
        pause_markers=pause_markers,
        correction_indices=tuple(
            index for index, pair in enumerate(pairs) if pair.code in CORRECTION_CODES
        ),
        quality_issues=tuple(quality_issues),
        valid_event_count=len(pairs) * 2,
    )
