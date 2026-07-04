"""Unit tests for scripts.init."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.config import load_config
from scripts.init import InitError, init_project, render_config_yaml


class TestRenderConfigYaml:
    def test_only_provided_fields_written(self) -> None:
        content = render_config_yaml(brand="Example Corp")
        assert "brand: Example Corp" in content
        assert "domain" not in content

    def test_no_overrides_produces_empty_mapping(self) -> None:
        assert render_config_yaml() == "{}\n"

    def test_all_fields_written(self) -> None:
        content = render_config_yaml(brand="Example Corp", domain="example.com", output_dir="dist", default_similarity_threshold=0.5)
        assert "brand: Example Corp" in content
        assert "domain: example.com" in content
        assert "output_dir: dist" in content
        assert "default_similarity_threshold: 0.5" in content


class TestInitProject:
    def test_writes_config_file(self, tmp_path: Path) -> None:
        path = init_project(tmp_path, brand="Example Corp")
        assert path == tmp_path / "seo-playbook.yml"
        assert path.exists()
        assert "brand: Example Corp" in path.read_text(encoding="utf-8")

    def test_result_loadable_by_cli_config(self, tmp_path: Path) -> None:
        path = init_project(tmp_path, brand="Example Corp", domain="example.com")
        config = load_config(path)
        assert config.brand == "Example Corp"
        assert config.domain == "example.com"

    def test_refuses_to_overwrite_by_default(self, tmp_path: Path) -> None:
        init_project(tmp_path, brand="Example Corp")
        with pytest.raises(InitError):
            init_project(tmp_path, brand="Other Corp")

    def test_force_overwrites_existing(self, tmp_path: Path) -> None:
        init_project(tmp_path, brand="Example Corp")
        path = init_project(tmp_path, brand="Other Corp", force=True)
        assert "Other Corp" in path.read_text(encoding="utf-8")

    def test_rejects_unrecognized_filename(self, tmp_path: Path) -> None:
        with pytest.raises(InitError):
            init_project(tmp_path, filename="not-a-recognized-name.yml")

    def test_creates_missing_directory(self, tmp_path: Path) -> None:
        target_dir = tmp_path / "nested" / "project"
        path = init_project(target_dir, brand="Example Corp")
        assert path.exists()
