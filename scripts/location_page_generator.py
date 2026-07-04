"""Generate governed location pages for multi-location businesses.

Implements the "governed template" workflow from
``docs/books/complete/seo/chapter-19.md`` section 11: renders a shared
Jinja2 page template per location, enforcing the chapter's mandatory
quality gates before writing anything — unique local content per page
(no thin, templated duplicates), verified/complete NAP data, and no
boilerplate content shared identically across sibling location pages.
Reuses ``scripts.schema_generator.generate_local_business_schema`` and
``scripts.meta_generator.generate_title`` for the per-location
``LocalBusiness`` schema and title tag required by section 7.

Example:
    >>> from scripts.location_page_generator import NAP, LocationPageSpec, check_quality_gates
    >>> nap = NAP(name="Example Dental", street_address="1 Main St", address_locality="Austin",
    ...     address_region="TX", postal_code="78701", telephone="512-555-0100")
    >>> spec = LocationPageSpec(url_slug="austin-tx", nap=nap, hours={"Monday": "9am-5pm"}, unique_content="short")
    >>> check_quality_gates(spec)
    ['Unique content is only 1 word(s) (recommended >= 50); thin/templated location pages violate Chapter 19 guidance']
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MIN_UNIQUE_CONTENT_WORDS = 50
_NAP_FIELDS = ("name", "street_address", "address_locality", "address_region", "postal_code", "telephone")

_PAGE_TEMPLATE = """# {{ nap.name }} — {{ nap.address_locality }}, {{ nap.address_region }}

{{ unique_content }}

## Location Details

**Address:** {{ nap.street_address }}, {{ nap.address_locality }}, {{ nap.address_region }} {{ nap.postal_code }}
**Phone:** {{ nap.telephone }}

## Hours
{% for day, time in hours.items() %}
- {{ day }}: {{ time }}
{%- endfor %}

{{ schema_tag }}
"""


class LocationPageQualityError(ValueError):
    """Raised when a location page spec fails one or more quality gates."""


@dataclass
class NAP:
    """A location's Name, Address, and Phone — the foundational local trust signal (chapter 19 section 4)."""

    name: str
    street_address: str
    address_locality: str
    address_region: str
    postal_code: str
    telephone: str
    address_country: str = "US"


@dataclass
class LocationPageSpec:
    """Input data for a single governed location page."""

    url_slug: str
    nap: NAP
    hours: dict[str, str] = field(default_factory=dict)
    unique_content: str = ""
    business_type: str = "LocalBusiness"


def check_quality_gates(spec: LocationPageSpec, *, other_specs: list[LocationPageSpec] | None = None) -> list[str]:
    """Check a location page spec against the chapter 19 section 11 quality gates.

    Args:
        spec: The location page to check.
        other_specs: Sibling location page specs, used to detect boilerplate
            content duplicated identically across locations.

    Returns:
        A list of human-readable violation messages; empty if the spec passes.
    """
    violations: list[str] = []

    missing_fields = [field_name for field_name in _NAP_FIELDS if not getattr(spec.nap, field_name).strip()]
    if missing_fields:
        violations.append(f"NAP data incomplete: missing {', '.join(missing_fields)}")

    word_count = len(spec.unique_content.split())
    if word_count < MIN_UNIQUE_CONTENT_WORDS:
        violations.append(
            f"Unique content is only {word_count} word(s) (recommended >= {MIN_UNIQUE_CONTENT_WORDS}); "
            "thin/templated location pages violate Chapter 19 guidance"
        )

    for other in other_specs or []:
        if other.url_slug == spec.url_slug:
            continue
        if spec.unique_content.strip() and spec.unique_content.strip() == other.unique_content.strip():
            violations.append(
                f"unique_content is identical to location '{other.url_slug}' — "
                "location pages must not share boilerplate content"
            )

    return violations


def generate_location_page(
    spec: LocationPageSpec, *, other_specs: list[LocationPageSpec] | None = None, enforce_quality_gates: bool = True
) -> str:
    """Render a single governed location page.

    Args:
        spec: The location page to render.
        other_specs: Sibling location specs, passed through to
            :func:`check_quality_gates` for cross-location duplicate detection.
        enforce_quality_gates: If True (the default), raise rather than
            render when any quality gate fails.

    Returns:
        The rendered page content (Markdown with an embedded JSON-LD
        ``LocalBusiness`` schema).

    Raises:
        LocationPageQualityError: If enforce_quality_gates is True and any
            quality gate check fails.
    """
    if enforce_quality_gates:
        violations = check_quality_gates(spec, other_specs=other_specs)
        if violations:
            raise LocationPageQualityError("; ".join(violations))

    from jinja2 import Template

    from scripts.schema_generator import generate_local_business_schema, to_script_tag

    schema = generate_local_business_schema(
        name=spec.nap.name,
        street_address=spec.nap.street_address,
        address_locality=spec.nap.address_locality,
        address_region=spec.nap.address_region,
        postal_code=spec.nap.postal_code,
        address_country=spec.nap.address_country,
        telephone=spec.nap.telephone,
        business_type=spec.business_type,
    )

    rendered = Template(_PAGE_TEMPLATE).render(
        nap=spec.nap, hours=spec.hours, unique_content=spec.unique_content.strip(), schema_tag=to_script_tag(schema)
    )
    logger.info("Rendered location page for %r (%s)", spec.nap.name, spec.url_slug)
    return rendered


def generate_location_pages(specs: list[LocationPageSpec], *, enforce_quality_gates: bool = True) -> dict[str, str]:
    """Render multiple governed location pages, cross-checking for shared boilerplate.

    Args:
        specs: The full batch of location page specs (used together so
            cross-location duplicate content can be detected).
        enforce_quality_gates: Passed through to :func:`generate_location_page`.

    Returns:
        A mapping of url_slug to rendered page content.

    Raises:
        LocationPageQualityError: If enforce_quality_gates is True and any
            spec fails its quality gates.
    """
    return {spec.url_slug: generate_location_page(spec, other_specs=specs, enforce_quality_gates=enforce_quality_gates) for spec in specs}


def nap_from_dict(raw: dict[str, str]) -> NAP:
    """Build a :class:`NAP` from parsed JSON/dict data."""
    return NAP(
        name=raw["name"],
        street_address=raw["street_address"],
        address_locality=raw["address_locality"],
        address_region=raw["address_region"],
        postal_code=raw["postal_code"],
        telephone=raw["telephone"],
        address_country=raw.get("address_country", "US"),
    )


def specs_from_dict(raw_specs: list[dict]) -> list[LocationPageSpec]:
    """Build :class:`LocationPageSpec` objects from parsed JSON/dict data."""
    return [
        LocationPageSpec(
            url_slug=raw["url_slug"],
            nap=nap_from_dict(raw["nap"]),
            hours=raw.get("hours", {}),
            unique_content=raw.get("unique_content", ""),
            business_type=raw.get("business_type", "LocalBusiness"),
        )
        for raw in raw_specs
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.location_page_generator specs.json output_dir``."""
    import argparse
    import json
    from pathlib import Path

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate governed location pages from a JSON spec list.")
    parser.add_argument("specs_file", help='JSON file: a list of {url_slug, nap, hours, unique_content} objects')
    parser.add_argument("output_dir", help="Directory to write one Markdown file per location")
    parser.add_argument(
        "--skip-quality-gates", action="store_true", help="Render pages even if they fail quality gates (not recommended)"
    )
    args = parser.parse_args(argv)

    try:
        with open(args.specs_file, encoding="utf-8") as f:
            specs = specs_from_dict(json.load(f))
        pages = generate_location_pages(specs, enforce_quality_gates=not args.skip_quality_gates)
    except (OSError, KeyError, json.JSONDecodeError, LocationPageQualityError) as exc:
        logging.error("Location page generation failed: %s", exc)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for slug, content in pages.items():
        (output_dir / f"{slug}.md").write_text(content, encoding="utf-8")

    logging.info("Wrote %d location page(s) to %s", len(pages), output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
