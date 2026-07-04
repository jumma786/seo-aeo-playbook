"""Validate Schema.org JSON-LD markup for structural correctness.

Complements ``scripts/schema_generator.py``: where that module builds valid
schema dicts from scratch, this module independently re-validates JSON-LD
as it would already be found rendered in a page's
``<script type="application/ld+json">`` tag — so a CI pipeline can catch
invalid or incomplete markup before it reaches production, per
``docs/books/complete/seo/chapter-14.md`` section 18.

Example:
    >>> from scripts.schema_validator import validate_schema
    >>> issues = validate_schema({"@context": "https://schema.org", "@type": "Article", "headline": "Hi"})
    >>> [issue.path for issue in issues]
    ['author', 'datePublished']
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A single problem found while validating a JSON-LD schema object."""

    severity: str  # "error" | "warning" | "info"
    path: str
    message: str


def _check_present(schema: dict[str, Any], field: str, schema_type: str, issues: list[ValidationIssue]) -> None:
    if not schema.get(field):
        issues.append(
            ValidationIssue(severity="error", path=field, message=f"{schema_type} is missing required field '{field}'")
        )


def _validate_article(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    schema_type = schema.get("@type", "Article")
    for field in ("headline", "author", "datePublished"):
        _check_present(schema, field, schema_type, issues)
    author = schema.get("author")
    if isinstance(author, dict) and not author.get("name"):
        issues.append(ValidationIssue("error", "author.name", f"{schema_type} author is missing a 'name'"))


def _validate_product(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    _check_present(schema, "name", "Product", issues)
    offers = schema.get("offers")
    if offers is None:
        issues.append(ValidationIssue("error", "offers", "Product is missing required field 'offers'"))
    elif isinstance(offers, dict):
        for field in ("price", "priceCurrency"):
            if not offers.get(field):
                issues.append(
                    ValidationIssue("error", f"offers.{field}", f"Product offers is missing required field '{field}'")
                )
    else:
        issues.append(ValidationIssue("warning", "offers", "Product offers should be an object with price/priceCurrency"))


def _validate_faq_page(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    main_entity = schema.get("mainEntity")
    if not main_entity:
        issues.append(ValidationIssue("error", "mainEntity", "FAQPage is missing required field 'mainEntity'"))
        return
    if not isinstance(main_entity, list):
        issues.append(ValidationIssue("error", "mainEntity", "FAQPage mainEntity must be a list of Question entries"))
        return

    for index, entry in enumerate(main_entity):
        if not isinstance(entry, dict) or not entry.get("name"):
            issues.append(ValidationIssue("error", f"mainEntity[{index}].name", "FAQPage entry is missing a question 'name'"))
        accepted_answer = entry.get("acceptedAnswer") if isinstance(entry, dict) else None
        if not isinstance(accepted_answer, dict) or not accepted_answer.get("text"):
            issues.append(
                ValidationIssue(
                    "error", f"mainEntity[{index}].acceptedAnswer.text", "FAQPage entry is missing 'acceptedAnswer.text'"
                )
            )


def _validate_local_business(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    schema_type = schema.get("@type", "LocalBusiness")
    for field in ("name", "address"):
        _check_present(schema, field, schema_type, issues)


def _validate_breadcrumb_list(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    items = schema.get("itemListElement")
    if not items:
        issues.append(ValidationIssue("error", "itemListElement", "BreadcrumbList is missing required field 'itemListElement'"))
    elif not isinstance(items, list):
        issues.append(ValidationIssue("error", "itemListElement", "BreadcrumbList itemListElement must be a list"))


def _validate_organization(schema: dict[str, Any], issues: list[ValidationIssue]) -> None:
    for field in ("name", "url"):
        _check_present(schema, field, "Organization", issues)


# Maps @type -> validator function. Types without a registered validator
# (e.g. LocalBusiness subtypes like "Dentist") get an informational notice
# rather than a false-negative "no issues found".
VALIDATORS: dict[str, Callable[[dict[str, Any], list[ValidationIssue]], None]] = {
    "Article": _validate_article,
    "NewsArticle": _validate_article,
    "BlogPosting": _validate_article,
    "Product": _validate_product,
    "FAQPage": _validate_faq_page,
    "LocalBusiness": _validate_local_business,
    "BreadcrumbList": _validate_breadcrumb_list,
    "Organization": _validate_organization,
}


def validate_schema(schema: dict[str, Any], *, require_context: bool = True) -> list[ValidationIssue]:
    """Validate a single JSON-LD schema object for structural correctness.

    Args:
        schema: A parsed JSON-LD object — either a standalone schema (e.g.
            as produced by ``scripts.schema_generator``) or an object
            containing an ``@graph`` list of nested schemas.
        require_context: Whether a missing ``@context`` should be flagged.
            Nested ``@graph`` items are validated with this set to False,
            since ``@context`` is conventionally declared once at the
            top level and inherited by graph members (see
            ``scripts.schema_generator.combine_schemas``).

    Returns:
        A list of :class:`ValidationIssue`; empty if no problems were found.
    """
    issues: list[ValidationIssue] = []

    if "@graph" in schema:
        graph = schema.get("@graph")
        if not isinstance(graph, list):
            issues.append(ValidationIssue("error", "@graph", "@graph must be a list of schema objects"))
            return issues
        for index, item in enumerate(graph):
            for issue in validate_schema(item, require_context=False):
                issues.append(ValidationIssue(issue.severity, f"@graph[{index}].{issue.path}", issue.message))
        return issues

    schema_type = schema.get("@type")
    if not schema_type:
        issues.append(ValidationIssue("error", "@type", "Schema is missing required field '@type'"))
        return issues

    if require_context and "@context" not in schema:
        issues.append(
            ValidationIssue("warning", "@context", "Schema is missing '@context' (expected 'https://schema.org')")
        )

    validator = VALIDATORS.get(schema_type)
    if validator is None:
        issues.append(
            ValidationIssue("info", "@type", f"No built-in validation rules for @type {schema_type!r}; skipping field checks")
        )
        return issues

    validator(schema, issues)
    return issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    """Return True if any issue in the list is an "error"-severity issue."""
    return any(issue.severity == "error" for issue in issues)


def extract_json_ld_from_html(html: str) -> list[dict[str, Any]]:
    """Extract all JSON-LD objects from ``<script type="application/ld+json">`` tags.

    Args:
        html: Raw page HTML.

    Returns:
        Parsed JSON-LD dicts, in document order. A tag containing invalid
        JSON is skipped (with a warning logged) rather than aborting
        extraction of the rest of the page.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    schemas: list[dict[str, Any]] = []
    for index, tag in enumerate(soup.find_all("script", attrs={"type": "application/ld+json"})):
        raw = tag.string or tag.get_text()
        try:
            schemas.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            logger.warning("Skipping malformed JSON-LD block %d: %s", index, exc)
    return schemas


def validate_html(html: str) -> list[tuple[dict[str, Any], list[ValidationIssue]]]:
    """Extract and validate every JSON-LD block embedded in a page's HTML.

    Args:
        html: Raw page HTML.

    Returns:
        A list of (schema, issues) pairs, one per JSON-LD block found.
    """
    return [(schema, validate_schema(schema)) for schema in extract_json_ld_from_html(html)]


def format_report(results: list[tuple[dict[str, Any], list[ValidationIssue]]]) -> str:
    """Render validation results for one or more schema blocks as a text report."""
    lines = [f"Schema Validation Report ({len(results)} JSON-LD block(s) found)", ""]
    for index, (schema, issues) in enumerate(results):
        schema_type = schema.get("@type") or ("@graph" if "@graph" in schema else "Unknown")
        lines.append(f"Block {index + 1}: @type={schema_type!r}")
        if not issues:
            lines.append("  OK - no issues found")
        for issue in issues:
            lines.append(f"  [{issue.severity.upper()}] {issue.path}: {issue.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.schema_validator page.html|schema.json``.

    Exits with status 1 if any error-severity issue is found, matching the
    "fail the build" behavior expected of a CI validation step.
    """
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Validate Schema.org JSON-LD markup in an HTML page or a standalone JSON schema file."
    )
    parser.add_argument("input_file", help="Path to an .html file or a .json file containing a single schema object")
    args = parser.parse_args(argv)

    try:
        with open(args.input_file, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        logging.error("Could not read %s: %s", args.input_file, exc)
        return 1

    if args.input_file.lower().endswith(".json"):
        try:
            schema = json.loads(content)
        except json.JSONDecodeError as exc:
            logging.error("Invalid JSON in %s: %s", args.input_file, exc)
            return 1
        results = [(schema, validate_schema(schema))]
    else:
        results = validate_html(content)

    print(format_report(results))
    return 1 if any(has_errors(issues) for _, issues in results) else 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
