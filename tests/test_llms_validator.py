"""Unit tests for scripts.llms_validator."""

from __future__ import annotations

from scripts.llms_validator import AI_CRAWLERS, audit_robots_txt, format_report


class TestAuditRobotsTxt:
    def test_permissive_robots_allows_all_crawlers(self) -> None:
        statuses = audit_robots_txt("User-agent: *\nDisallow: /private/\n")
        assert len(statuses) == len(AI_CRAWLERS)
        assert all(status.allowed for status in statuses)
        assert all(status.blocked_by is None for status in statuses)

    def test_blanket_disallow_blocks_crawlers_without_dedicated_rule(self) -> None:
        statuses = audit_robots_txt("User-agent: *\nDisallow: /\n")
        assert all(not status.allowed for status in statuses)
        assert all(status.blocked_by == "*" for status in statuses)
        assert all(status.warning is not None for status in statuses)

    def test_dedicated_disallow_blocks_only_that_crawler(self) -> None:
        statuses = audit_robots_txt("User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nDisallow: /private/\n")
        by_crawler = {status.crawler: status for status in statuses}
        assert by_crawler["GPTBot"].allowed is False
        assert by_crawler["GPTBot"].blocked_by == "GPTBot"
        assert by_crawler["ClaudeBot"].allowed is True

    def test_dedicated_allow_overrides_blanket_block(self) -> None:
        statuses = audit_robots_txt("User-agent: *\nDisallow: /\n\nUser-agent: ClaudeBot\nAllow: /\n")
        by_crawler = {status.crawler: status for status in statuses}
        assert by_crawler["ClaudeBot"].allowed is True
        assert by_crawler["GPTBot"].allowed is False

    def test_no_rules_allows_everything(self) -> None:
        statuses = audit_robots_txt("")
        assert all(status.allowed for status in statuses)


class TestFormatReport:
    def test_report_includes_summary_line(self) -> None:
        statuses = audit_robots_txt("User-agent: *\nDisallow: /\n")
        report = format_report(statuses)
        assert f"{len(AI_CRAWLERS)} of {len(AI_CRAWLERS)} known AI crawlers are blocked." in report
        assert "[BLOCKED]" in report

    def test_report_shows_allowed_crawlers(self) -> None:
        statuses = audit_robots_txt("")
        report = format_report(statuses)
        assert "0 of" in report
        assert "[ALLOWED]" in report
