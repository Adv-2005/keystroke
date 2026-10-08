"""Validated project configuration and reproducible random-seed handling."""

from __future__ import annotations

import importlib.util
import random
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from keystroke.schemas import SchemaVersion


class _ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProjectSettings(_ConfigModel):
    schema_version: SchemaVersion
    random_seed: int = Field(ge=0, le=2**32 - 1)


class SequenceSettings(_ConfigModel):
    pause_threshold_ms: float = Field(gt=0, allow_inf_nan=False)


class ScoringSettings(_ConfigModel):
    enrollment_samples: int = Field(gt=0)
    keystrokes_per_enrollment_sample: int = Field(gt=0)
    window_length: int = Field(gt=0)
    window_stride: int = Field(gt=0)
    smoothing_alpha: float = Field(gt=0, le=1, allow_inf_nan=False)
    target_far: float = Field(ge=0, le=1, allow_inf_nan=False)
    warning_consecutive_windows: int = Field(gt=0)
    reauthentication_consecutive_windows: int = Field(gt=0)


class AppConfig(_ConfigModel):
    project: ProjectSettings
    sequence: SequenceSettings
    scoring: ScoringSettings


class SeedReport(_ConfigModel):
    seed: int
    python_seeded: bool
    numpy_seeded: bool
    torch_seeded: bool


def load_config(path: Path) -> AppConfig:
    """Load a checked-in TOML configuration through a strict schema."""

    with path.open("rb") as config_file:
        return AppConfig.model_validate(tomllib.load(config_file))


def seed_everything(seed: int, *, deterministic_torch: bool = True) -> SeedReport:
    """Seed installed numerical runtimes without requiring optional ML packages."""

    if not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must fit in an unsigned 32-bit integer")

    random.seed(seed)
    numpy_seeded = False
    torch_seeded = False

    if importlib.util.find_spec("numpy") is not None:
        import numpy

        numpy.random.seed(seed)
        numpy_seeded = True

    if importlib.util.find_spec("torch") is not None:
        import torch

        torch.manual_seed(seed)
        if deterministic_torch:
            torch.use_deterministic_algorithms(True)
        torch_seeded = True

    return SeedReport(
        seed=seed,
        python_seeded=True,
        numpy_seeded=numpy_seeded,
        torch_seeded=torch_seeded,
    )
