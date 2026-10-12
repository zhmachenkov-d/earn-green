"""Unit tests for Finding schema + fingerprint (I/O matrix)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from earngreen.core.findings import (
    UNKNOWN_CONFIDENCE,
    UNKNOWN_SEVERITY,
    UNKNOWN_STR,
    DetectionMode,
    ErrorType,
    Finding,
    FindingValidationError,
    compute_fingerprint,
)
from earngreen.core.findings import TestType as FindingTestType


def _sample_finding(**overrides: Any) -> Finding:
    kwargs: dict[str, Any] = {
        "why": "no behavioral asserts on CUT",
        "test_type": FindingTestType.UNIT,
        "error_type": ErrorType.NO_BEHAVIORAL_ASSERT,
        "severity": 3,
        "confidence": 0.8,
        "ai_blind_spot_prior": "high",
        "rule_id": "advisory.no_behavioral_assert",
        "subject_identity": "tests/test_x.py::test_x",
        "schema_version": 1,
    }
    kwargs.update(overrides)
    return Finding(**kwargs)


def test_round_trip_equals_original() -> None:
    original = _sample_finding(detection_mode=DetectionMode.STATIC)
    restored = Finding.from_json(original.to_json())
    assert restored == original
    assert restored.fingerprint == original.fingerprint


def test_missing_required_key_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    del wire["why"]
    with pytest.raises(FindingValidationError, match="missing required key"):
        Finding.from_json(wire)


def test_missing_fingerprint_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    del wire["fingerprint"]
    with pytest.raises(FindingValidationError, match="missing required key"):
        Finding.from_json(wire)


def test_fingerprint_stable_across_attribute_changes() -> None:
    a = _sample_finding(why="one", severity=1)
    b = _sample_finding(why="two", severity=5, confidence=0.1)
    assert a.fingerprint == b.fingerprint
    assert a.fingerprint == compute_fingerprint(a.rule_id, a.subject_identity)


def test_fingerprint_differs_when_identity_changes() -> None:
    base = _sample_finding()
    other_rule = _sample_finding(rule_id="advisory.tautology")
    other_subject = _sample_finding(subject_identity="tests/test_y.py::test_y")
    assert base.fingerprint != other_rule.fingerprint
    assert base.fingerprint != other_subject.fingerprint


def test_fingerprint_mismatch_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["fingerprint"] = "0" * 64
    with pytest.raises(FindingValidationError, match="fingerprint mismatch"):
        Finding.from_json(wire)


def test_unknown_attrs_present_with_sentinels() -> None:
    finding = _sample_finding(
        why=UNKNOWN_STR,
        test_type=FindingTestType.UNKNOWN,
        error_type=ErrorType.UNKNOWN,
        severity=UNKNOWN_SEVERITY,
        confidence=UNKNOWN_CONFIDENCE,
        ai_blind_spot_prior=UNKNOWN_STR,
    )
    wire = finding.to_wire_dict()
    for key in (
        "why",
        "test_type",
        "error_type",
        "severity",
        "confidence",
        "ai_blind_spot_prior",
    ):
        assert key in wire
    assert wire["why"] == UNKNOWN_STR
    assert wire["test_type"] == UNKNOWN_STR
    assert wire["error_type"] == UNKNOWN_STR
    assert wire["severity"] == UNKNOWN_SEVERITY
    assert wire["confidence"] == UNKNOWN_CONFIDENCE
    assert wire["ai_blind_spot_prior"] == UNKNOWN_STR
    assert "detection_mode" not in wire


def test_detection_mode_omitted_when_unset() -> None:
    finding = _sample_finding()
    assert finding.detection_mode is None
    assert "detection_mode" not in finding.to_wire_dict()
    assert "detection_mode" not in json.loads(finding.to_json())


@pytest.mark.parametrize("mode", [DetectionMode.STATIC, DetectionMode.MUTATION])
def test_detection_mode_round_trips_when_set(mode: DetectionMode) -> None:
    original = _sample_finding(detection_mode=mode)
    restored = Finding.from_json(original.to_json())
    assert restored.detection_mode == mode
    assert json.loads(original.to_json())["detection_mode"] == mode.value


def test_invalid_detection_mode_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["detection_mode"] = "heuristic"
    with pytest.raises(FindingValidationError, match="detection_mode"):
        Finding.from_json(wire)


def test_empty_rule_id_rejected_at_construct() -> None:
    with pytest.raises(FindingValidationError, match="rule_id"):
        _sample_finding(rule_id="")


def test_empty_subject_identity_rejected_at_construct() -> None:
    with pytest.raises(FindingValidationError, match="subject_identity"):
        _sample_finding(subject_identity="")


def test_empty_rule_id_rejected_on_deserialize() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["rule_id"] = ""
    wire["fingerprint"] = "deadbeef"
    with pytest.raises(FindingValidationError, match="rule_id"):
        Finding.from_json(wire)


def test_severity_float_rejected() -> None:
    with pytest.raises(FindingValidationError, match="severity"):
        _sample_finding(severity=1.0)


def test_severity_float_rejected_on_deserialize() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["severity"] = 1.0
    with pytest.raises(FindingValidationError, match="severity"):
        Finding.from_json(wire)


def test_severity_out_of_range_rejected() -> None:
    with pytest.raises(FindingValidationError, match="severity"):
        _sample_finding(severity=6)


def test_confidence_out_of_range_rejected() -> None:
    with pytest.raises(FindingValidationError, match="confidence"):
        _sample_finding(confidence=1.5)


def test_confidence_unknown_sentinel_accepted() -> None:
    finding = _sample_finding(confidence=UNKNOWN_CONFIDENCE)
    assert finding.confidence == UNKNOWN_CONFIDENCE


def test_bad_enum_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["test_type"] = "smoke"
    with pytest.raises(FindingValidationError, match="test_type"):
        Finding.from_json(wire)


def test_bad_error_type_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["error_type"] = "not_a_class"
    with pytest.raises(FindingValidationError, match="error_type"):
        Finding.from_json(wire)


def test_missing_schema_version_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    del wire["schema_version"]
    with pytest.raises(FindingValidationError, match="missing required key"):
        Finding.from_json(wire)


def test_non_int_schema_version_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["schema_version"] = "1"
    with pytest.raises(FindingValidationError, match="schema_version"):
        Finding.from_json(wire)


@pytest.mark.parametrize("bad_version", [True, 1.0])
def test_construct_rejects_non_int_schema_version_equal_to_one(bad_version: object) -> None:
    with pytest.raises(FindingValidationError, match="schema_version"):
        _sample_finding(schema_version=bad_version)


def test_wrong_schema_version_rejected() -> None:
    wire = _sample_finding().to_wire_dict()
    wire["schema_version"] = 2
    with pytest.raises(FindingValidationError, match="schema_version"):
        Finding.from_json(wire)


def test_embedded_nul_rejected_in_identity_fields() -> None:
    with pytest.raises(FindingValidationError, match="NUL"):
        _sample_finding(rule_id="rule\0extra")
    with pytest.raises(FindingValidationError, match="NUL"):
        _sample_finding(subject_identity="tests/a.py::t\0x")
    with pytest.raises(ValueError, match="NUL"):
        compute_fingerprint("rule\0extra", "subject")
    with pytest.raises(ValueError, match="NUL"):
        compute_fingerprint("rule", "subject\0extra")


def test_fingerprint_not_trusted_at_construct() -> None:
    finding = _sample_finding()
    assert finding.fingerprint == compute_fingerprint(
        "advisory.no_behavioral_assert",
        "tests/test_x.py::test_x",
    )
    # frozen dataclass: fingerprint is not a constructor argument
    with pytest.raises(TypeError):
        Finding(  # type: ignore[call-arg]
            why="x",
            test_type=FindingTestType.UNIT,
            error_type=ErrorType.UNKNOWN,
            severity=0,
            confidence=-1.0,
            ai_blind_spot_prior="unknown",
            rule_id="r",
            subject_identity="s",
            fingerprint="forged",
        )
