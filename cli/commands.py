"""Click subcommands for the ``seo-playbook`` CLI, wiring up ``scripts/``.

Each subcommand is a thin adapter over an existing function in ``scripts/``:
this module owns argument parsing, config resolution, and error presentation,
while the actual SEO logic stays in the already-tested ``scripts`` modules.
"""

from __future__ import annotations

import json
import logging

import click

from cli.config import Config, ConfigError, load_config
from scripts.entity_extractor import extract_entities, find_entity_gaps, format_report as format_entity_report
from scripts.internal_linker import format_report as format_linking_report
from scripts.internal_linker import pages_from_dict, suggest_internal_links
from scripts.keyword_cluster import cluster_keywords
from scripts.link_checker import check_links, extract_links_from_html
from scripts.link_checker import format_report as format_link_check_report
from scripts.page_speed import audit_url_performance
from scripts.page_speed import format_report as format_page_speed_report
from scripts.llms_txt_generator import LlmsTxtValidationError, generate_llms_txt, sections_from_dict
from scripts.llms_validator import audit_robots_txt
from scripts.llms_validator import format_report as format_crawler_report
from scripts.meta_generator import (
    generate_meta_description,
    generate_title,
    validate_meta_description,
    validate_title,
)
from scripts.robots_generator import RobotsGroup, RobotsValidationError, generate_robots_txt
from scripts.schema_generator import (
    SchemaValidationError,
    generate_article_schema,
    generate_faq_schema,
    to_script_tag,
)
from scripts.schema_validator import has_errors, validate_html, validate_schema
from scripts.schema_validator import format_report as format_schema_validation_report
from scripts.seo_audit import audit_url, format_report
from scripts.sitemap_generator import SitemapURL, SitemapValidationError, generate_sitemap

logger = logging.getLogger(__name__)


def _emit(content: str, output_path: str | None) -> None:
    """Write content to output_path if given, otherwise print it to stdout."""
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"Wrote output to {output_path}")
    else:
        click.echo(content)


@click.group()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to a seo-playbook.yml config file (defaults to ./seo-playbook.yml if present).",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None, verbose: bool) -> None:
    """seo-playbook: SEO, AEO, and GEO automation toolkit."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")
    try:
        ctx.obj = load_config(config_path)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.group()
def schema() -> None:
    """Generate Schema.org JSON-LD structured data."""


@schema.command("article")
@click.option("--headline", required=True)
@click.option("--author", required=True)
@click.option("--date-published", required=True)
@click.option("--date-modified", default=None)
@click.option("--output", type=click.Path(dir_okay=False), default=None, help="Write to a file instead of stdout.")
def schema_article(
    headline: str, author: str, date_published: str, date_modified: str | None, output: str | None
) -> None:
    """Generate an Article schema and print it as a <script> tag."""
    try:
        result = generate_article_schema(
            headline=headline,
            author_name=author,
            date_published=date_published,
            date_modified=date_modified,
        )
    except SchemaValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(to_script_tag(result), output)


@schema.command("faq")
@click.argument("json_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", type=click.Path(dir_okay=False), default=None, help="Write to a file instead of stdout.")
def schema_faq(json_file: str, output: str | None) -> None:
    """Generate a FAQPage schema from a JSON file of [question, answer] pairs."""
    try:
        with open(json_file, encoding="utf-8") as f:
            pairs = [tuple(pair) for pair in json.load(f)]
        result = generate_faq_schema(pairs)  # type: ignore[arg-type]
    except (SchemaValidationError, OSError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(to_script_tag(result), output)


@schema.command("validate")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def schema_validate(ctx: click.Context, input_file: str) -> None:
    """Validate JSON-LD markup in an HTML page or a standalone .json schema file.

    Exits with a non-zero status if any error-severity issue is found, so
    this can be used as a CI gate.
    """
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    if input_file.lower().endswith(".json"):
        try:
            schema_obj = json.loads(content)
        except json.JSONDecodeError as exc:
            raise click.ClickException(f"Invalid JSON in {input_file}: {exc}") from exc
        results = [(schema_obj, validate_schema(schema_obj))]
    else:
        results = validate_html(content)

    click.echo(format_schema_validation_report(results))
    if any(has_errors(issues) for _, issues in results):
        ctx.exit(1)


@cli.group()
def llms() -> None:
    """Generate and audit llms.txt / AI crawler accessibility (AEO)."""


@llms.command("generate")
@click.argument("spec_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", type=click.Path(dir_okay=False), default=None, help="Write to a file instead of stdout.")
def llms_generate(spec_file: str, output: str | None) -> None:
    """Generate an llms.txt file from a JSON spec (name, summary, sections)."""
    try:
        with open(spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        sections = sections_from_dict(spec.get("sections", []))
        content = generate_llms_txt(spec["name"], spec["summary"], sections)
    except (OSError, KeyError, LlmsTxtValidationError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(content, output)


@llms.command("audit-crawlers")
@click.argument("robots_file", type=click.Path(exists=True, dir_okay=False))
def llms_audit_crawlers(robots_file: str) -> None:
    """Audit a robots.txt file for AI crawler (GPTBot, ClaudeBot, ...) accessibility."""
    with open(robots_file, encoding="utf-8") as f:
        content = f.read()
    statuses = audit_robots_txt(content)
    click.echo(format_crawler_report(statuses))


@cli.command("audit")
@click.argument("url")
@click.option("--timeout", type=float, default=10.0, show_default=True)
def audit(url: str, timeout: float) -> None:
    """Fetch a URL and run an on-page SEO audit against it."""
    try:
        result = audit_url(url, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the CLI user
        raise click.ClickException(f"Failed to audit {url}: {exc}") from exc
    click.echo(format_report(result))


@cli.command("page-speed")
@click.argument("url")
@click.option("--timeout", type=float, default=10.0, show_default=True)
def page_speed(url: str, timeout: float) -> None:
    """Fetch a URL and run a static page speed audit against it."""
    try:
        result = audit_url_performance(url, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the CLI user
        raise click.ClickException(f"Failed to audit {url}: {exc}") from exc
    click.echo(format_page_speed_report(result))


@cli.command("cluster")
@click.argument("keywords_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--threshold", type=float, default=None, help="Similarity threshold override (0.0-1.0).")
@click.pass_obj
def cluster(config: Config, keywords_file: str, threshold: float | None) -> None:
    """Cluster keywords from a file (one per line) by lexical similarity."""
    resolved_threshold = threshold if threshold is not None else config.default_similarity_threshold
    with open(keywords_file, encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    try:
        clusters = cluster_keywords(keywords, similarity_threshold=resolved_threshold)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    for group in clusters:
        click.echo(f"# {group.label}")
        for keyword in group.keywords:
            click.echo(f"  - {keyword}")


@cli.command("entities")
@click.argument("content_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--compare",
    "compare_file",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="A competitor text file; reports entities it mentions that content_file doesn't.",
)
def entities(content_file: str, compare_file: str | None) -> None:
    """Extract entity mentions (and optionally gaps vs. a competitor file) from text."""
    with open(content_file, encoding="utf-8") as f:
        mentions = extract_entities(f.read())
    click.echo(format_entity_report(mentions))

    if compare_file:
        with open(compare_file, encoding="utf-8") as f:
            competitor_mentions = extract_entities(f.read())
        gaps = find_entity_gaps(mentions, competitor_mentions)
        click.echo(f"\nEntity gaps ({len(gaps)} found in {compare_file} but not {content_file}):")
        for gap in gaps:
            click.echo(f"  - {gap}")


@cli.command("link-suggestions")
@click.argument("pages_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--max-per-page", type=int, default=5, show_default=True)
def link_suggestions(pages_file: str, max_per_page: int) -> None:
    """Suggest internal links and flag orphan pages from a JSON page list."""
    try:
        with open(pages_file, encoding="utf-8") as f:
            pages = pages_from_dict(json.load(f))
    except (KeyError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc

    suggestions = suggest_internal_links(pages, max_suggestions_per_page=max_per_page)
    click.echo(format_linking_report(pages, suggestions))


@cli.command("check-links")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--base-url", default="", help="Base URL for resolving relative links (HTML input only).")
@click.option("--timeout", type=float, default=10.0, show_default=True)
@click.pass_context
def check_links_command(ctx: click.Context, input_file: str, base_url: str, timeout: float) -> None:
    """Check links for broken URLs and redirects.

    A .html file has its links extracted and checked; any other file is
    treated as a plain text list of URLs, one per line. Exits non-zero if
    any broken link is found, so this can be used as a CI gate.
    """
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    if input_file.lower().endswith(".html"):
        urls = extract_links_from_html(content, base_url=base_url)
    else:
        urls = [line.strip() for line in content.splitlines() if line.strip()]

    results = check_links(urls, timeout=timeout)
    click.echo(format_link_check_report(results))
    if any(result.is_broken for result in results):
        ctx.exit(1)


@cli.command("sitemap")
@click.argument("urls_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
def sitemap(urls_file: str, output_file: str) -> None:
    """Generate an XML sitemap from a file of absolute URLs (one per line)."""
    try:
        with open(urls_file, encoding="utf-8") as f:
            urls = [SitemapURL(loc=line.strip()) for line in f if line.strip()]
        xml = generate_sitemap(urls)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml)
    except (OSError, SitemapValidationError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Wrote sitemap with {len(urls)} URLs to {output_file}")


@cli.command("robots")
@click.argument("output_file", type=click.Path(dir_okay=False))
@click.option("--disallow", multiple=True, help="Path to disallow for all crawlers (repeatable).")
@click.option("--sitemap-url", "sitemap_urls", multiple=True, help="Sitemap URL to advertise (repeatable).")
@click.pass_obj
def robots(config: Config, output_file: str, disallow: tuple[str, ...], sitemap_urls: tuple[str, ...]) -> None:
    """Generate a robots.txt file."""
    resolved_sitemap_urls = list(sitemap_urls)
    if not resolved_sitemap_urls and config.domain:
        resolved_sitemap_urls = [f"https://{config.domain}/sitemap.xml"]

    try:
        group = RobotsGroup(user_agent="*", disallow=list(disallow))
        content = generate_robots_txt([group], sitemap_urls=resolved_sitemap_urls or None)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
    except (OSError, RobotsValidationError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Wrote robots.txt to {output_file}")


@cli.command("meta")
@click.option("--title", default=None, help="Page-specific title text.")
@click.option("--brand", default=None, help="Brand name to append to the title (defaults to config brand).")
@click.option("--description", default=None, help="Source text for the meta description.")
@click.pass_obj
def meta(config: Config, title: str | None, brand: str | None, description: str | None) -> None:
    """Generate an SEO title tag and/or meta description."""
    if not title and not description:
        raise click.UsageError("Provide --title and/or --description")

    resolved_brand = brand if brand is not None else config.brand

    if title:
        result_title = generate_title(title, brand=resolved_brand)
        click.echo(f"Title ({len(result_title)} chars): {result_title}")
        for warning in validate_title(result_title):
            click.echo(f"  warning: {warning}", err=True)

    if description:
        result_description = generate_meta_description(description)
        click.echo(f"Description ({len(result_description)} chars): {result_description}")
        for warning in validate_meta_description(result_description):
            click.echo(f"  warning: {warning}", err=True)
