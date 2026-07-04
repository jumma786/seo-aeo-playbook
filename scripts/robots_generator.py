"""Generate robots.txt content from structured crawl rules.

Supports per-user-agent allow/disallow rules, crawl-delay, sitemap
references, and validation against common mistakes (e.g. accidentally
blocking the entire site).

Example:
    >>> from scripts.robots_generator import RobotsGroup, generate_robots_txt
    >>> group = RobotsGroup(user_agent="*", disallow=["/admin/"])
    >>> print(generate_robots_txt([group], sitemap_urls=["https://example.com/sitemap.xml"]))
    User-agent: *
    Disallow: /admin/
    <BLANKLINE>
    Sitemap: https://example.com/sitemap.xml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class RobotsValidationError(ValueError):
    """Raised when a robots.txt rule or ruleset is invalid."""


@dataclass
class RobotsGroup:
    """A single ``User-agent`` block of allow/disallow rules."""

    user_agent: str
    disallow: list[str] = field(default_factory=list)
    allow: list[str] = field(default_factory=list)
    crawl_delay: float | None = None

    def __post_init__(self) -> None:
        if not self.user_agent.strip():
            raise RobotsValidationError("user_agent must not be empty")
        for path in (*self.disallow, *self.allow):
            if path and not path.startswith("/") and path != "*":
                raise RobotsValidationError(f"Path rules must start with '/', got {path!r}")

    def to_lines(self) -> list[str]:
        lines = [f"User-agent: {self.user_agent}"]
        for path in self.disallow:
            lines.append(f"Disallow: {path}")
        for path in self.allow:
            lines.append(f"Allow: {path}")
        if self.crawl_delay is not None:
            lines.append(f"Crawl-delay: {self.crawl_delay:g}")
        return lines


def generate_robots_txt(
    groups: list[RobotsGroup],
    *,
    sitemap_urls: list[str] | None = None,
) -> str:
    """Render a complete robots.txt document from rule groups.

    Args:
        groups: One or more :class:`RobotsGroup` rule sets, each for a
            distinct user-agent (or ``*`` for all crawlers).
        sitemap_urls: Absolute URLs of XML sitemaps to advertise.

    Returns:
        The rendered robots.txt content as a string.

    Raises:
        RobotsValidationError: If groups is empty.
    """
    if not groups:
        raise RobotsValidationError("At least one RobotsGroup is required")

    _warn_if_blocks_everything(groups)

    blocks = ["\n".join(group.to_lines()) for group in groups]
    content = "\n\n".join(blocks)

    if sitemap_urls:
        sitemap_lines = "\n".join(f"Sitemap: {url}" for url in sitemap_urls)
        content = f"{content}\n\n{sitemap_lines}"

    return content + "\n"


def _warn_if_blocks_everything(groups: list[RobotsGroup]) -> None:
    for group in groups:
        if group.user_agent == "*" and "/" in group.disallow:
            logger.warning(
                "RobotsGroup for user-agent '*' disallows '/', which blocks the entire "
                "site from all crawlers. Confirm this is intentional."
            )


def parse_robots_txt(content: str) -> list[RobotsGroup]:
    """Parse an existing robots.txt document back into structured groups.

    Args:
        content: Raw robots.txt file content.

    Returns:
        A list of :class:`RobotsGroup` reconstructed from the file, in
        the order they appeared. Sitemap directives are ignored (use a
        dedicated sitemap parser if needed).
    """
    groups: list[RobotsGroup] = []
    current: RobotsGroup | None = None

    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        directive, _, value = line.partition(":")
        directive = directive.strip().lower()
        value = value.strip()

        if directive == "user-agent":
            current = RobotsGroup(user_agent=value)
            groups.append(current)
        elif current is None:
            continue
        elif directive == "disallow" and value:
            current.disallow.append(value)
        elif directive == "allow" and value:
            current.allow.append(value)
        elif directive == "crawl-delay":
            try:
                current.crawl_delay = float(value)
            except ValueError:
                logger.warning("Skipping unparseable Crawl-delay value: %r", value)

    return groups


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.robots_generator output.txt --sitemap URL``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate a robots.txt file.")
    parser.add_argument("output_file", help="Path to write the generated robots.txt")
    parser.add_argument("--disallow", action="append", default=[], help="Path to disallow for all crawlers")
    parser.add_argument("--sitemap", action="append", default=[], help="Sitemap URL to advertise")
    args = parser.parse_args(argv)

    try:
        group = RobotsGroup(user_agent="*", disallow=args.disallow)
        content = generate_robots_txt([group], sitemap_urls=args.sitemap or None)
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(content)
    except (OSError, RobotsValidationError) as exc:
        logging.error("robots.txt generation failed: %s", exc)
        return 1

    logging.info("Wrote robots.txt to %s", args.output_file)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
