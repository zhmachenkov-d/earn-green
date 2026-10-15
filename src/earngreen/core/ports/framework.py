"""Framework adapter port contract (AD-10)."""

from __future__ import annotations

from typing import Protocol

from earngreen.core.config import ResolvedConfig
from earngreen.core.ports.types import ParsedTarget, ParseError, ScanTarget, SmellCandidate


class FrameworkPort(Protocol):
    """Collect / parse / analyze behind core — adapters never author Findings."""

    def collect_scan_targets(self, config: ResolvedConfig) -> list[ScanTarget]:
        """Discover scan-targets; must call ``config.filter_scan_targets``."""
        ...

    def parse_target(self, target: ScanTarget) -> ParsedTarget | ParseError:
        """Parse one target; expected failures return ``ParseError`` (no raise)."""
        ...

    def analyze_target(self, parsed: ParsedTarget) -> list[SmellCandidate]:
        """Emit smell candidates for a successfully parsed target."""
        ...
