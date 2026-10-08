# Experiment Protocol

## Reproducibility controls

- The checked-in default seed is `20261008`; every manifest and experiment must
  record its effective seed.
- Split subjects before fitting preprocessing, sampling pairs/triplets, tuning,
  or calibrating thresholds.
- Fit learned preprocessing on training identities only. Use validation
  identities for model selection, calibration, and the operational threshold.
- Freeze preprocessing, models, calibration, and thresholds before one final
  evaluation on untouched test identities.
- Record dataset version and manifest hash, eligibility filters, enrollment
  size, window length/stride, impostor sampling, and calibration policy.
- Do not use subject ID, session ID, row order, prompt ID, or split membership as
  predictive features.

No dataset has been downloaded or inspected in Milestone 1. Dataset adapters,
license/checksum records, and verified counts are Milestone 2 work.

## CMU fixed-text reproducibility track

Follow the protocol recorded in `plan.md`: first 200 repetitions per genuine
user for training, last 200 for genuine probes, and the first five repetitions
from each other subject for impostor probes. Report per-user and aggregate
results for Euclidean, Manhattan, and Mahalanobis distances. Any deviation must
be labeled and reported separately.

Primary source: [CMU Keystroke Dynamics Benchmark](https://www.cs.cmu.edu/~keystroke/).

## Aalto free-text comparison track

Build a seeded, deterministic subject-disjoint manifest only after validating
the downloaded dataset and its terms. The planned target is 5,000 background
training, 1,000 validation, and 1,000 final-test identities, configurable
downward for CPU limits without changing selection rules. Evaluate every model
on common users/trials and, where available, 25, 50, 100, and 200-keystroke
probe lengths.

Primary source: [Aalto Computational Behavior Lab code and data index](https://cbl.aalto.fi/codedata/).

## Local continuous track

Use consenting adults, pseudonymous IDs, public non-secret prompts, and marked
handover points. Prefer two sessions separated by 24 hours where scheduling
permits. Local study data must not tune the selected model or threshold.

## Required reporting

Report FAR, FRR, EER, ROC-AUC, balanced accuracy, explicitly defined
conventional accuracy, user-bootstrap 95% intervals, sample counts, and CPU
latency. Continuous trials additionally report detection delay in seconds and
valid keystrokes. Unusable sessions, missed handovers, negative results, and
censored trials remain in the audit trail.

Keep CMU fixed-text, Aalto free-text, and local continuous conclusions separate;
their metrics are not interchangeable evidence.
