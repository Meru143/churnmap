"""Configuration loading and merge logic for churnmap."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Literal, get_args

import yaml

OutputFormat = Literal["both", "html", "json"]


class ConfigError(Exception):
    """Raised when churnmap configuration cannot be loaded."""


@dataclass(frozen=True)
class ChurnmapConfig:
    """Runtime configuration for a churnmap CLI invocation."""

    repo: Path = Path(".")
    output_dir: Path = Path("./coupling-report")
    lookback_days: int = 90
    min_occurrences: int = 3
    heatmap_limit: int = 50
    top_files: int = 100
    format: OutputFormat = "both"
    exclude: list[str] = field(default_factory=list)
    low_threshold: float = 0.3
    high_threshold: float = 0.7
    open_browser: bool = False


def load_yaml_config(repo_path: Path) -> dict[str, Any]:
    """Load optional ``.churnmap.yml`` from a repository root."""

    config_path = repo_path / ".churnmap.yml"
    if not config_path.exists():
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = f"line {mark.line + 1}: " if mark is not None else ""
        problem = getattr(exc, "problem", None) or str(exc)
        raise ConfigError(f"{line}{problem}") from exc

    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ConfigError("configuration must be a YAML mapping")

    return {str(key): value for key, value in loaded.items()}


def build_config(cli_kwargs: dict[str, Any], repo_path: Path) -> ChurnmapConfig:
    """Merge defaults, YAML configuration, and command-line values."""

    defaults = _defaults_dict()
    yaml_data = _normalize_config_dict(load_yaml_config(repo_path))
    cli_data = _normalize_config_dict(
        {key: value for key, value in cli_kwargs.items() if value is not None}
    )
    merged = defaults | yaml_data | cli_data
    _validate_config_values(merged)
    return ChurnmapConfig(**merged)


def _defaults_dict() -> dict[str, Any]:
    return {
        field_def.name: getattr(ChurnmapConfig(), field_def.name)
        for field_def in fields(ChurnmapConfig)
    }


def _normalize_config_dict(raw: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in raw.items():
        target_key = "open_browser" if key == "open" else key
        if target_key not in _defaults_dict():
            continue
        normalized[target_key] = _cast_value(target_key, value)
    return normalized


def _cast_value(key: str, value: Any) -> Any:
    if key in {"repo", "output_dir"}:
        return Path(value)
    if key in {"lookback_days", "min_occurrences", "heatmap_limit", "top_files"}:
        return int(value)
    if key in {"low_threshold", "high_threshold"}:
        return float(value)
    if key == "exclude":
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value]
    if key == "open_browser":
        return _cast_bool(value)
    if key == "format":
        return str(value)
    return value


def _cast_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _validate_config_values(config: dict[str, Any]) -> None:
    valid_formats = set(get_args(OutputFormat))
    if config["format"] not in valid_formats:
        raise ConfigError("format must be one of: both, html, json")

    for key in ("lookback_days", "min_occurrences", "heatmap_limit", "top_files"):
        if config[key] < 1:
            raise ConfigError(f"{key} must be greater than 0")

    if not 0 <= config["low_threshold"] <= 1:
        raise ConfigError("low_threshold must be between 0 and 1")
    if not 0 <= config["high_threshold"] <= 1:
        raise ConfigError("high_threshold must be between 0 and 1")
    if config["low_threshold"] >= config["high_threshold"]:
        raise ConfigError("low_threshold must be lower than high_threshold")
