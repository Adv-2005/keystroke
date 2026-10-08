# AGENTS.md

## Purpose and Scope

This repository contains a CPU-friendly behavioral-biometric research prototype. It studies whether typing rhythm is consistent with an enrolled user and provides a local web demonstration of continuous verification.

These instructions apply to the entire repository. Keep this file focused on durable engineering guidance; put milestones, experiment narratives, and project-management details in dedicated documentation.

This is a research prototype, not production authentication. Do not describe its output as proof of identity or use it as a replacement for passwords or multi-factor authentication.

## Intended Technology

- Frontend: React, TypeScript, and Vite.
- API and research code: Python and FastAPI.
- Machine learning: scikit-learn and CPU-compatible PyTorch.
- Data processing: Pandas and related Python tooling already adopted by the repository.
- Local metadata: SQLite.

Treat this list as architectural direction, not permission to invent setup commands or add dependencies without checking the repository first. Document only commands verified against checked-in configuration.

## Architecture

- Define canonical schemas for raw keystroke events, timing sequences, feature windows, enrollment templates, and score results. Reuse them across ingestion, training, evaluation, and serving.
- Offline evaluation and live inference must use the same validated feature-extraction implementation. Do not maintain parallel feature logic in notebooks and the application.
- Model implementations must follow a common lifecycle: train background state where applicable, enroll a user, score a probe, save artifacts, and load artifacts.
- Keep dataset adapters separate from canonical preprocessing. Dataset-specific quirks must not leak into model code.
- Version model artifacts together with their preprocessing configuration, feature schema, training seed, and dataset-manifest identifier.
- Keep downloaded datasets, participant recordings, generated features, checkpoints, and trained models outside Git. Commit small manifests, schemas, configurations, and reproducible scripts instead.

## Privacy and Security

- Capture keyboard events only while the dedicated demo input is focused. Do not add global keyboard hooks or page-wide monitoring.
- Never persist or transmit the input element's text value. Do not log typed content in application logs, analytics, fixtures, error reports, or debug output.
- Treat key codes and timing data as sensitive biometric data because they may reveal typed content or identifying behavior.
- Collect participant data only with explicit consent, pseudonymous identifiers, non-secret prompts, a stated retention policy, and a working deletion path.
- Minimize stored events and metadata. Avoid collecting names, email addresses, passwords, clipboard contents, or unrelated device information.
- Keep raw participant data and enrollment templates local by default. Do not add telemetry or external uploads without an explicit project decision and documentation.
- Use synthetic events in tests unless a test explicitly requires an approved, anonymized fixture.
- Present re-authentication as a simulated research workflow. Never claim that a consistency score is a security guarantee.

## Machine-Learning Validity

- Split data by subject before fitting preprocessing, generating training pairs or triplets, tuning hyperparameters, or calibrating thresholds.
- Fit imputers, scalers, feature selectors, calibration functions, and other learned preprocessing on training data only.
- Use validation data for model selection and operational thresholds. Do not change a model or threshold after examining final-test results.
- Keep the official fixed-text CMU benchmark protocol separate from the free-text Aalto comparison protocol. Label deviations and do not compare results produced under incompatible protocols as if they were equivalent.
- Use deterministic, recorded seeds for sampling, subject splits, training pairs or triplets, and model initialization.
- Record dataset versions, manifest hashes, eligibility filters, enrollment size, window length, stride, impostor sampling, and calibration policy with every reported experiment.
- Report FAR, FRR, EER, ROC-AUC, the declared form of accuracy, uncertainty intervals, and sample counts. For continuous trials, also report detection delay in seconds and keystrokes.
- Report missed detections, unusable sessions, negative results, and censored trials. Do not silently remove difficult subjects or failed runs.
- Never use subject identity, session identifiers, row order, prompt identifiers, or other leakage-prone metadata as predictive features.

## Runtime Behavior

- Use a monotonic high-resolution clock for event intervals; do not derive timing features from wall-clock timestamps.
- Ignore paste, key auto-repeat, unsupported shortcuts, events recorded outside the focused input, and events spanning a focus loss.
- Detect and flag malformed keydown/keyup pairs rather than fabricating durations. Define explicit quality criteria for scoring or rejecting a window.
- Preserve valid overlapping key events and negative keyup-to-keydown intervals where the feature definition permits them.
- Apply the same window length, stride, normalization, and feature schema used when the selected artifact was trained.
- Distinguish insufficient evidence, low-quality input, low consistency, and system failure in API responses and the UI.
- Label the displayed value as a calibrated **typing consistency score**. Do not call it an identity probability unless probability calibration has been separately validated and documented.

## Testing and Verification

- Unit-test event pairing, overlapping keys, missing releases, auto-repeat, focus loss, pauses, corrections, window boundaries, feature extraction, normalization, scoring, and threshold transitions.
- Add leakage tests that prove subjects do not cross dataset partitions and that preprocessing never fits on validation or test data.
- Test metric implementations against small hand-calculated examples, including FAR, FRR, EER, ROC-AUC, smoothing, and detection delay.
- Contract-test API schemas, artifact compatibility, insufficient-data responses, malformed input, and deletion behavior.
- Add browser-flow coverage for consent, enrollment, live scoring, focus changes, paste rejection, warnings, simulated re-authentication, and data deletion.
- Include privacy tests confirming that typed text values are absent from network payloads, persistence, logs, and exported artifacts.
- Check CPU inference latency and deterministic reproduction of fixed-seed evaluation results.
- Run the narrowest relevant tests while iterating, followed by the broader applicable suite before handing off a change.

## Agent Workflow

- Inspect the repository, nested `AGENTS.md` files, existing schemas, manifests, and tool configuration before making changes.
- Preserve user work and unrelated modifications. Make small, scoped changes that follow existing project conventions.
- Do not invent package, build, test, or data-download commands. Derive them from checked-in files and verify them before documenting them.
- Add or update tests whenever behavior changes. A model change also requires evaluation coverage or a documented reason why existing coverage is sufficient.
- Keep exploratory notebooks thin: reusable preprocessing, models, metrics, and plots belong in importable modules.
- Document any change to dataset filtering, subject splits, feature definitions, evaluation protocols, thresholds, or metric calculations in the same change.
- Do not commit datasets, participant data, generated experiment outputs, secrets, local databases, model artifacts, or dependency caches.
- For every commit, use a concise subject followed by a descriptive body that explains the intent, key changes, and verification performed. Include material deviations or deliberate omissions when relevant so the message can serve as a reliable basis for pull-request content.
- Cite the official CMU and Aalto sources whenever documenting their datasets, benchmark protocols, or assumptions.
- If a required command, dependency, dataset license, or protocol detail cannot be verified, state the uncertainty and stop before encoding a guess as project policy.

## Documentation Boundaries

- Keep installation and execution instructions synchronized with checked-in configuration.
- Put milestone schedules and task tracking in project-planning documentation, not this file.
- Put detailed experiment protocols, threat models, consent materials, and dataset cards in their own documents and link to them when they exist.
- Keep research claims tied to the exact dataset, split, model version, threshold, and evaluation procedure that produced them.

## Primary Dataset References

- CMU Keystroke Dynamics Benchmark: <https://www.cs.cmu.edu/~keystroke/>
- Aalto Computational Behavior Lab code and data index: <https://cbl.aalto.fi/codedata/>
