"""Pydantic models for versioned knowledge pack manifests."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from figure_agent.knowledge.schema import (
    PACK_FORMAT_VERSION,
    VALID_ENTRY_KINDS,
    VALID_PACK_STATUSES,
    VALID_REVIEW_STATUSES,
)
from figure_agent.knowledge.semver import SemanticVersion


class PackProvenance(BaseModel):
    """Provenance metadata for a knowledge pack or entry."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    maintainer: str = Field(..., min_length=1)
    organization: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    license: str | None = None
    created_at: date
    updated_at: date
    review_status: str = "unreviewed"
    notes: str | None = None

    @field_validator("review_status")
    @classmethod
    def _validate_review_status(cls, value: str) -> str:
        if value not in VALID_REVIEW_STATUSES:
            raise ValueError(f"review_status must be one of {sorted(VALID_REVIEW_STATUSES)}")
        return value


class EntryProvenance(BaseModel):
    """Provenance metadata for a single knowledge entry."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    curator: str = Field(..., min_length=1)
    source_ref: str = Field(..., min_length=1)
    retrieved_at: date | None = None
    confidence: str | None = None
    notes: str | None = None


class PackDependency(BaseModel):
    """Declared dependency on another knowledge pack."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, pattern=r"^[a-z][a-z0-9-]*$")
    version_constraint: str = Field(..., min_length=1)
    optional: bool = False

    @field_validator("version_constraint")
    @classmethod
    def _validate_constraint_syntax(cls, value: str) -> str:
        # Validate operators and version tokens parse correctly.
        from figure_agent.knowledge.semver import satisfies

        probe = SemanticVersion.parse("1.0.0")
        satisfies(probe, value)
        return value


class PackInheritance(BaseModel):
    """Reference to a parent pack for inheritance."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, pattern=r"^[a-z][a-z0-9-]*$")
    version_constraint: str | None = None

    @field_validator("version_constraint")
    @classmethod
    def _validate_constraint_syntax(cls, value: str | None) -> str | None:
        if value is None:
            return value
        from figure_agent.knowledge.semver import satisfies

        satisfies(SemanticVersion.parse("1.0.0"), value)
        return value


class KnowledgeEntry(BaseModel):
    """A single curated knowledge item within a pack."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, pattern=r"^[a-z][a-z0-9._-]*$")
    kind: str
    title: str = Field(..., min_length=1)
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    provenance: EntryProvenance
    content: dict[str, Any] = Field(default_factory=dict)

    @field_validator("kind")
    @classmethod
    def _validate_kind(cls, value: str) -> str:
        if value not in VALID_ENTRY_KINDS:
            raise ValueError(f"kind must be one of {sorted(VALID_ENTRY_KINDS)}")
        return value


class KnowledgePackManifest(BaseModel):
    """Machine-readable knowledge pack manifest (``pack.yaml``)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    pack_format_version: str = Field(default=PACK_FORMAT_VERSION)
    id: str = Field(..., min_length=1, pattern=r"^[a-z][a-z0-9-]*$")
    semantic_version: str
    name: str = Field(..., min_length=1)
    description: str = ""
    domain: str = Field(..., min_length=1)
    status: str = "draft"
    provenance: PackProvenance
    extends: str | PackInheritance | None = None
    depends_on: list[PackDependency] = Field(default_factory=list)
    aliases: dict[str, list[str]] = Field(default_factory=dict)
    entries: list[KnowledgeEntry] = Field(default_factory=list)

    @field_validator("pack_format_version")
    @classmethod
    def _validate_format_version(cls, value: str) -> str:
        if value != PACK_FORMAT_VERSION:
            raise ValueError(
                f"pack_format_version must be {PACK_FORMAT_VERSION!r}, got {value!r}"
            )
        return value

    @field_validator("semantic_version")
    @classmethod
    def _validate_semantic_version(cls, value: str) -> str:
        SemanticVersion.parse(value)
        return value

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in VALID_PACK_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_PACK_STATUSES)}")
        return value

    @field_validator("aliases")
    @classmethod
    def _validate_aliases(
        cls,
        value: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        seen: set[str] = set()
        for canonical, alias_list in value.items():
            if not canonical.strip():
                raise ValueError("alias canonical keys must not be empty")
            for alias in alias_list:
                if not alias.strip():
                    raise ValueError("alias values must not be empty")
                if alias in seen:
                    raise ValueError(f"duplicate alias: {alias!r}")
                seen.add(alias)
        return value

    @model_validator(mode="after")
    def _validate_unique_entry_ids(self) -> KnowledgePackManifest:
        entry_ids = [entry.id for entry in self.entries]
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("entry ids must be unique within a pack")
        return self

    @property
    def version(self) -> SemanticVersion:
        """Parsed semantic version."""
        return SemanticVersion.parse(self.semantic_version)

    @property
    def inheritance(self) -> PackInheritance | None:
        """Normalized inheritance reference."""
        if self.extends is None:
            return None
        if isinstance(self.extends, PackInheritance):
            return self.extends
        return PackInheritance(id=self.extends)


class ResolvedKnowledgePack(BaseModel):
    """Fully resolved pack after inheritance and dependency validation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    semantic_version: str
    name: str
    description: str
    domain: str
    status: str
    provenance: PackProvenance
    depends_on: list[PackDependency]
    aliases: dict[str, list[str]]
    entries: list[KnowledgeEntry]
    inherited_from: list[str] = Field(default_factory=list)
    resolved_dependencies: list[str] = Field(default_factory=list)
    source_path: str | None = None