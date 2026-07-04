"""Generate service-area pages for businesses without a public physical presence.

Implements the service-area business guidance from
``docs/books/complete/seo/chapter-19.md`` section 10: unlike
``location_page_generator.py`` (for storefronts with a public address), a
service-area business (plumber, cleaner, etc.) must never publish a
street address or claim a physical presence in a city it doesn't
actually have one in — doing so violates Google's guidelines and risks
suspension. This is enforced structurally: :class:`ServiceAreaPageSpec`
has no street-address field at all, and the schema is built with
``areaServed`` rather than a physical ``address``. Reuses the same
minimum-unique-content quality gate as ``location_page_generator.py`` and
``scripts.meta_generator.generate_title`` for the page's title tag.

Example:
    >>> from scripts.service_page_generator import ServiceAreaPageSpec, check_quality_gates
    >>> spec = ServiceAreaPageSpec(
    ...     url_slug="austin-tx-plumbing",
    ...     business_name="Example Plumbing",
    ...     service_name="Emergency Plumbing",
    ...     area_served="Austin, TX",
    ...     telephone="512-555-0100",
    ...     unique_content="short",
    ... )
    >>> check_quality_gates(spec)
    ['Unique content is only 1 word(s) (recommended >= 50); thin/templated service-area pages violate Chapter 19 guidance']
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from scripts.location_page_generator import MIN_UNIQUE_CONTENT_WORDS

logger = logging.getLogger(__name__)

_PAGE_TEMPLATE = """# {{ title }}

{{ unique_content }}

## Service Details

**Service:** {{ spec.service_name }}
**Area served:** {{ spec.area_served }}
**Phone:** {{ spec.telephone }}

{{ schema_tag }}
"""


class ServicePageQualityError(ValueError):
    """Raised when a service-area page spec fails one or more quality gates."""


@dataclass
class ServiceAreaPageSpec:
    """Input data for a single governed service-area page.

    Deliberately has no street-address field: a service-area business must
    not claim a physical presence in the areas it serves.
    """

    url_slug: str
    business_name: str
    service_name: str
    area_served: str
    telephone: str
    unique_content: str = ""
    price_range: str | None = None


def check_quality_gates(spec: ServiceAreaPageSpec, *, other_specs: list[ServiceAreaPageSpec] | None = None) -> list[str]:
    """Check a service-area page spec against the chapter 19 section 10 quality gates.

    Args:
        spec: The service-area page to check.
        other_specs: Sibling service-area page specs, used to detect
            boilerplate content duplicated identically across pages.

    Returns:
        A list of human-readable violation messages; empty if the spec passes.
    """
    violations: list[str] = []

    for field_name in ("business_name", "service_name", "area_served", "telephone"):
        if not getattr(spec, field_name).strip():
            violations.append(f"{field_name} is required")

    word_count = len(spec.unique_content.split())
    if word_count < MIN_UNIQUE_CONTENT_WORDS:
        violations.append(
            f"Unique content is only {word_count} word(s) (recommended >= {MIN_UNIQUE_CONTENT_WORDS}); "
            "thin/templated service-area pages violate Chapter 19 guidance"
        )

    for other in other_specs or []:
        if other.url_slug == spec.url_slug:
            continue
        if spec.unique_content.strip() and spec.unique_content.strip() == other.unique_content.strip():
            violations.append(
                f"unique_content is identical to service area '{other.url_slug}' — "
                "pages must not share boilerplate content"
            )

    return violations


def generate_service_schema(spec: ServiceAreaPageSpec) -> dict:
    """Build a LocalBusiness JSON-LD schema scoped by ``areaServed``, with no street address.

    Args:
        spec: The service-area page to build schema for.

    Returns:
        A schema dict using ``areaServed`` rather than a physical ``address``,
        per chapter 19 section 10.
    """
    schema: dict = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": spec.business_name,
        "areaServed": spec.area_served,
        "telephone": spec.telephone,
    }
    if spec.price_range:
        schema["priceRange"] = spec.price_range
    return schema


def generate_service_page(
    spec: ServiceAreaPageSpec,
    *,
    other_specs: list[ServiceAreaPageSpec] | None = None,
    enforce_quality_gates: bool = True,
) -> str:
    """Render a single governed service-area page.

    Args:
        spec: The service-area page to render.
        other_specs: Sibling specs, passed through to :func:`check_quality_gates`.
        enforce_quality_gates: If True (the default), raise rather than
            render when any quality gate fails.

    Returns:
        The rendered page content (Markdown with an embedded JSON-LD schema).

    Raises:
        ServicePageQualityError: If enforce_quality_gates is True and any
            quality gate check fails.
    """
    if enforce_quality_gates:
        violations = check_quality_gates(spec, other_specs=other_specs)
        if violations:
            raise ServicePageQualityError("; ".join(violations))

    from jinja2 import Template

    from scripts.meta_generator import generate_title
    from scripts.schema_generator import to_script_tag

    title = generate_title(f"{spec.service_name} in {spec.area_served}", brand=spec.business_name)
    schema_tag = to_script_tag(generate_service_schema(spec))

    rendered = Template(_PAGE_TEMPLATE).render(title=title, spec=spec, unique_content=spec.unique_content.strip(), schema_tag=schema_tag)
    logger.info("Rendered service-area page for %r in %r (%s)", spec.service_name, spec.area_served, spec.url_slug)
    return rendered


def generate_service_pages(
    specs: list[ServiceAreaPageSpec], *, enforce_quality_gates: bool = True
) -> dict[str, str]:
    """Render multiple governed service-area pages, cross-checking for shared boilerplate.

    Args:
        specs: The full batch of service-area page specs.
        enforce_quality_gates: Passed through to :func:`generate_service_page`.

    Returns:
        A mapping of url_slug to rendered page content.

    Raises:
        ServicePageQualityError: If enforce_quality_gates is True and any
            spec fails its quality gates.
    """
    return {
        spec.url_slug: generate_service_page(spec, other_specs=specs, enforce_quality_gates=enforce_quality_gates)
        for spec in specs
    }


def specs_from_dict(raw_specs: list[dict]) -> list[ServiceAreaPageSpec]:
    """Build :class:`ServiceAreaPageSpec` objects from parsed JSON/dict data."""
    return [
        ServiceAreaPageSpec(
            url_slug=raw["url_slug"],
            business_name=raw["business_name"],
            service_name=raw["service_name"],
            area_served=raw["area_served"],
            telephone=raw["telephone"],
            unique_content=raw.get("unique_content", ""),
            price_range=raw.get("price_range"),
        )
        for raw in raw_specs
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.service_page_generator specs.json output_dir``."""
    import argparse
    import json
    from pathlib import Path

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate governed service-area pages from a JSON spec list.")
    parser.add_argument(
        "specs_file", help='JSON file: a list of {url_slug, business_name, service_name, area_served, telephone, unique_content} objects'
    )
    parser.add_argument("output_dir", help="Directory to write one Markdown file per service area")
    parser.add_argument(
        "--skip-quality-gates", action="store_true", help="Render pages even if they fail quality gates (not recommended)"
    )
    args = parser.parse_args(argv)

    try:
        with open(args.specs_file, encoding="utf-8") as f:
            specs = specs_from_dict(json.load(f))
        pages = generate_service_pages(specs, enforce_quality_gates=not args.skip_quality_gates)
    except (OSError, KeyError, json.JSONDecodeError, ServicePageQualityError) as exc:
        logging.error("Service-area page generation failed: %s", exc)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for slug, content in pages.items():
        (output_dir / f"{slug}.md").write_text(content, encoding="utf-8")

    logging.info("Wrote %d service-area page(s) to %s", len(pages), output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
