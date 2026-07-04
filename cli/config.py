"""Load and resolve seo-playbook CLI configuration.

Configuration is optional: every setting has a built-in default, and a
project config file only needs to override the values that differ. Lookup
order: an explicit ``--config`` path, then ``seo-playbook.yml`` or
``.seo-playbook.yml`` in the current directory, then built-in defaults.

Example:
    >>> from cli.config import Config
    >>> Config.from_dict({"brand": "Example Corp"}).brand
    'Example Corp'
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILENAMES = ("seo-playbook.yml", ".seo-playbook.yml")


class ConfigError(ValueError):
    """Raised when a config file exists but cannot be loaded as expected."""


@dataclasses.dataclass
class Config:
    """Resolved CLI configuration, merging file values with defaults."""

    brand: str | None = None
    domain: str | None = None
    output_dir: str = "."
    default_similarity_threshold: float = 0.34

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Build a :class:`Config`, ignoring any keys that aren't recognized fields.

        Args:
            data: A mapping of config keys to values, typically parsed from YAML.

        Returns:
            A :class:`Config` populated from the recognized keys in data.
        """
        known_fields = {f.name for f in dataclasses.fields(cls)}
        unknown = set(data) - known_fields
        if unknown:
            logger.warning("Ignoring unknown config key(s): %s", ", ".join(sorted(unknown)))
        return cls(**{key: value for key, value in data.items() if key in known_fields})


def find_config_file(explicit_path: str | Path | None = None) -> Path | None:
    """Locate the config file to load.

    Args:
        explicit_path: A user-specified config file path. If given, it must exist.

    Returns:
        The resolved config file path, or ``None`` if no config file was
        specified and none of the default filenames exist in the current directory.

    Raises:
        ConfigError: If explicit_path is given but does not point to a file.
    """
    if explicit_path is not None:
        path = Path(explicit_path)
        if not path.is_file():
            raise ConfigError(f"Config file not found: {path}")
        return path

    for name in DEFAULT_CONFIG_FILENAMES:
        candidate = Path(name)
        if candidate.is_file():
            return candidate
    return None


def load_config(explicit_path: str | Path | None = None) -> Config:
    """Load and resolve the CLI configuration.

    Args:
        explicit_path: A user-specified config file path, overriding auto-discovery.

    Returns:
        A :class:`Config`. If no config file is found, returns default values.

    Raises:
        ConfigError: If a config file is found but is not a valid YAML mapping.
    """
    path = find_config_file(explicit_path)
    if path is None:
        return Config()

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse config file {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"Config file {path} must contain a YAML mapping at the top level")

    logger.debug("Loaded config from %s", path)
    return Config.from_dict(raw)
