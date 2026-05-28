"""Config loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from churnmap.config import ChurnmapConfig, ConfigError, build_config, load_yaml_config


def test_valid_yaml_loaded_sets_lookback_days(tmp_path: Path) -> None:
    (tmp_path / ".churnmap.yml").write_text("lookback_days: 180\n", encoding="utf-8")

    data = load_yaml_config(tmp_path)

    assert data["lookback_days"] == 180


def test_cli_flag_override_wins_over_yaml_value(tmp_path: Path) -> None:
    (tmp_path / ".churnmap.yml").write_text("lookback_days: 90\n", encoding="utf-8")

    config = build_config({"lookback_days": 180}, tmp_path)

    assert config.lookback_days == 180


def test_missing_yaml_file_applies_defaults(tmp_path: Path) -> None:
    config = build_config({}, tmp_path)

    assert config == ChurnmapConfig()


def test_invalid_yaml_raises_config_error_with_line_number(tmp_path: Path) -> None:
    (tmp_path / ".churnmap.yml").write_text("lookback_days: [90\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="line 2"):
        load_yaml_config(tmp_path)


def test_multiple_exclude_values_merge_into_list(tmp_path: Path) -> None:
    config = build_config({"exclude": ["docs/**", "*.md"]}, tmp_path)

    assert config.exclude == ["docs/**", "*.md"]


@pytest.mark.parametrize("output_format", ["both", "html", "json"])
def test_valid_format_values_are_accepted(tmp_path: Path, output_format: str) -> None:
    config = build_config({"format": output_format}, tmp_path)

    assert config.format == output_format


def test_invalid_format_raises_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="format must be one of"):
        build_config({"format": "invalid"}, tmp_path)


def test_yaml_open_maps_to_open_browser(tmp_path: Path) -> None:
    (tmp_path / ".churnmap.yml").write_text("open: true\n", encoding="utf-8")

    config = build_config({}, tmp_path)

    assert config.open_browser is True
