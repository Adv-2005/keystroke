from __future__ import annotations

import random
from pathlib import Path

from keystroke.config import load_config, seed_everything


def test_checked_in_configuration_is_valid() -> None:
    config_path = Path(__file__).parents[2] / "config" / "default.toml"

    config = load_config(config_path)

    assert config.project.schema_version == "1.0.0"
    assert config.scoring.window_length == 50
    assert config.scoring.window_stride == 10
    assert config.scoring.smoothing_alpha == 0.35


def test_seed_everything_reproduces_python_random_stream() -> None:
    first_report = seed_everything(731)
    first_values = [random.random() for _ in range(3)]

    second_report = seed_everything(731)
    second_values = [random.random() for _ in range(3)]

    assert first_report.seed == second_report.seed == 731
    assert first_report.python_seeded is True
    assert first_values == second_values
