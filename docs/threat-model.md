# Threat Model

## Scope and security claim

The project measures whether a focused browser typing sample is behaviorally
consistent with a locally enrolled template. It is a research prototype, not
production authentication, proof of identity, or a replacement for passwords
or multi-factor authentication. Re-authentication is simulated.

## Protected data

- Key codes and monotonic event timestamps.
- Derived timing sequences and feature windows.
- Enrollment templates, embeddings, thresholds, and score history.
- Pseudonymous participant/session identifiers and consent records.

Key-code sequences are sensitive because they may permit partial reconstruction
of entered text. Avoiding the input element's text value reduces exposure but
does not make the event stream anonymous.

## Trust boundaries

1. The dedicated, focused browser input is the only authorized capture surface.
2. The local API validates canonical schemas and must reject extra fields.
3. Local raw-data, artifact, and SQLite locations are outside Git.
4. Public dataset imports are untrusted until an adapter validates their shape
   and provenance.
5. Experiment outputs are research evidence, not authorization decisions.

## Threats and controls

| Threat | Initial control | Later verification |
| --- | --- | --- |
| Accidental capture of passwords or unrelated typing | Capture only in a dedicated focused input; use public non-secret prompts | Browser-flow focus and paste tests |
| Typed text sent or persisted | Canonical event schema excludes text and forbids unknown fields | Payload, log, persistence, and export privacy tests |
| Reconstruction from key codes | Treat events as sensitive; disclose risk; minimize retention; local storage by default | Participant materials and deletion tests |
| Global/page-wide monitoring | No global hooks; invalidate focus-spanning pairs | Browser-flow inspection |
| Replay or fabricated events | Pseudonymous sessions, ordered monotonic timestamps, quality checks | API/session validation in later milestones |
| Malformed timings affecting scores | Exclude and flag malformed pairs; never fabricate durations | Pairing and quality tests |
| Model or preprocessing incompatibility | Version schemas, preprocessing, seed, and dataset manifest with artifacts | Save/load compatibility tests |
| Research leakage or optimistic evaluation | Subject-first splits; train-only fitted transforms; frozen final test | Automated leakage tests |
| Misleading UI claims | Use “typing consistency score”; show evidence and quality states | UI copy and browser-flow tests |
| Local data remaining after withdrawal | Define full deletion scope before collection | API and filesystem deletion tests |

## Explicit non-goals

Milestone 1 does not add event capture, participant collection, remote uploads,
account lockout, adversarial-spoof resistance, or production security controls.
