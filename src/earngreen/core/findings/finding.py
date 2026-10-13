"""Versioned Finding schema (schema_version=1) and JSON wire form."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, cast

from earngreen.core.findings.fingerprint import compute_fingerprint

SCHEMA_VERSION_V1: int = 1

UNKNOWN_STR: str = "unknown"
UNKNOWN_SEVERITY: int = 0
UNKNOWN_CONFIDENCE: float = -1.0

_REQUIRED_WIRE_KEYS: frozenset[str] = frozenset(
    {
        "why",
        "test_type",
        "error_type",
        "severity",
        "confidence",
        "ai_blind_spot_prior",
        "rule_id",
        "subject_identity",
        "schema_version",
        "fingerprint",
    }
)
_OPTIONAL_WIRE_KEYS: frozenset[str] = frozenset({"detection_mode"})
_ALLOWED_WIRE_KEYS: frozenset[str] = _REQUIRED_WIRE_KEYS | _OPTIONAL_WIRE_KEYS


class TestType(StrEnum):
    """Closed test_type enum (advisory-classes.md)."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PARAMETRIZED = "parametrized"
    UNKNOWN = "unknown"


class ErrorType(StrEnum):
    """Closed error_type enum (advisory-classes.md)."""

    EMPTY_ASSERT = "empty_assert"
    TAMPER_SWALLOW = "tamper_swallow"
    TAMPER_SKIP = "tamper_skip"
    NO_BEHAVIORAL_ASSERT = "no_behavioral_assert"
    MOCKS_ONLY = "mocks_only"
    TAUTOLOGY = "tautology"
    UNREACHABLE_ASSERT = "unreachable_assert"
    SKIP_NOISE = "skip_noise"
    NEVER_EXERCISED_CUT = "never_exercised_cut"
    OVER_BROAD_EXCEPT = "over_broad_except"
    ORACLE_STATUS_QUO = "oracle_status_quo"
    VACUOUS_PARAMETRIZE = "vacuous_parametrize"
    UNKNOWN = "unknown"


class DetectionMode(StrEnum):
    """Optional Oracle detection_mode."""

    STATIC = "static"
    MUTATION = "mutation"


class FindingValidationError(ValueError):
    """Raised when Finding construction or JSON wire validation fails."""


def _is_json_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_json_number(value: object) -> bool:
    return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)


def _validate_severity(severity: object) -> int:
    if not _is_json_int(severity):
        msg = f"severity must be a JSON int in {{0}} ∪ {{1..5}}, got {severity!r}"
        raise FindingValidationError(msg)
    severity_int = cast(int, severity)
    if severity_int != UNKNOWN_SEVERITY and severity_int not in range(1, 6):
        msg = f"severity must be a JSON int in {{0}} ∪ {{1..5}}, got {severity_int!r}"
        raise FindingValidationError(msg)
    return severity_int


def _validate_confidence(confidence: object) -> float:
    if not _is_json_number(confidence):
        msg = f"confidence must be a JSON number in {{-1.0}} ∪ [0.0, 1.0], got {confidence!r}"
        raise FindingValidationError(msg)
    confidence_float = float(cast(int | float, confidence))
    if confidence_float != UNKNOWN_CONFIDENCE and not (0.0 <= confidence_float <= 1.0):
        msg = f"confidence must be a JSON number in {{-1.0}} ∪ [0.0, 1.0], got {confidence_float!r}"
        raise FindingValidationError(msg)
    return confidence_float


def _validate_non_empty_str(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or not value.strip():
        msg = f"{name} must be a non-empty string"
        raise FindingValidationError(msg)
    if "\0" in value:
        msg = f"{name} must not contain NUL (\\0)"
        raise FindingValidationError(msg)
    return value


def _validate_str(name: str, value: object) -> str:
    if not isinstance(value, str):
        msg = f"{name} must be a string"
        raise FindingValidationError(msg)
    return value


def _parse_enum[E: StrEnum](enum_cls: type[E], name: str, value: object) -> E:
    if isinstance(value, enum_cls):
        return value
    if isinstance(value, StrEnum):
        msg = f"{name} must be {enum_cls.__name__}, got {type(value).__name__}"
        raise FindingValidationError(msg)
    if not isinstance(value, str):
        msg = f"{name} must be a string, got {value!r}"
        raise FindingValidationError(msg)
    try:
        return enum_cls(value)
    except ValueError as exc:
        allowed = ", ".join(repr(m.value) for m in enum_cls)
        msg = f"invalid {name} {value!r}; allowed: {allowed}"
        raise FindingValidationError(msg) from exc


@dataclass(frozen=True)
class Finding:
    """JSON-serializable Finding (schema v1) with stable fingerprint."""

    why: str
    test_type: TestType
    error_type: ErrorType
    severity: int
    confidence: float
    ai_blind_spot_prior: str
    rule_id: str
    subject_identity: str
    schema_version: int = SCHEMA_VERSION_V1
    detection_mode: DetectionMode | None = None
    fingerprint: str = field(init=False)

    SCHEMA_VERSION: ClassVar[int] = SCHEMA_VERSION_V1

    def __post_init__(self) -> None:
        _validate_str("why", self.why)
        object.__setattr__(self, "test_type", _parse_enum(TestType, "test_type", self.test_type))
        object.__setattr__(self, "error_type", _parse_enum(ErrorType, "error_type", self.error_type))
        object.__setattr__(self, "severity", _validate_severity(self.severity))
        object.__setattr__(self, "confidence", _validate_confidence(self.confidence))
        _validate_str("ai_blind_spot_prior", self.ai_blind_spot_prior)
        _validate_non_empty_str("rule_id", self.rule_id)
        _validate_non_empty_str("subject_identity", self.subject_identity)
        if not _is_json_int(self.schema_version) or self.schema_version != SCHEMA_VERSION_V1:
            msg = f"schema_version must be a JSON int equal to {SCHEMA_VERSION_V1}, got {self.schema_version!r}"
            raise FindingValidationError(msg)
        if self.detection_mode is not None:
            object.__setattr__(
                self,
                "detection_mode",
                _parse_enum(DetectionMode, "detection_mode", self.detection_mode),
            )
        object.__setattr__(
            self,
            "fingerprint",
            compute_fingerprint(self.rule_id, self.subject_identity),
        )

    def to_wire_dict(self) -> dict[str, Any]:
        """Return the JSON-serializable wire object (snake_case keys)."""
        data: dict[str, Any] = {
            "why": self.why,
            "test_type": self.test_type.value,
            "error_type": self.error_type.value,
            "severity": self.severity,
            "confidence": self.confidence,
            "ai_blind_spot_prior": self.ai_blind_spot_prior,
            "rule_id": self.rule_id,
            "subject_identity": self.subject_identity,
            "schema_version": self.schema_version,
            "fingerprint": self.fingerprint,
        }
        if self.detection_mode is not None:
            data["detection_mode"] = self.detection_mode.value
        return data

    def to_json(self) -> str:
        """Serialize to a JSON object string."""
        return json.dumps(self.to_wire_dict(), ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def from_json(cls, payload: str | Mapping[str, Any]) -> Finding:
        """Deserialize JSON text or a wire mapping; recompute and verify fingerprint."""
        if isinstance(payload, str):
            try:
                loaded: Any = json.loads(payload)
            except json.JSONDecodeError as exc:
                msg = f"invalid Finding JSON: {exc}"
                raise FindingValidationError(msg) from exc
        else:
            loaded = payload

        if not isinstance(loaded, dict):
            msg = "Finding JSON must be an object"
            raise FindingValidationError(msg)

        data = cast(dict[str, Any], loaded)
        missing = sorted(_REQUIRED_WIRE_KEYS - data.keys())
        if missing:
            msg = f"Finding JSON missing required key(s): {', '.join(missing)}"
            raise FindingValidationError(msg)
        unknown = sorted(data.keys() - _ALLOWED_WIRE_KEYS)
        if unknown:
            msg = f"Finding JSON unknown key(s): {', '.join(unknown)}"
            raise FindingValidationError(msg)

        schema_version = data["schema_version"]
        if not _is_json_int(schema_version):
            msg = f"schema_version must be a JSON int equal to {SCHEMA_VERSION_V1}, got {schema_version!r}"
            raise FindingValidationError(msg)
        if schema_version != SCHEMA_VERSION_V1:
            msg = f"schema_version must be {SCHEMA_VERSION_V1}, got {schema_version!r}"
            raise FindingValidationError(msg)

        wire_fingerprint = data["fingerprint"]
        if not isinstance(wire_fingerprint, str) or not wire_fingerprint:
            msg = "fingerprint must be a non-empty string"
            raise FindingValidationError(msg)

        detection_mode: DetectionMode | None = None
        if data.get("detection_mode") is not None:
            detection_mode = _parse_enum(DetectionMode, "detection_mode", data["detection_mode"])

        finding = cls(
            why=_validate_str("why", data["why"]),
            test_type=_parse_enum(TestType, "test_type", data["test_type"]),
            error_type=_parse_enum(ErrorType, "error_type", data["error_type"]),
            severity=_validate_severity(data["severity"]),
            confidence=_validate_confidence(data["confidence"]),
            ai_blind_spot_prior=_validate_str("ai_blind_spot_prior", data["ai_blind_spot_prior"]),
            rule_id=_validate_non_empty_str("rule_id", data["rule_id"]),
            subject_identity=_validate_non_empty_str("subject_identity", data["subject_identity"]),
            schema_version=SCHEMA_VERSION_V1,
            detection_mode=detection_mode,
        )

        if finding.fingerprint != wire_fingerprint:
            msg = "fingerprint mismatch: wire value does not match recomputation from rule_id and subject_identity"
            raise FindingValidationError(msg)

        return finding
