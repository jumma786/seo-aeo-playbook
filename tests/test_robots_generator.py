"""Unit tests for scripts.robots_generator."""

from __future__ import annotations

import logging

import pytest

from scripts.robots_generator import (
    RobotsGroup,
    RobotsValidationError,
    generate_robots_txt,
    parse_robots_txt,
)


class TestRobotsGroup:
    def test_empty_user_agent_rejected(self) -> None:
        with pytest.raises(RobotsValidationError):
            RobotsGroup(user_agent="  ")

    def test_path_must_start_with_slash(self) -> None:
        with pytest.raises(RobotsValidationError):
            RobotsGroup(user_agent="*", disallow=["admin"])

    def test_to_lines_includes_crawl_delay(self) -> None:
        group = RobotsGroup(user_agent="*", disallow=["/admin/"], crawl_delay=1.5)
        lines = group.to_lines()
        assert "Crawl-delay: 1.5" in lines


class TestGenerateRobotsTxt:
    def test_basic_group_rendered(self) -> None:
        content = generate_robots_txt([RobotsGroup(user_agent="*", disallow=["/admin/"])])
        assert "User-agent: *" in content
        assert "Disallow: /admin/" in content
        assert content.endswith("\n")

    def test_sitemap_urls_appended(self) -> None:
        content = generate_robots_txt(
            [RobotsGroup(user_agent="*", disallow=[])],
            sitemap_urls=["https://example.com/sitemap.xml"],
        )
        assert "Sitemap: https://example.com/sitemap.xml" in content

    def test_multiple_groups_separated_by_blank_line(self) -> None:
        content = generate_robots_txt(
            [
                RobotsGroup(user_agent="*", disallow=["/admin/"]),
                RobotsGroup(user_agent="Googlebot", disallow=[], allow=["/"]),
            ]
        )
        assert "User-agent: *" in content
        assert "User-agent: Googlebot" in content
        assert "\n\n" in content

    def test_empty_groups_raises(self) -> None:
        with pytest.raises(RobotsValidationError):
            generate_robots_txt([])

    def test_disallow_root_for_wildcard_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            generate_robots_txt([RobotsGroup(user_agent="*", disallow=["/"])])
        assert any("blocks the entire site" in record.message for record in caplog.records)


class TestParseRobotsTxt:
    def test_round_trip_basic(self) -> None:
        original = generate_robots_txt([RobotsGroup(user_agent="*", disallow=["/admin/"], allow=["/public/"])])
        parsed = parse_robots_txt(original)
        assert len(parsed) == 1
        assert parsed[0].user_agent == "*"
        assert parsed[0].disallow == ["/admin/"]
        assert parsed[0].allow == ["/public/"]

    def test_ignores_comments_and_blank_lines(self) -> None:
        content = "# comment\n\nUser-agent: *\nDisallow: /admin/\n"
        parsed = parse_robots_txt(content)
        assert len(parsed) == 1
        assert parsed[0].disallow == ["/admin/"]

    def test_multiple_user_agent_blocks(self) -> None:
        content = "User-agent: *\nDisallow: /admin/\n\nUser-agent: Googlebot\nAllow: /\n"
        parsed = parse_robots_txt(content)
        assert [g.user_agent for g in parsed] == ["*", "Googlebot"]

    def test_crawl_delay_parsed_as_float(self) -> None:
        content = "User-agent: *\nCrawl-delay: 2\n"
        parsed = parse_robots_txt(content)
        assert parsed[0].crawl_delay == 2.0

    def test_empty_content_returns_no_groups(self) -> None:
        assert parse_robots_txt("") == []
