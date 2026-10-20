"""Minimal port-product DTOs (AD-10) — not the Finding wire schema."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanTarget:
    """A framework-local scan unit (repo-relative path + nodeid)."""

    path: str
    nodeid: str


@dataclass(frozen=True, slots=True)
class BodyHashInputs:
    """Opaque bytes for core to hash; no framework AST objects."""

    payload: bytes


@dataclass(frozen=True, slots=True)
class ParsedTarget:
    """Successful parse product: target plus body-hash inputs."""

    target: ScanTarget
    body_hash_inputs: BodyHashInputs


@dataclass(frozen=True, slots=True)
class SmellCandidate:
    """Framework-local smell evidence; ``rule_hint`` is advisory only."""

    evidence: Mapping[str, object]
    rule_hint: str | None


@dataclass(frozen=True, slots=True)
class ParseError:
    """Expected parse failure (union return — not raised)."""

    message: str
    target: ScanTarget | None
