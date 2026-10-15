"""Hypothesis property tests for Finding schema invariants."""

from __future__ import annotations

from typing import Literal

from hypothesis import given
from hypothesis import strategies as st

from earngreen.core.findings import (
    UNKNOWN_CONFIDENCE,
    UNKNOWN_SEVERITY,
    DetectionMode,
    ErrorType,
    Finding,
    compute_fingerprint,
)
from earngreen.core.findings import TestType as FindingTestType

_CharCategory = Literal["Cs"]
_NO_SURROGATES: tuple[_CharCategory, ...] = ("Cs",)

_non_empty_identity = st.text(
    alphabet=st.characters(blacklist_categories=_NO_SURROGATES, blacklist_characters="\0"),
    min_size=1,
    max_size=64,
).filter(lambda value: bool(value.strip()))

_plain_str = st.text(
    alphabet=st.characters(blacklist_categories=_NO_SURROGATES, blacklist_characters="\0"),
    max_size=64,
)

_severity = st.sampled_from([UNKNOWN_SEVERITY, *range(1, 6)])
_confidence = st.one_of(
    st.just(UNKNOWN_CONFIDENCE),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
_detection_mode = st.one_of(st.none(), st.sampled_from(list(DetectionMode)))


@given(
    why=_plain_str,
    test_type=st.sampled_from(list(FindingTestType)),
    error_type=st.sampled_from(list(ErrorType)),
    severity=_severity,
    confidence=_confidence,
    ai_blind_spot_prior=_plain_str,
    rule_id=_non_empty_identity,
    subject_identity=_non_empty_identity,
    detection_mode=_detection_mode,
)
def test_finding_property_json_round_trip(
    why: str,
    test_type: FindingTestType,
    error_type: ErrorType,
    severity: int,
    confidence: float,
    ai_blind_spot_prior: str,
    rule_id: str,
    subject_identity: str,
    detection_mode: DetectionMode | None,
) -> None:
    """Valid Findings survive to_json/from_json with equal fields and fingerprint."""
    original = Finding(
        why=why,
        test_type=test_type,
        error_type=error_type,
        severity=severity,
        confidence=confidence,
        ai_blind_spot_prior=ai_blind_spot_prior,
        rule_id=rule_id,
        subject_identity=subject_identity,
        detection_mode=detection_mode,
    )
    restored = Finding.from_json(original.to_json())
    assert restored == original
    assert restored.fingerprint == compute_fingerprint(rule_id, subject_identity)
