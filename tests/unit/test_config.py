import os
from unittest.mock import patch
import pytest
from pydantic import ValidationError

from ai_testgen.config import Settings, get_settings


def test_settings_load_successfully():
    """Test that settings load correctly when all required env vars are present."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key_123", "AI_TESTGEN_MODEL": "custom-model"}):
        settings = get_settings()
        assert settings.google_api_key == "fake_key_123"
        assert settings.model_name == "custom-model"
        assert settings.max_retries == 3
        assert settings.temperature == 0.1


def test_settings_missing_api_key(monkeypatch, tmp_path):
    """Test that settings raise ValueError via get_settings if GOOGLE_API_KEY is missing."""
    monkeypatch.chdir(tmp_path)
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            get_settings()
