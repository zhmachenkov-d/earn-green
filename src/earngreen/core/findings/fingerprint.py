"""Stable Finding fingerprint: SHA-256 of rule id + subject identity."""

from __future__ import annotations

import hashlib


def compute_fingerprint(rule_id: str, subject_identity: str) -> str:
    """Return SHA-256 hex of UTF-8 ``rule_id + "\\0" + subject_identity``."""
    if not isinstance(rule_id, str):
        msg = "rule_id must be a non-empty string"
        raise ValueError(msg)
    if not isinstance(subject_identity, str):
        msg = "subject_identity must be a non-empty string"
        raise ValueError(msg)
    if not rule_id or not rule_id.strip():
        msg = "rule_id must be a non-empty string"
        raise ValueError(msg)
    if not subject_identity or not subject_identity.strip():
        msg = "subject_identity must be a non-empty string"
        raise ValueError(msg)
    if "\0" in rule_id:
        msg = "rule_id must not contain NUL (\\0)"
        raise ValueError(msg)
    if "\0" in subject_identity:
        msg = "subject_identity must not contain NUL (\\0)"
        raise ValueError(msg)
    payload = f"{rule_id}\0{subject_identity}".encode()
    return hashlib.sha256(payload).hexdigest()
