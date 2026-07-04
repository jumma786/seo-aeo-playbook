"""Unit tests for cli.commands (the seo-playbook CLI)."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

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


class TestSchemaValidate:
    def test_valid_json_schema_exits_zero(self, runner: CliRunner, tmp_path: Path) -> None:
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(
            json.dumps(
                {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": "Example Corp",
                    "url": "https://example.com",
                }
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["schema", "validate", str(schema_file)])
        assert result.exit_code == 0
        assert "OK - no issues found" in result.output

    def test_invalid_json_schema_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": "Hi"}), encoding="utf-8")
        result = runner.invoke(cli, ["schema", "validate", str(schema_file)])
        assert result.exit_code == 1
        assert "[ERROR]" in result.output

    def test_malformed_json_file_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        schema_file = tmp_path / "schema.json"
        schema_file.write_text("{not valid json", encoding="utf-8")
        result = runner.invoke(cli, ["schema", "validate", str(schema_file)])
        assert result.exit_code != 0

    def test_validates_html_file(self, runner: CliRunner, tmp_path: Path) -> None:
        html_file = tmp_path / "page.html"
        html_file.write_text(
            '<script type="application/ld+json">{"@context": "https://schema.org", '
            '"@type": "Organization", "name": "Example Corp", "url": "https://example.com"}</script>',
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["schema", "validate", str(html_file)])
        assert result.exit_code == 0
        assert "OK - no issues found" in result.output


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


class TestPageSpeed:
    def test_reports_audit_result(self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        from scripts.page_speed import PageSpeedResult

        fake_result = PageSpeedResult(url="https://example.com/")

        def fake_audit(url: str, *, timeout: float = 10.0) -> PageSpeedResult:
            assert url == "https://example.com/"
            return fake_result

        monkeypatch.setattr(commands, "audit_url_performance", fake_audit)
        result = runner.invoke(cli, ["page-speed", "https://example.com/"])
        assert result.exit_code == 0
        assert "Page Speed Report" in result.output

    def test_fetch_failure_reported_as_cli_error(self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        def failing_audit(url: str, *, timeout: float = 10.0):
            raise RuntimeError("connection refused")

        monkeypatch.setattr(commands, "audit_url_performance", failing_audit)
        result = runner.invoke(cli, ["page-speed", "https://example.com/"])
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


class TestGeoScore:
    def test_scores_markdown_content(self, runner: CliRunner, tmp_path: Path) -> None:
        content_file = tmp_path / "content.md"
        content_file.write_text(
            "Core Web Vitals is a set of three metrics — LCP, INP, and CLS — introduced by Google in 2020 "
            "to measure loading speed, responsiveness, and visual stability.",
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["geo-score", str(content_file)])
        assert result.exit_code == 0
        assert "GEO Citability Report" in result.output

    def test_scores_html_content(self, runner: CliRunner, tmp_path: Path) -> None:
        content_file = tmp_path / "page.html"
        content_file.write_text("<html><body><p>A short paragraph.</p></body></html>", encoding="utf-8")
        result = runner.invoke(cli, ["geo-score", str(content_file)])
        assert result.exit_code == 0
        assert "1 passage(s)" in result.output

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["geo-score", "does-not-exist.md"])
        assert result.exit_code != 0


class TestFaq:
    GOOD_ANSWER = "SEO is the practice of optimizing a website so it ranks higher in organic search engine results pages."

    def test_generates_markdown_and_schema(self, runner: CliRunner, tmp_path: Path) -> None:
        faq_file = tmp_path / "faq.json"
        faq_file.write_text(
            json.dumps([{"question": "What is SEO?", "answer": self.GOOD_ANSWER}]), encoding="utf-8"
        )
        result = runner.invoke(cli, ["faq", str(faq_file)])
        assert result.exit_code == 0
        assert "## Frequently Asked Questions" in result.output
        assert "FAQPage" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        faq_file = tmp_path / "faq.json"
        faq_file.write_text(
            json.dumps([{"question": "What is SEO?", "answer": self.GOOD_ANSWER}]), encoding="utf-8"
        )
        output_file = tmp_path / "faq.md"
        result = runner.invoke(cli, ["faq", str(faq_file), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "FAQPage" in output_file.read_text(encoding="utf-8")

    def test_validation_warnings_shown_but_not_fatal(self, runner: CliRunner, tmp_path: Path) -> None:
        faq_file = tmp_path / "faq.json"
        faq_file.write_text(json.dumps([{"question": "What is SEO", "answer": "Short."}]), encoding="utf-8")
        result = runner.invoke(cli, ["faq", str(faq_file)])
        assert result.exit_code == 0
        assert "FAQ Validation Report" in result.output

    def test_empty_list_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        faq_file = tmp_path / "faq.json"
        faq_file.write_text("[]", encoding="utf-8")
        result = runner.invoke(cli, ["faq", str(faq_file)])
        assert result.exit_code != 0


class TestBlogScaffold:
    def _spec_dict(self, **overrides: object) -> dict:
        spec = {
            "title": "Core Web Vitals Explained: A Complete Guide",
            "slug": "core-web-vitals-explained",
            "author_name": "Jane Doe",
            "date_published": "2026-01-15",
            "primary_keyword": "core web vitals",
            "related_keywords": ["largest contentful paint guide"],
            "target_word_count": 1000,
        }
        spec.update(overrides)
        return spec

    def test_generates_scaffold_from_spec(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(self._spec_dict()), encoding="utf-8")
        result = runner.invoke(cli, ["blog-scaffold", str(spec_file)])
        assert result.exit_code == 0
        assert "Core Web Vitals Explained" in result.output
        assert "Article" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(self._spec_dict()), encoding="utf-8")
        output_file = tmp_path / "post.md"
        result = runner.invoke(cli, ["blog-scaffold", str(spec_file), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()

    def test_missing_required_key_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps({"primary_keyword": "core web vitals"}), encoding="utf-8")
        result = runner.invoke(cli, ["blog-scaffold", str(spec_file)])
        assert result.exit_code != 0


class TestContentBrief:
    def test_generates_brief_from_spec(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            json.dumps(
                {
                    "primary_keyword": "core web vitals",
                    "related_keywords": ["largest contentful paint guide"],
                    "target_word_count": 1000,
                }
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["content-brief", str(spec_file)])
        assert result.exit_code == 0
        assert "Content Brief: core web vitals" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps({"primary_keyword": "core web vitals", "related_keywords": []}), encoding="utf-8")
        output_file = tmp_path / "brief.md"
        result = runner.invoke(cli, ["content-brief", str(spec_file), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "core web vitals" in output_file.read_text(encoding="utf-8")

    def test_missing_primary_keyword_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps({"related_keywords": []}), encoding="utf-8")
        result = runner.invoke(cli, ["content-brief", str(spec_file)])
        assert result.exit_code != 0


class TestKeywordMap:
    def test_audit_reports_cannibalization(self, runner: CliRunner, tmp_path: Path) -> None:
        mappings_file = tmp_path / "mappings.json"
        mappings_file.write_text(
            json.dumps(
                [
                    {"keyword": "running shoes", "url": "/running-shoes"},
                    {"keyword": "running shoes", "url": "/best-running-shoes"},
                ]
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["keyword-map", "audit", str(mappings_file)])
        assert result.exit_code == 0
        assert "1 issue(s) found" in result.output
        assert "running shoes" in result.output

    def test_audit_missing_key_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        mappings_file = tmp_path / "mappings.json"
        mappings_file.write_text(json.dumps([{"keyword": "running shoes"}]), encoding="utf-8")
        result = runner.invoke(cli, ["keyword-map", "audit", str(mappings_file)])
        assert result.exit_code != 0

    def test_suggest_maps_keywords_to_pages(self, runner: CliRunner, tmp_path: Path) -> None:
        keywords_file = tmp_path / "keywords.txt"
        keywords_file.write_text("core web vitals\n", encoding="utf-8")
        pages_file = tmp_path / "pages.json"
        pages_file.write_text(json.dumps({"/cwv": "Core Web Vitals Guide"}), encoding="utf-8")
        result = runner.invoke(cli, ["keyword-map", "suggest", str(keywords_file), str(pages_file)])
        assert result.exit_code == 0
        assert "/cwv" in result.output

    def test_suggest_reports_unmapped(self, runner: CliRunner, tmp_path: Path) -> None:
        keywords_file = tmp_path / "keywords.txt"
        keywords_file.write_text("totally unrelated keyword\n", encoding="utf-8")
        pages_file = tmp_path / "pages.json"
        pages_file.write_text(json.dumps({"/cwv": "Core Web Vitals Guide"}), encoding="utf-8")
        result = runner.invoke(cli, ["keyword-map", "suggest", str(keywords_file), str(pages_file)])
        assert result.exit_code == 0
        assert "Unmapped keywords" in result.output


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


class TestCheckLinks:
    def test_ok_links_from_text_file(self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import requests

        monkeypatch.setattr(requests, "head", lambda url, **kwargs: SimpleNamespace(status_code=200, url=url, history=[]))
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com/a\nhttps://example.com/b\n", encoding="utf-8")
        result = runner.invoke(cli, ["check-links", str(urls_file)])
        assert result.exit_code == 0
        assert "0 broken" in result.output

    def test_broken_link_exits_nonzero(self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import requests

        monkeypatch.setattr(requests, "head", lambda url, **kwargs: SimpleNamespace(status_code=404, url=url, history=[]))
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com/missing\n", encoding="utf-8")
        result = runner.invoke(cli, ["check-links", str(urls_file)])
        assert result.exit_code == 1
        assert "Broken links" in result.output

    def test_html_input_extracts_and_checks_links(
        self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import requests

        monkeypatch.setattr(requests, "head", lambda url, **kwargs: SimpleNamespace(status_code=200, url=url, history=[]))
        html_file = tmp_path / "page.html"
        html_file.write_text('<a href="/about">About</a>', encoding="utf-8")
        result = runner.invoke(cli, ["check-links", str(html_file), "--base-url", "https://example.com/"])
        assert result.exit_code == 0
        assert "1 link(s) checked" in result.output

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["check-links", "does-not-exist.txt"])
        assert result.exit_code != 0


class TestSiteAudit:
    def test_audits_pages_from_file(self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import requests

        fake_response = SimpleNamespace(
            text=(
                '<html><head><title>A Well Optimized Page About Testing</title>'
                '<meta name="description" content="A sufficiently long meta description that satisfies the recommended length guidance."></head>'
                "<body><h1>Testing</h1><p>" + ("word " * 320) + "</p></body></html>"
            ),
            elapsed=timedelta(seconds=0.1),
            raise_for_status=lambda: None,
        )
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: fake_response)

        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com/\n", encoding="utf-8")
        result = runner.invoke(cli, ["site-audit", str(urls_file)])
        assert result.exit_code == 0
        assert "Site Audit Report" in result.output

    def test_fetch_failure_exits_nonzero(self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import requests

        def fail(url: str, **kwargs: object) -> None:
            raise requests.ConnectionError("connection refused")

        monkeypatch.setattr(requests, "get", fail)
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://example.com/down\n", encoding="utf-8")
        result = runner.invoke(cli, ["site-audit", str(urls_file)])
        assert result.exit_code == 1
        assert "FAILED TO FETCH" in result.output

    def test_missing_file_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["site-audit", "does-not-exist.txt"])
        assert result.exit_code != 0


class TestLocationPages:
    GOOD_CONTENT = " ".join(["Our Austin location offers"] * 15)

    def _spec_dict(self, slug: str, unique_content: str) -> dict:
        return {
            "url_slug": slug,
            "nap": {
                "name": "Example Dental",
                "street_address": "1 Main St",
                "address_locality": "Austin",
                "address_region": "TX",
                "postal_code": "78701",
                "telephone": "512-555-0100",
            },
            "hours": {"Monday": "9am-5pm"},
            "unique_content": unique_content,
        }

    def test_generates_location_pages(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(
            json.dumps([self._spec_dict("austin-tx", self.GOOD_CONTENT + " austin unique")]), encoding="utf-8"
        )
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["location-pages", str(specs_file), str(output_dir)])
        assert result.exit_code == 0
        assert (output_dir / "austin-tx.md").exists()
        assert "Example Dental" in (output_dir / "austin-tx.md").read_text(encoding="utf-8")

    def test_quality_gate_failure_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(json.dumps([self._spec_dict("austin-tx", "Too short.")]), encoding="utf-8")
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["location-pages", str(specs_file), str(output_dir)])
        assert result.exit_code != 0

    def test_skip_quality_gates_flag_bypasses_check(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(json.dumps([self._spec_dict("austin-tx", "Too short.")]), encoding="utf-8")
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["location-pages", str(specs_file), str(output_dir), "--skip-quality-gates"])
        assert result.exit_code == 0
        assert (output_dir / "austin-tx.md").exists()

    def test_missing_file_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["location-pages", "does-not-exist.json", str(tmp_path / "out")])
        assert result.exit_code != 0


class TestServicePages:
    GOOD_CONTENT = (
        "Our licensed plumbers serve the greater Austin area with 24/7 emergency response, transparent "
        "flat-rate pricing, and a satisfaction guarantee backed by over a decade of local service experience. "
        "We specialize in burst pipe repair, water heater installation, and drain cleaning for homes and "
        "small businesses throughout the metro area, with most technicians arriving within ninety minutes."
    )

    def _spec_dict(self, slug: str, unique_content: str) -> dict:
        return {
            "url_slug": slug,
            "business_name": "Example Plumbing",
            "service_name": "Emergency Plumbing",
            "area_served": "Austin, TX",
            "telephone": "512-555-0100",
            "unique_content": unique_content,
        }

    def test_generates_service_pages(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(json.dumps([self._spec_dict("austin-tx-plumbing", self.GOOD_CONTENT)]), encoding="utf-8")
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["service-pages", str(specs_file), str(output_dir)])
        assert result.exit_code == 0
        content = (output_dir / "austin-tx-plumbing.md").read_text(encoding="utf-8")
        assert "Example Plumbing" in content
        assert "streetAddress" not in content

    def test_quality_gate_failure_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(json.dumps([self._spec_dict("austin-tx-plumbing", "Too short.")]), encoding="utf-8")
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["service-pages", str(specs_file), str(output_dir)])
        assert result.exit_code != 0

    def test_skip_quality_gates_flag_bypasses_check(self, runner: CliRunner, tmp_path: Path) -> None:
        specs_file = tmp_path / "specs.json"
        specs_file.write_text(json.dumps([self._spec_dict("austin-tx-plumbing", "Too short.")]), encoding="utf-8")
        output_dir = tmp_path / "out"
        result = runner.invoke(cli, ["service-pages", str(specs_file), str(output_dir), "--skip-quality-gates"])
        assert result.exit_code == 0

    def test_missing_file_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["service-pages", "does-not-exist.json", str(tmp_path / "out")])
        assert result.exit_code != 0


class TestGenerateReadme:
    SAMPLE_CHAPTER = (
        "# Chapter 1: Example Chapter\n\n**Version:** 1.0\n\n---\n\n# Table of Contents\n\n1. Intro\n\n---\n\n"
        "# 1. Intro\n\nThis chapter covers the basics of the topic. More detail follows.\n"
    )

    def test_generates_readme_from_spec(self, runner: CliRunner, tmp_path: Path) -> None:
        book_dir = tmp_path / "book"
        book_dir.mkdir()
        (book_dir / "chapter-01.md").write_text(self.SAMPLE_CHAPTER, encoding="utf-8")
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            json.dumps(
                {
                    "title": "The Example Book",
                    "description": "A short description of the book.",
                    "book_directory": str(book_dir),
                }
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cli, ["generate-readme", str(spec_file)])
        assert result.exit_code == 0
        assert "# The Example Book" in result.output
        assert "chapter-01.md" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        book_dir = tmp_path / "book"
        book_dir.mkdir()
        (book_dir / "chapter-01.md").write_text(self.SAMPLE_CHAPTER, encoding="utf-8")
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            json.dumps({"title": "The Example Book", "description": "A description.", "book_directory": str(book_dir)}),
            encoding="utf-8",
        )
        output_file = tmp_path / "README.md"
        result = runner.invoke(cli, ["generate-readme", str(spec_file), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()

    def test_missing_required_key_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps({"description": "A description."}), encoding="utf-8")
        result = runner.invoke(cli, ["generate-readme", str(spec_file)])
        assert result.exit_code != 0


class TestGenerateToc:
    SAMPLE_CHAPTER = (
        "# Chapter 1: Example Chapter\n\n**Version:** 1.0\n\n---\n\n# Table of Contents\n\n1. Intro\n\n---\n\n"
        "# 1. Intro\n\nThis chapter covers the basics of the topic. More detail follows.\n"
    )

    def test_generates_toc_from_directory(self, runner: CliRunner, tmp_path: Path) -> None:
        (tmp_path / "chapter-01.md").write_text(self.SAMPLE_CHAPTER, encoding="utf-8")
        result = runner.invoke(cli, ["generate-toc", str(tmp_path)])
        assert result.exit_code == 0
        assert "| # | Chapter | Focus |" in result.output
        assert "chapter-01.md" in result.output

    def test_writes_to_output_file(self, runner: CliRunner, tmp_path: Path) -> None:
        (tmp_path / "chapter-01.md").write_text(self.SAMPLE_CHAPTER, encoding="utf-8")
        output_file = tmp_path / "toc.md"
        result = runner.invoke(cli, ["generate-toc", str(tmp_path), "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "chapter-01.md" in output_file.read_text(encoding="utf-8")

    def test_no_chapter_files_fails(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(cli, ["generate-toc", str(tmp_path)])
        assert result.exit_code != 0

    def test_missing_directory_fails(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["generate-toc", "does-not-exist-dir"])
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
