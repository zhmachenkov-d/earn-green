"""earngreen.yaml schema + resolve (AD-5)."""

from earngreen.core.config.defaults import (
    DEFAULT_AI_AUTHOR_LOGINS,
    DEFAULT_AI_COAUTHOR_PATTERNS,
    DEFAULT_AI_MARKER_REGEX,
    DEFAULT_PATH_EXCLUDE_GLOBS,
    DEFAULT_PATH_INCLUDE_GLOBS,
    DEFAULT_SCAN_MODE,
)
from earngreen.core.config.resolve import ConfigError, ResolvedConfig, ScanMode, resolve_config

__all__ = [
    "DEFAULT_AI_AUTHOR_LOGINS",
    "DEFAULT_AI_COAUTHOR_PATTERNS",
    "DEFAULT_AI_MARKER_REGEX",
    "DEFAULT_PATH_EXCLUDE_GLOBS",
    "DEFAULT_PATH_INCLUDE_GLOBS",
    "DEFAULT_SCAN_MODE",
    "ConfigError",
    "ResolvedConfig",
    "ScanMode",
    "resolve_config",
]
