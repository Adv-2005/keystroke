"""Common lifecycle contract for every verification model family."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import ClassVar, TypeAlias

from keystroke.schemas import (
    ArtifactMetadata,
    EnrollmentTemplate,
    FeatureWindow,
    PseudonymousId,
    ScoreResult,
    TimingSequence,
)

ModelInput: TypeAlias = FeatureWindow | TimingSequence


class TypingVerificationModel(ABC):
    """Uniform train, enroll, score, persist, and restore lifecycle."""

    model_id: ClassVar[str]
    model_version: ClassVar[str]

    @abstractmethod
    def fit_background(
        self,
        samples: Mapping[PseudonymousId, Sequence[ModelInput]],
        *,
        seed: int,
    ) -> None:
        """Fit global state using background-training identities only."""

    @abstractmethod
    def enroll(
        self,
        user_id: PseudonymousId,
        samples: Sequence[ModelInput],
        *,
        artifact: ArtifactMetadata,
    ) -> EnrollmentTemplate:
        """Build a template for an unseen pseudonymous user."""

    @abstractmethod
    def score(
        self,
        probe: ModelInput,
        template: EnrollmentTemplate,
    ) -> ScoreResult:
        """Score a probe with the documented common score direction."""

    @abstractmethod
    def save(self, destination: Path) -> None:
        """Persist model state plus preprocessing and compatibility metadata."""

    @classmethod
    @abstractmethod
    def load(
        cls,
        source: Path,
        *,
        expected_schema_version: str,
        expected_feature_schema_version: str,
    ) -> TypingVerificationModel:
        """Restore an artifact, rejecting incompatible schema versions."""
