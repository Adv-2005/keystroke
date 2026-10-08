from __future__ import annotations

import json
from pathlib import Path

import pytest

from keystroke.schemas import KeystrokeEventBatch


@pytest.fixture
def synthetic_batch() -> KeystrokeEventBatch:
    fixture_path = Path(__file__).parent / "fixtures" / "synthetic_events.json"
    return KeystrokeEventBatch.model_validate(json.loads(fixture_path.read_text()))
