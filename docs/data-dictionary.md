# Canonical Data Dictionary

Canonical schema version: `1.0.0`. The executable definitions live in
`backend/src/keystroke/schemas.py`; this document describes their meaning and
privacy constraints.

## KeystrokeEvent

| Field | Meaning | Constraint |
| --- | --- | --- |
| `schema_version` | Canonical contract version | Exactly `1.0.0` |
| `session_id` | Pseudonymous session reference | 8-64 safe identifier characters |
| `code` | Approved browser-style physical key code | Never the input text value |
| `event_type` | Event edge | `keydown` or `keyup` |
| `timestamp_ms` | High-resolution monotonic time | Finite, non-negative milliseconds |
| `repeat` | Browser auto-repeat indicator | Repeated events are ignored during conversion |

`KeystrokeEventBatch` requires one session, timestamp ordering, and at least one
event. Unknown fields are rejected; therefore a `text`, `value`, or similar
field cannot silently enter the canonical payload.

## TimingSequence

Contains ordered paired key codes, down/up timestamps, hold durations,
keydown-to-keydown intervals, and keyup-to-next-keydown intervals. Negative
keyup-to-keydown values are valid and represent overlap. It also records pause
markers, correction-key indices, quality issues, and the count of events in
valid pairs. Malformed pairs are flagged and omitted, not assigned invented
durations.

## FeatureWindow

Contains the feature-schema version, half-open source index bounds, valid-event
count, ordered feature names and numeric values, quality issues, and an explicit
rejection state/reason. Identifiers and prompt/session metadata are not feature
values. Actual feature extraction begins in Milestone 3.

## EnrollmentTemplate

Contains a pseudonymous user ID, artifact metadata, accepted enrollment feature
windows and/or an embedding centroid, and a validation-derived calibration
reference. Artifact metadata records model, preprocessing, feature schema,
training seed, and dataset-manifest versions.

## ScoreResult

Contains model/artifact identifiers, evidence size, raw score, calibrated
0-100 typing consistency score, smoothed score, operational threshold, quality
issues, and one explicit state:

- `warming_up`
- `normal`
- `warning`
- `reauthentication_requested`
- `insufficient_evidence`
- `low_quality_input`
- `system_error`

The score is not an identity probability. Non-scoring states do not carry
numeric scores, preventing missing evidence from appearing as a low score.

## QualityIssue

Uses controlled codes and severities rather than arbitrary messages that could
accidentally include typed content. A key code and event index may be retained
for local diagnosis; both remain sensitive.
