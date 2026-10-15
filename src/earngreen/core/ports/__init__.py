"""Framework ports (AD-10)."""

from earngreen.core.ports.framework import FrameworkPort
from earngreen.core.ports.types import (
    BodyHashInputs,
    ParsedTarget,
    ParseError,
    ScanTarget,
    SmellCandidate,
)

__all__ = [
    "BodyHashInputs",
    "FrameworkPort",
    "ParseError",
    "ParsedTarget",
    "ScanTarget",
    "SmellCandidate",
]
