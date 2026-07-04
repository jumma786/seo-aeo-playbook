"""Unit tests for cli.config."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.config import Config, ConfigError, find_config_file, load_config


class TestConfigFromDict:
    def test_known_keys_populate_fields(self) -> None:
        config = Config.from_dict({"brand": "Example Corp", "domain": "example.com"})
        assert config.brand == "Example Corp"
        assert config.domain == "example.com"

    def test_unknown_keys_are_ignored(self, caplog: pytest.LogCaptureFixture) -> None:
        config = Config.from_dict({"brand": "Example Corp", "made_up_key": "value"})
        assert config.brand == "Example Corp"
        assert not hasattr(config, "made_up_key")

    def test_empty_dict_returns_defaults(self) -> None:
        assert Config.from_dict({}) == Config()


class TestFindConfigFile:
    def test_no_file_present_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert find_config_file() is None

    def test_default_filename_discovered(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "seo-playbook.yml").write_text("brand: Example\n", encoding="utf-8")
        found = find_config_file()
        assert found is not None
        assert found.name == "seo-playbook.yml"

    def test_explicit_path_must_exist(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigError):
            find_config_file(tmp_path / "does-not-exist.yml")

    def test_explicit_path_returned_when_present(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.yml"
        config_file.write_text("brand: Example\n", encoding="utf-8")
        assert find_config_file(config_file) == config_file


class TestLoadConfig:
    def test_no_config_file_returns_defaults(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert load_config() == Config()

    def test_loads_values_from_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.yml"
        config_file.write_text("brand: Example Corp\ndomain: example.com\n", encoding="utf-8")
        config = load_config(config_file)
        assert config.brand == "Example Corp"
        assert config.domain == "example.com"

    def test_non_mapping_yaml_raises(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.yml"
        config_file.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ConfigError):
            load_config(config_file)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.yml"
        config_file.write_text("brand: [unclosed\n", encoding="utf-8")
        with pytest.raises(ConfigError):
            load_config(config_file)

    def test_empty_file_returns_defaults(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.yml"
        config_file.write_text("", encoding="utf-8")
        assert load_config(config_file) == Config()
