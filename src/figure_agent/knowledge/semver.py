"""Semantic version parsing and constraint matching."""

from __future__ import annotations

import re
from dataclasses import dataclass

from figure_agent.knowledge.exceptions import KnowledgePackValidationError

_VERSION_RE = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True, order=True)
class SemanticVersion:
    """Parsed semantic version (major.minor.patch)."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> SemanticVersion:
        """Parse a semantic version string."""
        match = _VERSION_RE.match(value.strip())
        if match is None:
            raise KnowledgePackValidationError(
                f"Invalid semantic version: {value!r}",
            )
        major, minor, patch = (int(group) for group in match.groups()[:3])
        return cls(major=major, minor=minor, patch=patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def satisfies(version: SemanticVersion, constraint: str) -> bool:
    """Return whether ``version`` satisfies a composite constraint string."""
    trimmed = constraint.strip()
    if not trimmed:
        raise KnowledgePackValidationError("Version constraint must not be empty")

    if trimmed.startswith("^"):
        return _caret_match(version, SemanticVersion.parse(trimmed[1:]))

    if trimmed.startswith("~"):
        base = SemanticVersion.parse(trimmed[1:])
        return (
            version.major == base.major
            and version.minor == base.minor
            and version >= base
        )

    parts = [part.strip() for part in trimmed.split(",") if part.strip()]
    return all(_matches_single(version, part) for part in parts)


def _matches_single(version: SemanticVersion, part: str) -> bool:
    for operator in (">=", "<=", "==", ">", "<"):
        if part.startswith(operator):
            bound = SemanticVersion.parse(part[len(operator) :])
            if operator == ">=":
                return version >= bound
            if operator == "<=":
                return version <= bound
            if operator == "==":
                return version == bound
            if operator == ">":
                return version > bound
            return version < bound

    return version == SemanticVersion.parse(part)


def _caret_match(version: SemanticVersion, base: SemanticVersion) -> bool:
    """Return whether ``version`` is compatible with caret range ``^base``."""
    if version < base:
        return False
    if base.major > 0:
        return version.major == base.major
    if base.minor > 0:
        return version.major == 0 and version.minor == base.minor
    return version.major == 0 and version.minor == 0