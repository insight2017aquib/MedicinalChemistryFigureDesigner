"""Knowledge pack format constants and schema metadata."""

from __future__ import annotations

PACK_FORMAT_VERSION = "1.0.0"

PACK_MANIFEST_FILENAME = "pack.yaml"

VALID_PACK_STATUSES = frozenset({"draft", "published", "deprecated", "archived"})

VALID_ENTRY_KINDS = frozenset(
    {
        "convention",
        "pattern",
        "terminology",
        "constraint",
        "reference",
    }
)

VALID_REVIEW_STATUSES = frozenset(
    {
        "unreviewed",
        "in_review",
        "approved",
        "rejected",
    }
)