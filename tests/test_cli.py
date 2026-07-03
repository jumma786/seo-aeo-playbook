"""Unit tests for cli.commands (the seo-playbook CLI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

import cli.commands as commands
from cli.commands import cli
from scripts.seo_audit import AuditResult


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestSchemaArticle:
    def test_prints_script_tag_to_stdout(self, runner: CliRunner) -> None:
        result = runner.invoke(
            cli,
            [
                "schema",
                "article",
                "--headline",
                "Core Web Vitals",
                "--author",
                "Jane Doe",
                "--date-published",
                "2026-01-15",
            ],
        )
        assert result.exit_code == 0
        assert "<script type=\"application/ld+json\">" in result.output
        assert "Core Web Vitals" in result.output

    def test_missing_required_option_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["schema", "article", "--headline", "Only headline"])
        assert result.exit_code != 0

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        output_file = tmp_path / "article.html"
        result = runner.invoke(
            cli,
            [
                "schema",
                "article",
                "--headline",
                "Core Web Vitals",
                "--author",
                "Jane Doe",
                "--date-published",
                "2026-01-15",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Core Web Vitals" in output_file.read_text(encoding="utf-8")


class TestSchemaFaq:
    def test_generates_faq_schema_from_json_file(self, runner: CliRunner, tmp_path: Path) -> None:
        json_file = tmp_path / "faq.json"
        json_file.write_text(json.dumps([["What is SEO?", "Search engine optimization."]]), encoding="utf-8")
        result = runner.invoke(cli, ["schema", "faq", str(json_file)])
        assert result.exit_code == 0
        assert "FAQPage" in result.output

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["schema", "faq", "does-not-exist.json"])
        assert result.exit_code != 0

    def test_empty_pairs_fails_gracefully(self, runner: CliRunner, tmp_path: Path) -> None:
        json_file = tmp_path / "faq.json"
        json_file.write_text("[]", encoding="utf-8")
        result = runner.invoke(cli, ["schema", "faq", str(json_file)])
        assert result.exit_code != 0
        assert "FAQPage schema requires at least one Q&A pair" in result.output


class TestLlmsGenerate:
    def test_generates_llms_txt_from_spec(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            json.dumps(
                {
                    "name": "Example Corp",
                    "summary": "Example Corp builds SEO tools.",
                    "sections": [
                        {
                            "heading": "Documentation",
                            "links": [{"title": "Getting Started", "url": "https://example.com/docs"}],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["llms", "generate", str(spec_file)])
        assert result.exit_code == 0
        assert "# Example Corp" in result.output
        assert "## Documentation" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            json.dumps(
                {
                    "name": "Example Corp",
                    "summary": "Example Corp builds SEO tools.",
                    "sections": [{"heading": "Docs", "links": [{"title": "A", "url": "https://example.com/"}]}],
                }
            ),
            encoding="utf-8",
        )
        output_file = tmp_path / "llms.txt"
        result = runner.invoke(cli, ["llms", "generate", str(spec_file), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Example Corp" in output_file.read_text(encoding="utf-8")

    def test_missing_required_key_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps({"summary": "No name here."}), encoding="utf-8")
        result = runner.invoke(cli, ["llms", "generate", str(spec_file)])
        assert result.exit_code != 0


class TestLlmsAuditCrawlers:
    def test_reports_blocked_crawlers(self, runner: CliRunner, tmp_path: Path) -> None:
        robots_file = tmp_path / "robots.txt"
        robots_file.write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        result = runner.invoke(cli, ["llms", "audit-crawlers", str(robots_file)])
        assert result.exit_code == 0
        assert "AI Crawler Accessibility Report" in result.output
        assert "[BLOCKED]" in result.output

    def test_reports_allowed_crawlers(self, runner: CliRunner, tmp_path: Path) -> None:
        robots_file = tmp_path / "robots.txt"
        robots_file.write_text("User-agent: *\nDisallow: /private/\n", encoding="utf-8")
        result = runner.invoke(cli, ["llms", "audit-crawlers", str(robots_file)])
        assert result.exit_code == 0
        assert "[ALLOWED]" in result.output


class TestAudit:
    def test_reports_audit_result(self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_result = AuditResult(url="https://example.com/", title="Example")

        def fake_audit_url(url: str, *, timeout: float = 10.0) -> AuditResult:
            assert url == "https://example.com/"
            return fake_result

        monkeypatch.setattr(commands, "audit_url", fake_audit_url)
        result = runner.invoke(cli, ["audit", "https://example.com/"])
        assert result.exit_code == 0
        assert "SEO Audit Report" in result.output

    def test_fetch_failure_reported_as_cli_error(self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        def failing_audit_url(url: str, *, timeout: float = 10.0) -> AuditResult:
            raise RuntimeError("connection refused")

        monkeypatch.setattr(commands, "audit_url", failing_audit_url)
        result = runner.invoke(cli, ["audit", "https://example.com/"])
        assert result.exit_code != 0
        assert "connection refused" in result.output


class TestCluster:
    def test_clusters_keywords_from_file(self, runner: CliRunner, tmp_path: Path) -> None:
        keywords_file = tmp_path / "keywords.txt"
        keywords_file.write_text("best running shoes\nbest trail running shoes\n", encoding="utf-8")
        result = runner.invoke(cli, ["cluster", str(keywords_file)])
        assert result.exit_code == 0
        assert "best running shoes" in result.output

    def test_threshold_override_applied(self, runner: CliRunner, tmp_path: Path) -> None:
        keywords_file = tmp_path / "keywords.txt"
        keywords_file.write_text("apples\noranges\n", encoding="utf-8")
        result = runner.invoke(cli, ["cluster", str(keywords_file), "--threshold", "1.0"])
        assert result.exit_code == 0
        assert result.output.count("#") == 2


class TestEntities:
    def test_extracts_entities_from_file(self, runner: CliRunner, tmp_path: Path) -> None:
        content_file = tmp_path / "content.txt"
        content_file.write_text("Jane Doe joined Example Corp as CEO in 2024.", encoding="utf-8")
        result = runner.invoke(cli, ["entities", str(content_file)])
        assert result.exit_code == 0
        assert "Example Corp" in result.output
        assert "salience" in result.output

    def test_reports_gaps_against_compare_file(self, runner: CliRunner, tmp_path: Path) -> None:
        content_file = tmp_path / "own.txt"
        content_file.write_text("Example Corp builds tools.", encoding="utf-8")
        compare_file = tmp_path / "competitor.txt"
        compare_file.write_text("TrailCo builds tools.", encoding="utf-8")
        result = runner.invoke(cli, ["entities", str(content_file), "--compare", str(compare_file)])
        assert result.exit_code == 0
        assert "Entity gaps" in result.output
        assert "TrailCo" in result.output

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["entities", "does-not-exist.txt"])
        assert result.exit_code != 0


class TestLinkSuggestions:
    def test_suggests_links_and_flags_orphans(self, runner: CliRunner, tmp_path: Path) -> None:
        pages_file = tmp_path / "pages.json"
        pages_file.write_text(
            json.dumps(
                [
                    {"url": "/guide", "title": "SEO Guide", "body": "See Core Web Vitals for details."},
                    {"url": "/cwv", "title": "Core Web Vitals", "body": ""},
                ]
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["link-suggestions", str(pages_file)])
        assert result.exit_code == 0
        assert "/guide -> /cwv" in result.output
        assert "Orphan pages" in result.output

    def test_missing_required_key_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        pages_file = tmp_path / "pages.json"
        pages_file.write_text(json.dumps([{"title": "No URL here"}]), encoding="utf-8")
        result = runner.invoke(cli, ["link-suggestions", str(pages_file)])
        assert result.exit_code != 0

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["link-suggestions", "does-not-exist.json"])
        assert result.exit_code != 0


class TestSitemap:
    def test_writes_sitemap_file(self, runner: CliRunner, tmp_path: Path) -> None:
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com/\nhttps://example.com/about\n", encoding="utf-8")
        output_file = tmp_path / "sitemap.xml"
        result = runner.invoke(cli, ["sitemap", str(urls_file), str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "<urlset" in output_file.read_text(encoding="utf-8")

    def test_invalid_url_reported_as_cli_error(self, runner: CliRunner, tmp_path: Path) -> None:
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("not-a-url\n", encoding="utf-8")
        output_file = tmp_path / "sitemap.xml"
        result = runner.invoke(cli, ["sitemap", str(urls_file), str(output_file)])
        assert result.exit_code != 0


class TestRobots:
    def test_writes_robots_file(self, runner: CliRunner, tmp_path: Path) -> None:
        output_file = tmp_path / "robots.txt"
        result = runner.invoke(cli, ["robots", str(output_file), "--disallow", "/admin/"])
        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "Disallow: /admin/" in content

    def test_config_domain_supplies_default_sitemap(self, runner: CliRunner, tmp_path: Path) -> None:
        config_file = tmp_path / "seo-playbook.yml"
        config_file.write_text("domain: example.com\n", encoding="utf-8")
        output_file = tmp_path / "robots.txt"
        result = runner.invoke(cli, ["--config", str(config_file), "robots", str(output_file)])
        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "Sitemap: https://example.com/sitemap.xml" in content

    def test_explicit_sitemap_overrides_config(self, runner: CliRunner, tmp_path: Path) -> None:
        config_file = tmp_path / "seo-playbook.yml"
        config_file.write_text("domain: example.com\n", encoding="utf-8")
        output_file = tmp_path / "robots.txt"
        result = runner.invoke(
            cli,
            [
                "--config",
                str(config_file),
                "robots",
                str(output_file),
                "--sitemap-url",
                "https://other.com/sitemap.xml",
            ],
        )
        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "https://other.com/sitemap.xml" in content
        assert "example.com" not in content


class TestMeta:
    def test_title_only(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["meta", "--title", "Core Web Vitals"])
        assert result.exit_code == 0
        assert "Core Web Vitals" in result.output

    def test_title_and_description(self, runner: CliRunner) -> None:
        result = runner.invoke(
            cli,
            [
                "meta",
                "--title",
                "Core Web Vitals",
                "--description",
                "A concise summary of the page content that fits within limits here today.",
            ],
        )
        assert result.exit_code == 0
        assert "Title (" in result.output
        assert "Description (" in result.output

    def test_no_title_or_description_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["meta"])
        assert result.exit_code != 0

    def test_config_brand_applied_when_not_overridden(self, runner: CliRunner, tmp_path: Path) -> None:
        config_file = tmp_path / "seo-playbook.yml"
        config_file.write_text("brand: Example Corp\n", encoding="utf-8")
        result = runner.invoke(cli, ["--config", str(config_file), "meta", "--title", "Core Web Vitals"])
        assert result.exit_code == 0
        assert "Example Corp" in result.output


class TestConfigOption:
    def test_missing_config_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--config", "does-not-exist.yml", "meta", "--title", "Test"])
        assert result.exit_code != 0
