"""Generate XML sitemaps (and sitemap indexes) from a list of URLs.

Follows the sitemaps.org protocol and Google's 50,000-URL / 50MB-per-file
limits, automatically splitting large URL sets across multiple sitemap
files with a generated sitemap index.

Example:
    >>> from scripts.sitemap_generator import SitemapURL, generate_sitemap
    >>> xml = generate_sitemap([SitemapURL(loc="https://example.com/")])
    >>> xml.startswith("<?xml")
    True
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from xml.sax.saxutils import escape

logger = logging.getLogger(__name__)

MAX_URLS_PER_SITEMAP = 50_000
VALID_CHANGE_FREQUENCIES = frozenset(
    {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
)

_SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class SitemapValidationError(ValueError):
    """Raised when a sitemap URL or set of URLs is invalid."""


@dataclass
class SitemapURL:
    """A single ``<url>`` entry in an XML sitemap."""

    loc: str
    lastmod: str | date | datetime | None = None
    changefreq: str | None = None
    priority: float | None = None

    def __post_init__(self) -> None:
        if not self.loc or not self.loc.startswith(("http://", "https://")):
            raise SitemapValidationError(f"loc must be an absolute URL, got {self.loc!r}")
        if self.changefreq is not None and self.changefreq not in VALID_CHANGE_FREQUENCIES:
            raise SitemapValidationError(
                f"Invalid changefreq {self.changefreq!r}; must be one of {sorted(VALID_CHANGE_FREQUENCIES)}"
            )
        if self.priority is not None and not 0.0 <= self.priority <= 1.0:
            raise SitemapValidationError(f"priority must be between 0.0 and 1.0, got {self.priority}")

    def _lastmod_str(self) -> str | None:
        if self.lastmod is None:
            return None
        if isinstance(self.lastmod, (date, datetime)):
            return self.lastmod.strftime("%Y-%m-%d")
        return str(self.lastmod)

    def to_xml(self) -> str:
        """Render this URL entry as a ``<url>...</url>`` XML fragment."""
        parts = [f"  <url>\n    <loc>{escape(self.loc)}</loc>"]
        lastmod = self._lastmod_str()
        if lastmod:
            parts.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        if self.changefreq:
            parts.append(f"    <changefreq>{self.changefreq}</changefreq>")
        if self.priority is not None:
            parts.append(f"    <priority>{self.priority:.1f}</priority>")
        parts.append("  </url>")
        return "\n".join(parts)


def generate_sitemap(urls: list[SitemapURL]) -> str:
    """Render a single sitemap XML document.

    Args:
        urls: The URLs to include. Must not exceed :data:`MAX_URLS_PER_SITEMAP`;
            use :func:`generate_sitemaps` for larger sets.

    Returns:
        A complete, well-formed sitemap XML document as a string.

    Raises:
        SitemapValidationError: If urls exceeds the per-file URL limit or is empty.
    """
    if not urls:
        raise SitemapValidationError("Cannot generate a sitemap with zero URLs")
    if len(urls) > MAX_URLS_PER_SITEMAP:
        raise SitemapValidationError(
            f"{len(urls)} URLs exceeds the {MAX_URLS_PER_SITEMAP}-URL sitemap limit; "
            "use generate_sitemaps() to split across multiple files"
        )

    body = "\n".join(url.to_xml() for url in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="{_SITEMAP_NS}">\n{body}\n</urlset>\n'
    )


def generate_sitemaps(urls: list[SitemapURL], *, chunk_size: int = MAX_URLS_PER_SITEMAP) -> list[str]:
    """Split a large URL set into multiple sitemap XML documents.

    Args:
        urls: The full list of URLs across the site.
        chunk_size: Maximum URLs per generated sitemap file.

    Returns:
        A list of sitemap XML document strings, one per chunk.

    Raises:
        SitemapValidationError: If urls is empty or chunk_size exceeds the protocol limit.
    """
    if not urls:
        raise SitemapValidationError("Cannot generate sitemaps with zero URLs")
    if chunk_size > MAX_URLS_PER_SITEMAP:
        raise SitemapValidationError(f"chunk_size cannot exceed {MAX_URLS_PER_SITEMAP}")

    chunks = [urls[i : i + chunk_size] for i in range(0, len(urls), chunk_size)]
    logger.info("Generating %d sitemap file(s) for %d URLs", len(chunks), len(urls))
    return [generate_sitemap(chunk) for chunk in chunks]


def generate_sitemap_index(sitemap_urls: list[str]) -> str:
    """Render a sitemap index XML document referencing multiple sitemap files.

    Args:
        sitemap_urls: Absolute URLs of each individual sitemap file.

    Returns:
        A complete sitemap index XML document as a string.

    Raises:
        SitemapValidationError: If sitemap_urls is empty.
    """
    if not sitemap_urls:
        raise SitemapValidationError("Cannot generate a sitemap index with zero sitemap URLs")

    entries = "\n".join(f"  <sitemap>\n    <loc>{escape(url)}</loc>\n  </sitemap>" for url in sitemap_urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<sitemapindex xmlns="{_SITEMAP_NS}">\n{entries}\n</sitemapindex>\n'
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.sitemap_generator urls.txt output.xml``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate an XML sitemap from a list of URLs.")
    parser.add_argument("urls_file", help="Path to a text file, one absolute URL per line")
    parser.add_argument("output_file", help="Path to write the generated sitemap XML")
    args = parser.parse_args(argv)

    try:
        with open(args.urls_file, encoding="utf-8") as f:
            urls = [SitemapURL(loc=line.strip()) for line in f if line.strip()]
        xml = generate_sitemap(urls)
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(xml)
    except (OSError, SitemapValidationError) as exc:
        logging.error("Sitemap generation failed: %s", exc)
        return 1

    logging.info("Wrote sitemap with %d URLs to %s", len(urls), args.output_file)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
