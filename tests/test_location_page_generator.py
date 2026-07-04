"""Unit tests for scripts.location_page_generator."""

from __future__ import annotations

import pytest

from scripts.location_page_generator import (
    MIN_UNIQUE_CONTENT_WORDS,
    NAP,
    LocationPageQualityError,
    LocationPageSpec,
    check_quality_gates,
    generate_location_page,
    generate_location_pages,
    nap_from_dict,
    specs_from_dict,
)

GOOD_CONTENT = " ".join(["Our Austin location offers"] * 15)  # well over the minimum word count


def _make_spec(slug: str = "austin-tx", *, unique_content: str = GOOD_CONTENT, nap: NAP | None = None) -> LocationPageSpec:
    return LocationPageSpec(
        url_slug=slug,
        nap=nap
        or NAP(
            name="Example Dental",
            street_address="1 Main St",
            address_locality="Austin",
            address_region="TX",
            postal_code="78701",
            telephone="512-555-0100",
        ),
        hours={"Monday": "9am-5pm"},
        unique_content=unique_content,
    )


class TestCheckQualityGates:
    def test_valid_spec_has_no_violations(self) -> None:
        assert check_quality_gates(_make_spec()) == []

    def test_incomplete_nap_flagged(self) -> None:
        nap = NAP(name="", street_address="1 Main St", address_locality="Austin", address_region="TX", postal_code="78701", telephone="512-555-0100")
        violations = check_quality_gates(_make_spec(nap=nap))
        assert any("NAP data incomplete" in v for v in violations)

    def test_thin_content_flagged(self) -> None:
        violations = check_quality_gates(_make_spec(unique_content="Too short."))
        assert any(f">= {MIN_UNIQUE_CONTENT_WORDS}" in v for v in violations)

    def test_duplicate_content_across_locations_flagged(self) -> None:
        spec_a = _make_spec("austin-tx")
        spec_b = _make_spec("dallas-tx")
        violations = check_quality_gates(spec_a, other_specs=[spec_a, spec_b])
        assert any("identical" in v for v in violations)

    def test_unique_content_across_locations_not_flagged(self) -> None:
        spec_a = _make_spec("austin-tx", unique_content=GOOD_CONTENT + " austin")
        spec_b = _make_spec("dallas-tx", unique_content=GOOD_CONTENT + " dallas")
        violations = check_quality_gates(spec_a, other_specs=[spec_a, spec_b])
        assert violations == []


class TestGenerateLocationPage:
    def test_renders_nap_and_schema(self) -> None:
        content = generate_location_page(_make_spec())
        assert "Example Dental" in content
        assert "Austin" in content
        assert "LocalBusiness" in content
        assert "512-555-0100" in content

    def test_quality_gate_failure_raises_by_default(self) -> None:
        with pytest.raises(LocationPageQualityError):
            generate_location_page(_make_spec(unique_content="Too short."))

    def test_quality_gates_can_be_skipped(self) -> None:
        content = generate_location_page(_make_spec(unique_content="Too short."), enforce_quality_gates=False)
        assert "Example Dental" in content

    def test_hours_rendered(self) -> None:
        content = generate_location_page(_make_spec())
        assert "Monday: 9am-5pm" in content


class TestGenerateLocationPages:
    def test_renders_all_specs(self) -> None:
        specs = [
            _make_spec("austin-tx", unique_content=GOOD_CONTENT + " austin"),
            _make_spec("dallas-tx", unique_content=GOOD_CONTENT + " dallas"),
        ]
        pages = generate_location_pages(specs)
        assert set(pages.keys()) == {"austin-tx", "dallas-tx"}

    def test_duplicate_content_raises_for_whole_batch(self) -> None:
        specs = [_make_spec("austin-tx"), _make_spec("dallas-tx")]
        with pytest.raises(LocationPageQualityError):
            generate_location_pages(specs)


class TestNapFromDict:
    def test_builds_nap(self) -> None:
        nap = nap_from_dict(
            {
                "name": "Example Dental",
                "street_address": "1 Main St",
                "address_locality": "Austin",
                "address_region": "TX",
                "postal_code": "78701",
                "telephone": "512-555-0100",
            }
        )
        assert nap.name == "Example Dental"
        assert nap.address_country == "US"

    def test_missing_key_raises(self) -> None:
        with pytest.raises(KeyError):
            nap_from_dict({"name": "Example Dental"})


class TestSpecsFromDict:
    def test_builds_specs(self) -> None:
        raw = [
            {
                "url_slug": "austin-tx",
                "nap": {
                    "name": "Example Dental",
                    "street_address": "1 Main St",
                    "address_locality": "Austin",
                    "address_region": "TX",
                    "postal_code": "78701",
                    "telephone": "512-555-0100",
                },
                "hours": {"Monday": "9am-5pm"},
                "unique_content": GOOD_CONTENT,
            }
        ]
        specs = specs_from_dict(raw)
        assert len(specs) == 1
        assert specs[0].url_slug == "austin-tx"
        assert specs[0].nap.name == "Example Dental"
