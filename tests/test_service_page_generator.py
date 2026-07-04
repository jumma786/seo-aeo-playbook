"""Unit tests for scripts.service_page_generator."""

from __future__ import annotations

import pytest

from scripts.service_page_generator import (
    MIN_UNIQUE_CONTENT_WORDS,
    ServiceAreaPageSpec,
    ServicePageQualityError,
    check_quality_gates,
    generate_service_page,
    generate_service_pages,
    generate_service_schema,
    specs_from_dict,
)

GOOD_CONTENT = (
    "Our licensed plumbers serve the greater Austin area with 24/7 emergency response, transparent "
    "flat-rate pricing, and a satisfaction guarantee backed by over a decade of local service experience. "
    "We specialize in burst pipe repair, water heater installation, and drain cleaning for homes and "
    "small businesses throughout the metro area, with most technicians arriving within ninety minutes."
)


def _make_spec(slug: str = "austin-tx-plumbing", *, unique_content: str = GOOD_CONTENT) -> ServiceAreaPageSpec:
    return ServiceAreaPageSpec(
        url_slug=slug,
        business_name="Example Plumbing",
        service_name="Emergency Plumbing",
        area_served="Austin, TX",
        telephone="512-555-0100",
        unique_content=unique_content,
    )


class TestServiceAreaPageSpec:
    def test_has_no_street_address_field(self) -> None:
        spec = _make_spec()
        assert not hasattr(spec, "street_address")


class TestCheckQualityGates:
    def test_valid_spec_has_no_violations(self) -> None:
        assert check_quality_gates(_make_spec()) == []

    def test_missing_required_field_flagged(self) -> None:
        spec = _make_spec()
        spec.telephone = ""
        violations = check_quality_gates(spec)
        assert any("telephone is required" in v for v in violations)

    def test_thin_content_flagged(self) -> None:
        violations = check_quality_gates(_make_spec(unique_content="Too short."))
        assert any(f">= {MIN_UNIQUE_CONTENT_WORDS}" in v for v in violations)

    def test_duplicate_content_across_areas_flagged(self) -> None:
        spec_a = _make_spec("austin-tx-plumbing")
        spec_b = _make_spec("dallas-tx-plumbing")
        violations = check_quality_gates(spec_a, other_specs=[spec_a, spec_b])
        assert any("identical" in v for v in violations)


class TestGenerateServiceSchema:
    def test_uses_area_served_not_address(self) -> None:
        schema = generate_service_schema(_make_spec())
        assert schema["areaServed"] == "Austin, TX"
        assert "address" not in schema
        assert "streetAddress" not in schema

    def test_includes_price_range_when_present(self) -> None:
        spec = _make_spec()
        spec.price_range = "$$"
        schema = generate_service_schema(spec)
        assert schema["priceRange"] == "$$"


class TestGenerateServicePage:
    def test_renders_service_details_and_schema(self) -> None:
        content = generate_service_page(_make_spec())
        assert "Emergency Plumbing" in content
        assert "Austin, TX" in content
        assert "512-555-0100" in content
        assert "LocalBusiness" in content
        assert "areaServed" in content

    def test_no_street_address_in_rendered_output(self) -> None:
        content = generate_service_page(_make_spec())
        assert "streetAddress" not in content

    def test_quality_gate_failure_raises_by_default(self) -> None:
        with pytest.raises(ServicePageQualityError):
            generate_service_page(_make_spec(unique_content="Too short."))

    def test_quality_gates_can_be_skipped(self) -> None:
        content = generate_service_page(_make_spec(unique_content="Too short."), enforce_quality_gates=False)
        assert "Emergency Plumbing" in content


class TestGenerateServicePages:
    def test_renders_all_specs(self) -> None:
        specs = [
            _make_spec("austin-tx-plumbing", unique_content=GOOD_CONTENT + " austin"),
            _make_spec("dallas-tx-plumbing", unique_content=GOOD_CONTENT + " dallas"),
        ]
        pages = generate_service_pages(specs)
        assert set(pages.keys()) == {"austin-tx-plumbing", "dallas-tx-plumbing"}

    def test_duplicate_content_raises_for_whole_batch(self) -> None:
        specs = [_make_spec("austin-tx-plumbing"), _make_spec("dallas-tx-plumbing")]
        with pytest.raises(ServicePageQualityError):
            generate_service_pages(specs)


class TestSpecsFromDict:
    def test_builds_specs(self) -> None:
        raw = [
            {
                "url_slug": "austin-tx-plumbing",
                "business_name": "Example Plumbing",
                "service_name": "Emergency Plumbing",
                "area_served": "Austin, TX",
                "telephone": "512-555-0100",
                "unique_content": GOOD_CONTENT,
            }
        ]
        specs = specs_from_dict(raw)
        assert len(specs) == 1
        assert specs[0].area_served == "Austin, TX"

    def test_missing_key_raises(self) -> None:
        with pytest.raises(KeyError):
            specs_from_dict([{"url_slug": "austin-tx-plumbing"}])
