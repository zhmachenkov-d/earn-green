"""earngreen.yaml load, validate, resolve, and path-rule filter (AD-5)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Final, cast

import yaml

from earngreen.core.config.defaults import (
    DEFAULT_AI_AUTHOR_LOGINS,
    DEFAULT_AI_COAUTHOR_PATTERNS,
    DEFAULT_AI_MARKER_REGEX,
    DEFAULT_PATH_EXCLUDE_GLOBS,
    DEFAULT_PATH_INCLUDE_GLOBS,
    DEFAULT_SCAN_MODE,
)

_ALLOWED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "scan_mode",
        "path_exclude_globs",
        "path_include_globs",
        "ai_coauthor_patterns",
        "ai_author_logins",
        "ai_marker_regex",
    }
)


class ScanMode(StrEnum):
    """Scan scope mode: PR/Action default diff, or full suite."""

    DIFF = "diff"
    FULL = "full"


class ConfigError(ValueError):
    """Raised when earngreen.yaml load or validation fails."""


@dataclass(frozen=True, slots=True)
class ResolvedConfig:
    """Immutable resolved scan-scope + AI provenance knobs."""

    scan_mode: ScanMode
    path_exclude_globs: tuple[str, ...]
    path_include_globs: tuple[str, ...]
    ai_coauthor_patterns: tuple[str, ...]
    ai_author_logins: tuple[str, ...]
    ai_marker_regex: tuple[str, ...]

    def filter_scan_targets(self, candidates: Sequence[str]) -> list[str]:
        """Apply path exclude/include globs; provenance fields never affect the result."""
        kept: list[str] = []
        for raw in candidates:
            posix = _normalize_posix(raw)
            path = PurePosixPath(posix)
            if any(_path_matches(path, pattern) for pattern in self.path_exclude_globs):
                continue
            if self.path_include_globs and not any(_path_matches(path, pattern) for pattern in self.path_include_globs):
                continue
            kept.append(posix)
        return kept


def resolve_config(path: Path | None = None) -> ResolvedConfig:
    """Load and resolve earngreen.yaml, or return fresh-install defaults.

    ``None`` or a missing file yields defaults (not an error). Callers pass the
    path to ``earngreen.yaml``; this does not walk parents to discover it.
    """
    if path is None:
        return _defaults_resolved()
    if not path.exists():
        return _defaults_resolved()
    if not path.is_file():
        msg = f"config path must be a file, got {path}"
        raise ConfigError(msg)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"failed to read config file {path}: {exc}"
        raise ConfigError(msg) from exc

    try:
        loaded: object = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        msg = f"invalid YAML in {path}: {exc}"
        raise ConfigError(msg) from exc

    if loaded is None:
        return _defaults_resolved()
    if not isinstance(loaded, Mapping):
        msg = f"earngreen.yaml root must be a mapping, got {type(loaded).__name__}"
        raise ConfigError(msg)

    return _resolve_from_mapping(cast(Mapping[object, Any], loaded), source=str(path))


def _defaults_resolved() -> ResolvedConfig:
    return ResolvedConfig(
        scan_mode=ScanMode(DEFAULT_SCAN_MODE),
        path_exclude_globs=DEFAULT_PATH_EXCLUDE_GLOBS,
        path_include_globs=DEFAULT_PATH_INCLUDE_GLOBS,
        ai_coauthor_patterns=DEFAULT_AI_COAUTHOR_PATTERNS,
        ai_author_logins=DEFAULT_AI_AUTHOR_LOGINS,
        ai_marker_regex=DEFAULT_AI_MARKER_REGEX,
    )


def _resolve_from_mapping(data: Mapping[object, Any], *, source: str) -> ResolvedConfig:
    for key in data:
        if not isinstance(key, str):
            msg = f"config keys must be strings in {source}, got {key!r}"
            raise ConfigError(msg)
    unknown = sorted(set(cast(Mapping[str, Any], data)) - _ALLOWED_KEYS)
    if unknown:
        keys = ", ".join(unknown)
        msg = f"unknown config key(s) in {source}: {keys}"
        raise ConfigError(msg)

    scan_mode = _parse_scan_mode(data.get("scan_mode", DEFAULT_SCAN_MODE), source=source)
    return ResolvedConfig(
        scan_mode=scan_mode,
        path_exclude_globs=_parse_str_list(
            data.get("path_exclude_globs", list(DEFAULT_PATH_EXCLUDE_GLOBS)),
            key="path_exclude_globs",
            source=source,
        ),
        path_include_globs=_parse_str_list(
            data.get("path_include_globs", list(DEFAULT_PATH_INCLUDE_GLOBS)),
            key="path_include_globs",
            source=source,
        ),
        ai_coauthor_patterns=_parse_str_list(
            data.get("ai_coauthor_patterns", list(DEFAULT_AI_COAUTHOR_PATTERNS)),
            key="ai_coauthor_patterns",
            source=source,
        ),
        ai_author_logins=_parse_str_list(
            data.get("ai_author_logins", list(DEFAULT_AI_AUTHOR_LOGINS)),
            key="ai_author_logins",
            source=source,
        ),
        ai_marker_regex=_parse_str_list(
            data.get("ai_marker_regex", list(DEFAULT_AI_MARKER_REGEX)),
            key="ai_marker_regex",
            source=source,
        ),
    )


def _parse_scan_mode(value: object, *, source: str) -> ScanMode:
    if not isinstance(value, str):
        msg = f"scan_mode must be 'diff' or 'full' in {source}, got {value!r}"
        raise ConfigError(msg)
    try:
        return ScanMode(value)
    except ValueError as exc:
        msg = f"scan_mode must be 'diff' or 'full' in {source}, got {value!r}"
        raise ConfigError(msg) from exc


def _parse_str_list(value: object, *, key: str, source: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        msg = f"{key} must be a list of strings in {source}, got {type(value).__name__}"
        raise ConfigError(msg)
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            msg = f"{key}[{index}] must be a string in {source}, got {type(item).__name__}"
            raise ConfigError(msg)
        if item == "":
            msg = f"{key}[{index}] must be a non-empty string in {source}"
            raise ConfigError(msg)
        items.append(item)
    return tuple(items)


def _normalize_posix(candidate: str) -> str:
    return candidate.replace("\\", "/")


def _glob_match_variants(pattern: str) -> tuple[str, ...]:
    """Expand ``**`` directory globs into forms ``PurePosixPath.match`` accepts.

    Glossary defaults use ``**/vendor/**``-style patterns; a single raw
    ``path.match`` misses top-level and deeper nests (e.g. ``vendor/x.py``,
    ``a/vendor/b/c.py``). Each variant is still matched via ``PurePosixPath.match``.
    """
    variants: list[str] = [pattern]
    if pattern.endswith("/**"):
        base = pattern[:-3]
        variants.append(f"{base}/**/*")
        variants.append(f"{base}/*")
        if base.startswith("**/"):
            rest = base[3:]
            variants.extend([f"{rest}/**", f"{rest}/**/*", f"{rest}/*", rest])
        elif base:
            variants.append(base)
    return tuple(dict.fromkeys(variants))


def _path_matches(path: PurePosixPath, pattern: str) -> bool:
    return any(path.match(variant) for variant in _glob_match_variants(pattern))
