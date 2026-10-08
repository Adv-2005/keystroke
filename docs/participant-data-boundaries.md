# Participant Data Boundaries

Participant collection does not begin until consent, retention, withdrawal,
and deletion materials are reviewed for the local study. This file defines the
minimum engineering boundary; it is not an ethics approval or consent form.

## Before collection

- Obtain explicit consent before capturing any keyboard event.
- Use a pseudonymous participant ID and public, non-secret guided prompts.
- Explain that key codes can permit partial text reconstruction even though the
  text value is neither collected nor stored.
- State what is collected, why, how long it is retained, where it is stored,
  who can access it, and how withdrawal/deletion works.

## Allowed local data

- Consent status/version and pseudonymous participant/session IDs.
- Focus-scoped key codes, monotonic timing, repeat/quality metadata.
- Derived sequences, features, embeddings, templates, scores, and auditable
  trial outcomes.
- Marked handover timing needed to calculate detection delay.

## Prohibited data

- The input element's text value or logs/screenshots containing typed content.
- Passwords, clipboard content, names, email addresses, or unnecessary device
  identifiers.
- Events outside the dedicated focused input, events spanning focus loss,
  paste, browser auto-repeat, and unsupported shortcuts.
- Telemetry, cloud upload, or sharing without a separately documented decision
  and consent basis.

## Storage and deletion boundary

Raw events, derived features, local databases, templates, artifacts, and study
exports remain outside Git and local by default. A deletion request must remove
all participant-linked raw events, derived data, metadata, templates, scores,
and exports that remain under project control, then return an auditable outcome.
Backups or exceptions, if introduced later, must be stated before collection.

## Retention decision still required

The retention duration, named data custodian, consent document/version, and any
institutional review requirements are unresolved project decisions. Collection
must not start until they are explicitly recorded; Milestone 1 does not guess
them.
