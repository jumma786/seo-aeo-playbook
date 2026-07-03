"""Audit robots.txt content for AI crawler accessibility.

Checks the AI crawler directory documented in
``docs/books/complete/aeo/chapter-08.md`` section 7 against a site's
robots.txt rules, per the audit steps in section 8: for each known AI
crawler, is it explicitly allowed/disallowed, or unintentionally caught by
a blanket rule (e.g. ``User-agent: * / Disallow: /``)?

This is a heuristic accessibility check, not a full robots.txt precedence
resolver: it flags a user-agent group as "blocks everything" only when it
disallows ``/`` with no matching top-level ``Allow: /`` carve-out.

Example:
    >>> from scripts.llms_validator import audit_robots_txt
    >>> statuses = audit_robots_txt("User-agent: *\\nDisallow: /private/\\n")
    >>> all(status.allowed for status in statuses)
    True
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from scripts.robots_generator import RobotsGroup, parse_robots_txt

logger = logging.getLogger(__name__)

# The AI crawler directory from docs/books/complete/aeo/chapter-08.md section 7.
# Treat as a snapshot to verify against current vendor documentation, not a
# permanent reference (crawler lists change as vendors add new bots).
AI_CRAWLERS: dict[str, str] = {
    "GPTBot": "OpenAI - model training data",
    "OAI-SearchBot": "OpenAI - ChatGPT Search retrieval",
    "ChatGPT-User": "OpenAI - live fetch during active user conversations",
    "Google-Extended": "Google - Gemini/Vertex AI training and grounding",
    "PerplexityBot": "Perplexity - search retrieval",
    "ClaudeBot": "Anthropic - crawling for training and search grounding",
    "Bingbot": "Microsoft - Bing indexing, powers Copilot in part",
    "CCBot": "Common Crawl - open dataset used by many downstream LLM developers",
}


@dataclass
class CrawlerStatus:
    """The accessibility status of a single AI crawler against a robots.txt."""

    crawler: str
    purpose: str
    allowed: bool
    blocked_by: str | None = None
    warning: str | None = None


def _group_blocks_everything(group: RobotsGroup) -> bool:
    return "/" in group.disallow and "/" not in group.allow


def audit_crawler_access(groups: list[RobotsGroup]) -> list[CrawlerStatus]:
    """Check each known AI crawler's access against a parsed robots.txt ruleset.

    Args:
        groups: Parsed ``User-agent`` rule groups, typically from
            :func:`scripts.robots_generator.parse_robots_txt`.

    Returns:
        A :class:`CrawlerStatus` for every crawler in :data:`AI_CRAWLERS`, in
        the order they're listed there.
    """
    by_agent = {group.user_agent: group for group in groups}
    wildcard = by_agent.get("*")

    statuses = []
    for crawler, purpose in AI_CRAWLERS.items():
        specific = by_agent.get(crawler)
        if specific is not None:
            blocked = _group_blocks_everything(specific)
            statuses.append(
                CrawlerStatus(
                    crawler=crawler,
                    purpose=purpose,
                    allowed=not blocked,
                    blocked_by=crawler if blocked else None,
                )
            )
        elif wildcard is not None and _group_blocks_everything(wildcard):
            statuses.append(
                CrawlerStatus(
                    crawler=crawler,
                    purpose=purpose,
                    allowed=False,
                    blocked_by="*",
                    warning=(
                        f"{crawler} has no dedicated rule and is blocked by the "
                        "blanket 'User-agent: *' Disallow: / rule"
                    ),
                )
            )
        else:
            statuses.append(CrawlerStatus(crawler=crawler, purpose=purpose, allowed=True))

    blocked_count = sum(1 for status in statuses if not status.allowed)
    logger.info("Audited %d AI crawlers: %d blocked", len(statuses), blocked_count)
    return statuses


def audit_robots_txt(content: str) -> list[CrawlerStatus]:
    """Parse robots.txt content and audit AI crawler accessibility against it.

    Args:
        content: Raw robots.txt file content.

    Returns:
        A list of :class:`CrawlerStatus`, one per known AI crawler.
    """
    return audit_crawler_access(parse_robots_txt(content))


def format_report(statuses: list[CrawlerStatus]) -> str:
    """Render a list of :class:`CrawlerStatus` as a human-readable text report."""
    lines = ["AI Crawler Accessibility Report", ""]
    for status in statuses:
        state = "ALLOWED" if status.allowed else "BLOCKED"
        lines.append(f"[{state}] {status.crawler} ({status.purpose})")
        if status.blocked_by:
            lines.append(f"    blocked by rule for user-agent: {status.blocked_by}")
        if status.warning:
            lines.append(f"    warning: {status.warning}")

    blocked_count = sum(1 for status in statuses if not status.allowed)
    lines.append("")
    lines.append(f"{blocked_count} of {len(statuses)} known AI crawlers are blocked.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.llms_validator robots.txt``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Audit a robots.txt file for AI crawler accessibility.")
    parser.add_argument("robots_file", help="Path to a robots.txt file to audit")
    args = parser.parse_args(argv)

    try:
        with open(args.robots_file, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        logging.error("Could not read %s: %s", args.robots_file, exc)
        return 1

    statuses = audit_robots_txt(content)
    print(format_report(statuses))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
