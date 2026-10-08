# Behavioral Biometric Authentication Using Typing Patterns

## Handoff for a New Chat

This document is the implementation plan and decision record for the project. Before making changes, read [`AGENTS.md`](./AGENTS.md), inspect the repository, and reconcile this plan with any code or configuration that already exists.

Suggested opening request for a new chat:

> Read `AGENTS.md` and `plan.md`, inspect the repository, and implement Milestone 1. Keep the work scoped to that milestone, run the relevant checks, and report any deviations from the plan.

Do not implement every milestone in one change. Complete and verify each milestone before advancing.

## 1. Project Goal

Build a CPU-friendly academic research prototype that recognizes whether current typing behavior is consistent with an enrolled user. The system must support:

- An enrollment typing exercise.
- Continuous typing-pattern analysis inside a local web application.
- A calibrated 0-100 **typing consistency score**.
- A warning and simulated re-authentication request when typing becomes sufficiently inconsistent.
- Reproducible comparison of statistical, classical machine-learning, and compact deep-learning methods.
- Evaluation with standard biometric metrics and short-versus-long sample analysis.

The system analyzes timing and behavior rather than submitted text. Relevant signals include key-hold duration, inter-key timing, speed, corrections, pauses, digraph/trigraph timing, and behavioral drift during a session.

This is an academic prototype and demonstration. It is not production authentication, must not replace passwords or MFA, and must not describe its score as proof of identity.

## 2. Decisions Already Made

- Primary outcome: rigorous academic comparison plus a polished real-time demonstration.
- Demo platform: local web application.
- Development constraint: solo project over approximately 8-10 weeks.
- Compute constraint: training and inference must work without a GPU.
- Public data: CMU benchmark plus a deterministic, manageable subset of the Aalto desktop dataset.
- Local validation: a small consented study with approximately 10-20 participants.
- Deep model: compact LSTM embedding network trained with triplet loss.
- Browser scope: capture events only in the focused demo typing area, never system-wide.
- Output wording: "typing consistency score," not identity probability unless probability calibration is separately validated.
- Re-authentication: simulated modal/workflow only; do not lock a real user account.

## 3. Scope and Non-Goals

### In scope

- Guided enrollment and continuous scoring in a local browser UI.
- Offline CMU and Aalto ingestion and preprocessing.
- One shared feature pipeline for offline experiments and live inference.
- Statistical-distance baseline, KNN, One-Class SVM, Isolation Forest, Random Forest verifier, and LSTM embedding model.
- FAR, FRR, EER, ROC-AUC, balanced accuracy, declared conventional accuracy, detection delay, inference latency, and performance by sample length.
- Experiment reproducibility, privacy controls, participant deletion, and a final research report.

### Out of scope

- Operating-system-wide keyboard monitoring.
- Production account security, real account lockouts, or claims of deployment readiness.
- Cloud data collection, telemetry, or remote model serving.
- Identification of an unknown typist; the task is verification against an enrolled template.
- Mobile touchscreen authentication in the initial implementation.
- Training on the full Aalto dataset when a deterministic subset is sufficient for the project question.

## 4. Proposed Technology and Repository Shape

Use the repository's established configuration if it exists. For a greenfield repository, use:

- Frontend: React, TypeScript, and Vite.
- API: Python 3.11 and FastAPI.
- Classical ML: NumPy, Pandas, and scikit-learn.
- Deep learning: CPU-compatible PyTorch.
- Local metadata: SQLite.
- Processed tabular/sequence data: Parquet.
- Model artifacts: versioned `joblib` and PyTorch state files outside Git.
- Tests: pytest for Python; the existing TypeScript test framework plus browser-flow tests for the UI.

Suggested top-level responsibilities, without forcing directories before the repository is inspected:

- API and application services.
- Canonical schemas and feature extraction.
- Dataset adapters and reproducible split manifests.
- Model implementations behind a shared interface.
- Experiment/evaluation entry points.
- Web enrollment and continuous-scoring UI.
- Tests, research documentation, and small checked-in configurations.

Downloaded datasets, participant recordings, generated features, checkpoints, trained artifacts, local databases, and experiment output must remain outside Git. Add ignore rules and small manifest/configuration files instead.

## 5. System Architecture

### 5.1 Event capture

The frontend captures `keydown` and `keyup` events only while the dedicated input is focused. Use the browser's monotonic high-resolution time source. Never send or persist the input element's text value.

Ignore or invalidate:

- Paste operations.
- Browser-generated key auto-repeat.
- Unsupported keyboard shortcuts.
- Events outside the focused input.
- Key pairs spanning a focus loss.
- Malformed pairs that cannot produce reliable timing.

Preserve valid overlapping key events and negative keyup-to-next-keydown intervals, because they can represent genuine typing overlap.

### 5.2 Canonical types

Define and version these types before implementing models:

#### `KeystrokeEvent`

- Pseudonymous session ID.
- Key code or approved key representation.
- Event type: keydown or keyup.
- Monotonic timestamp in milliseconds.
- Repeat flag.
- Optional quality metadata that cannot reveal typed text.

#### `TimingSequence`

- Ordered key representation.
- Hold durations.
- Keydown-to-keydown intervals.
- Keyup-to-keydown intervals.
- Pause markers and correction events.
- Sequence quality flags.

#### `FeatureWindow`

- Feature schema version.
- Window start/end and valid-event count.
- Engineered numeric feature vector.
- Quality flags and rejection reason when applicable.

#### `EnrollmentTemplate`

- Pseudonymous user ID.
- Model and preprocessing versions.
- Enrollment feature windows and/or embedding centroid.
- Calibration/threshold reference.
- Creation metadata without personal identifiers.

#### `ScoreResult`

- Model ID and artifact version.
- Evidence/window size.
- Raw similarity or anomaly score.
- Calibrated 0-100 consistency score.
- Smoothed score.
- State: warming up, normal, warning, re-authentication requested, insufficient evidence, low-quality input, or system error.
- Operational threshold and quality information.

### 5.3 Shared model contract

Every model must support a consistent lifecycle, with no model-specific branching in the API layer:

- Fit background/global state when applicable.
- Enroll a new user from enrollment samples.
- Score a probe window against the enrollment template.
- Serialize the artifact and all preprocessing/configuration dependencies.
- Load it with schema/version compatibility checks.

### 5.4 API contract

Implement a local API with behavior equivalent to:

- `POST /api/enrollments` - start an enrollment and return a pseudonymous enrollment ID.
- `POST /api/enrollments/{id}/events` - validate and accept event batches.
- `POST /api/enrollments/{id}/finalize` - validate evidence and create an enrollment template.
- `POST /api/sessions` - start a verification session for an enrolled user.
- `POST /api/sessions/{id}/events` - accept events and return the latest `ScoreResult` when enough evidence exists.
- `GET /api/sessions/{id}/history` - return score/state history for the demo chart.
- `DELETE /api/users/{id}` - delete local events, metadata, and templates for that pseudonymous user.

Return distinct error/status responses for malformed input, insufficient evidence, low-quality input, incompatible artifacts, and server failure.

### 5.5 Runtime scoring policy

Initial defaults:

- Enrollment: five guided samples of approximately 50 valid keystrokes each.
- Scoring window: 50 valid keystrokes.
- Window stride: 10 valid keystrokes.
- Warm-up: no identity decision before the first complete window.
- Smoothing: exponential moving average with initial `alpha = 0.35`.
- Operational threshold: chosen on validation data at a target FAR of 1%; also report the EER threshold separately.
- Warning: two consecutive smoothed scores below the operational threshold.
- Simulated re-authentication: three consecutive scores below threshold.

These defaults are configuration, not hidden constants. If validation justifies changing them, record the change and rerun the frozen evaluation protocol.

## 6. Feature Pipeline

Offline evaluation and live inference must call the same feature implementation.

Classical features should include, where supported by the current window:

- Hold-time mean, standard deviation, median, and robust quantiles.
- Keydown-to-keydown and keyup-to-keydown timing statistics.
- Overlap frequency and magnitude.
- Keystrokes per second and burst-level speed.
- Backspace/correction frequency.
- Pause count, quantiles, histogram bins, and burst lengths.
- Within-window timing variability.
- Key-category and keyboard-region transition timing.
- Available common digraph and trigraph timing aggregates.
- Data-quality indicators, used for rejection or analysis rather than identity leakage.

Rules:

- Fit imputation, scaling, selection, and calibration only on training data.
- Never use user ID, session ID, row order, prompt ID, split membership, or other leakage-prone metadata as predictive input.
- Version the feature schema and reject incompatible artifacts.
- Use robust handling for missing n-grams in free text; do not fabricate timings.

## 7. Model Implementations

Implement and compare these six primary approaches:

1. **Statistical-distance baseline**
   - Primary free-text baseline: scaled Manhattan distance from the enrolled feature distribution.
   - Also implement Euclidean and Mahalanobis forms to reproduce the CMU reference results.

2. **K-Nearest Neighbours**
   - Score a probe using mean distance to the nearest enrolled feature windows.
   - Select `k` and distance/scaling on validation data only.

3. **One-Class SVM**
   - RBF kernel trained only on genuine enrollment samples for each user.
   - Tune kernel and `nu` using permitted training/validation data, never final-test users.

4. **Isolation Forest**
   - Train only on genuine enrollment samples for each user.
   - Convert anomaly output into the common score direction before calibration.

5. **Random Forest verifier**
   - Use a global subject-independent pairwise verifier rather than an under-sampled per-user classifier.
   - Train on features such as absolute differences between same-user and different-user sample pairs drawn only from background-training identities.
   - Apply the trained verifier to unseen enrolled users without retraining on test identities.

6. **Compact LSTM embedding model**
   - Two-layer sequence encoder sized for CPU training.
   - Train with triplet loss on Aalto background-training identities.
   - Freeze the encoder before validation/final testing.
   - Enroll unseen users by averaging enrollment embeddings.
   - Score probes using cosine similarity/distance to the template centroid.

All raw model outputs must follow a documented score direction and pass through validation-fitted calibration before being displayed.

## 8. Data and Evaluation Protocols

### 8.1 CMU reproducibility track

Use the official CMU Keystroke Dynamics benchmark to establish that the timing and metric pipeline is correct:

- 51 subjects.
- One fixed password.
- 400 repetitions per subject over eight sessions.
- For each genuine user, train on the first 200 repetitions.
- Test on the user's last 200 repetitions.
- Use the first five repetitions from each of the other 50 subjects as impostor probes.
- Compute per-user ROC/EER and aggregate across all 51 users.

Reproduce the published Euclidean, Manhattan, and Mahalanobis results before extending the benchmark. Keep any altered protocol clearly separate.

Official source: <https://www.cs.cmu.edu/~keystroke/>

### 8.2 Aalto full-comparison track

Create a seeded, deterministic, subject-disjoint subset of eligible Aalto desktop users:

- 5,000 background-training identities.
- 1,000 validation identities.
- 1,000 untouched final-test identities.

Initial test protocol:

- Five enrollment sequences per test user.
- Remaining eligible sequences serve as genuine probes.
- Use balanced, reproducible impostor trials drawn from other test users.
- Evaluate all six model families on exactly the same final-test users and trials.
- Evaluate probe lengths of 25, 50, 100, and 200 keystrokes where data permits.

If hardware limitations require a smaller subset, reduce it through configuration with the same seeded selection rules, record the change, and do not mix results from different subset definitions.

Aalto data index: <https://cbl.aalto.fi/codedata/>

Relevant embedding-model reference: <https://arxiv.org/abs/2101.05570>

### 8.3 Local continuous-authentication track

Recruit approximately 10-20 consenting adult participants. Use pseudonymous IDs and guided, non-secret prompts. Prefer at least two sessions per participant separated by 24 hours when scheduling permits.

Collect:

- Guided enrollment samples.
- Genuine continuation samples.
- Natural pauses and corrections.
- Deliberately slower and faster genuine typing.
- Marked handover trials in which an impostor begins typing at a known point.

Do not use local test trials to retune the selected model or threshold. Report unusable sessions and non-detections.

### 8.4 Metrics

Report:

- False Acceptance Rate (FAR).
- False Rejection Rate (FRR).
- Equal Error Rate (EER).
- ROC-AUC.
- Balanced accuracy.
- Conventional accuracy only with the class/trial distribution explicitly declared.
- Detection delay in seconds and valid keystrokes after a known handover.
- CPU inference latency per scored window.
- Performance for 25, 50, 100, and 200-keystroke samples.
- User-bootstrap 95% confidence intervals.

Missed handovers are censored failures, not observations to omit. Choose models and thresholds using validation results; final-test results are reported once without further tuning.

## 9. Privacy and Participant Handling

- Show consent before any participant event collection.
- Use public, non-secret guided prompts for enrollment and study trials.
- Never store or transmit the input's text value.
- Treat key codes, timestamps, features, embeddings, and templates as sensitive biometric data.
- Keep data local by default and provide verified deletion of raw events, derived features, metadata, and templates.
- Collect no names, email addresses, passwords, clipboard data, or unnecessary device identifiers.
- Define retention, withdrawal, and deletion procedures before recruitment.
- Use synthetic data in automated tests unless an explicitly approved anonymized fixture is necessary.

Key-code sequences may permit partial reconstruction of text even if text values are not stored. State this honestly in consent and documentation.

## 10. Milestones

### Milestone 1 - Foundation and protocol (Week 1)

Deliverables:

- Establish the actual frontend/backend project structure and dependency locks.
- Add configuration, reproducible random-seed handling, and ignored artifact/data locations.
- Define canonical event, sequence, feature, template, and score schemas.
- Define the common model interface.
- Write the threat model, data dictionary, experiment protocol, and participant-data boundaries.
- Add a synthetic event fixture and schema-validation tests.

Exit criteria:

- A synthetic event batch can be validated and converted into a canonical sequence.
- The project's verified setup and test commands are documented.
- No speculative commands or unverified dataset claims are recorded.

### Milestone 2 - Public-data pipelines (Week 2)

Deliverables:

- Reproducible download/import instructions with source, license/citation, and checksum records.
- CMU and Aalto dataset adapters producing the canonical sequence format.
- Deterministic subject-split manifests.
- Data-audit reports for subject counts, sessions, invalid events, and split overlap.

Exit criteria:

- Expected dataset structure is validated.
- Automated checks prove that subject identities do not cross Aalto partitions.

### Milestone 3 - Capture and features (Week 3)

Deliverables:

- Focus-scoped browser event collector.
- Keydown/keyup pairing, quality checks, and windowing.
- Shared classical feature extraction.
- Exploratory plots for timing distributions, missing events, pauses, and user/session variability.

Exit criteria:

- Equivalent prerecorded and live event streams produce matching timing sequences and features.
- Tests cover auto-repeat, overlap, missing keyup, focus loss, paste, pauses, and corrections.

### Milestone 4 - Statistical and classical models (Weeks 4-5)

Deliverables:

- CMU distance-baseline reproduction.
- KNN, One-Class SVM, Isolation Forest, and global pairwise Random Forest implementations.
- Validation-only tuning and artifact serialization.

Exit criteria:

- CMU distance EERs are within approximately one percentage point of published results, or discrepancies are investigated and documented.
- Every model conforms to the shared lifecycle and reloads with identical scoring behavior.

### Milestone 5 - LSTM embedding model (Week 6)

Deliverables:

- Compact two-layer LSTM encoder and triplet sampling/training pipeline.
- Frozen embedding inference, template averaging, and cosine scoring.
- Small validation ablation for sequence length and one-versus-five enrollment samples.

Exit criteria:

- CPU training finishes under the configured subset budget.
- A saved/reloaded encoder produces reproducible embeddings.
- Validation verification is measurably better than random scoring.

### Milestone 6 - Frozen comparison (Week 7)

Deliverables:

- Freeze preprocessing, hyperparameters, calibration, thresholds, and final-test identities.
- Evaluate all six models on the common Aalto protocol.
- Generate ROC/DET curves, FAR/FRR plots, sample-length comparisons, confidence intervals, and latency tables.
- Select the live-demo model using validation quality and CPU latency, not final-test ranking.

Exit criteria:

- One reproducible entry point regenerates the primary tables and figures.
- Final-test output contains every required metric and failed/censored trial count.

### Milestone 7 - Local web demo (Week 8)

Deliverables:

- Consent, guided enrollment, continuous typing, score gauge, evidence count, quality feedback, history chart, warning state, model selector, and simulated re-authentication.
- Local API and persistent pseudonymous profiles.
- Export/deletion controls appropriate to the research workflow.

Exit criteria:

- Enrollment-to-alert works without page reload.
- Selected-model scoring is below 100 ms p95 per window on the reference laptop.
- Inspection confirms that input text values are absent from network payloads, logs, and persistence.

### Milestone 8 - Participant study (Week 9)

Deliverables:

- Approved consent and collection procedure.
- Two-session data where feasible, genuine variation trials, and marked handovers.
- Cross-session error rates, score drift, and detection-delay results.

Exit criteria:

- Every attempted trial has an auditable outcome, including unusable sessions and non-detections.
- Local test data has not been used to change the selected model or threshold.

### Milestone 9 - Final report and handoff (Week 10)

Deliverables:

- Research report covering methodology, results, limitations, privacy, ethics, and failure cases.
- Reproducibility guide and dataset/model cards.
- Clean demonstration instructions based only on verified project commands.

Exit criteria:

- A clean environment can run the applicable tests, reproduce a small benchmark, load the selected artifact, and launch the local demo.
- Results clearly separate fixed-text CMU, free-text Aalto, and small local-study conclusions.

## 11. Test Plan

### Unit tests

- Event ordering and keydown/keyup pairing.
- Overlapping keys and valid negative up-down intervals.
- Missing releases, focus loss, auto-repeat, paste, shortcuts, and malformed input.
- Window lengths, strides, warm-up, quality rejection, and evidence counts.
- Feature values, imputation, normalization, and schema compatibility.
- Model score direction, calibration, smoothing, warning transitions, and artifact reload.
- FAR, FRR, EER, ROC-AUC, balanced accuracy, confidence intervals, and detection delay on hand-calculated examples.

### Leakage and reproducibility tests

- No subject overlap across Aalto train/validation/test partitions.
- No preprocessing fit on validation or final-test data.
- Pair/triplet generation stays within the permitted split.
- Fixed seeds reproduce manifests, trials, and deterministic evaluation outputs within documented numerical tolerance.

### Integration and browser tests

- Enrollment creation, event batching, finalization, scoring, history, and deletion.
- Consent flow, focus-scoped capture, paste rejection, warm-up, warning, re-authentication modal, and recovery.
- Invalid/insufficient evidence and incompatible-artifact responses.
- Typed text absent from requests, persistence, logs, and exports.

### Performance tests

- CPU scoring latency per 50-event window.
- Memory bounds for dataset conversion and subset training.
- Continuous session stability over long typing streams.

## 12. Acceptance Criteria

The project is complete when:

- All six requested model families are implemented behind the shared interface.
- CMU distance baselines are reproduced or discrepancies are rigorously explained.
- All models are evaluated on the same untouched Aalto test protocol.
- FAR, FRR, EER, ROC-AUC, accuracy definitions, confidence intervals, sample-length results, and latency are reported.
- Local handover trials report detection delay and missed detections.
- The local web demo supports consent, enrollment, live scoring, warning, simulated re-authentication, and deletion.
- No typed text value is sent or persisted.
- Subject split and preprocessing leakage checks pass.
- The selected model scores a window below 100 ms p95 on the documented reference CPU.
- Setup, tests, experiments, limitations, and dataset citations are reproducible and accurately documented.

## 13. Known Risks and Mitigations

- **Text leakage from key codes:** use only non-secret guided prompts for collected study data, minimize retention, disclose reconstruction risk, and never store the input value.
- **Browser timing noise:** record quality metadata, use monotonic timing, test across sessions, and avoid overstating results.
- **Too little enrollment data:** use five enrollment sequences by default and report one-versus-five-sample ablations.
- **Class imbalance:** use balanced, reproducible verification trials and report FAR/FRR separately from accuracy.
- **Data leakage:** enforce subject-first splitting and automated leakage tests before fitting any preprocessing or model.
- **Dataset mismatch:** report CMU fixed-text, Aalto transcribed free-text, and local continuous results separately.
- **Behavior drift:** measure cross-session changes and avoid updating templates from unverified sessions in the initial system.
- **CPU training cost:** keep the Aalto subset and LSTM size configurable while preserving deterministic selection and reporting.
- **Misleading confidence:** display a calibrated consistency score with evidence count and system state, not a categorical identity claim.

## 14. First Implementation Session

The first new chat should implement only Milestone 1:

1. Read `AGENTS.md` and this plan completely.
2. Inspect the repository, current Git state, manifests, and any nested instructions.
3. Identify and preserve existing work.
4. Establish only the minimum verified project structure needed for canonical schemas and tests.
5. Implement the event-to-sequence schema path using synthetic data.
6. Add focused tests and run the verified narrow test commands.
7. Update documentation with commands only after they have been run successfully.
8. Report completed acceptance checks, deviations, and the exact starting point for Milestone 2.
