"""Pydantic models for the Figure Specification Language (FSL)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    """Descriptive metadata for a figure specification."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(
        ..., min_length=1, description="Unique figure specification identifier"
    )
    title: str = Field(..., min_length=1, description="Human-readable figure title")
    created: str | None = Field(default=None, description="ISO 8601 creation timestamp")
    modified: str | None = Field(
        default=None, description="ISO 8601 modification timestamp"
    )
    author: str | None = Field(default=None, description="Specification author")
    provenance: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Source references and attribution entries",
    )


class ObjectReference(BaseModel):
    """Reference to an external object, asset, or repository path."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Reference identifier")
    ref: str | None = Field(
        default=None, description="Path or URI to the referenced object"
    )
    label: str | None = Field(
        default=None, description="Human-readable reference label"
    )


class StyleReference(BaseModel):
    """Reference to a style definition in the styles module."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    ref: str = Field(..., min_length=1, description="Path to a styles/ file")


class Panel(BaseModel):
    """A single panel within a figure layout."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Unique panel identifier")
    zones: list[str] = Field(
        default_factory=list, description="Named zones within the panel"
    )
    object_refs: list[str] = Field(
        default_factory=list,
        description="Content slot identifiers displayed in this panel",
    )


class Layout(BaseModel):
    """Spatial organization of panels within a figure."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    type: str = Field(..., min_length=1, description="Layout category identifier")
    panels: list[Panel] = Field(default_factory=list, description="Panel definitions")


class TemplateReference(BaseModel):
    """Reference to a layout template in the templates module."""

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(..., min_length=1, description="Path to a templates/ file")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Template parameter bindings"
    )


class StylesConfig(BaseModel):
    """Style bindings for a figure specification."""

    model_config = ConfigDict(extra="forbid")

    refs: list[StyleReference] = Field(
        default_factory=list, description="Style file references"
    )
    overrides: dict[str, Any] = Field(
        default_factory=dict, description="User-supplied style overrides"
    )


class ContentSlot(BaseModel):
    """Labeled placeholder for user-supplied figure content."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Unique slot identifier")
    label: str | None = Field(default=None, description="Human-readable slot name")
    type: str | None = Field(default=None, description="Slot content type identifier")
    value: Any = Field(default=None, description="User-supplied content")


class RulesConfig(BaseModel):
    """References to rule definitions applied to the figure."""

    model_config = ConfigDict(extra="forbid")

    refs: list[str] = Field(default_factory=list, description="Paths to rules/ files")


class ValidationOptions(BaseModel):
    """Validation configuration for a figure specification."""

    model_config = ConfigDict(extra="forbid")

    refs: list[str] = Field(
        default_factory=list, description="Paths to validation/ files"
    )
    required_checks: list[str] = Field(
        default_factory=list,
        description="Checklist item identifiers that must pass",
    )


class KnowledgeConfig(BaseModel):
    """References to optional knowledge packs."""

    model_config = ConfigDict(extra="forbid")

    packs: list[str] = Field(
        default_factory=list, description="Paths to knowledge/ packs"
    )


class ExportOptions(BaseModel):
    """Export targets and naming for a figure specification."""

    model_config = ConfigDict(extra="forbid")

    formats: list[str] = Field(
        default_factory=list, description="Target export format identifiers"
    )
    naming: str | None = Field(
        default=None, description="File naming pattern reference"
    )


class Figure(BaseModel):
    """Top-level Figure Specification Language document."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    fsl_version: str = Field(..., min_length=1, description="FSL schema version")
    metadata: Metadata
    template: TemplateReference
    layout: Layout
    styles: StylesConfig = Field(default_factory=StylesConfig)
    content_slots: list[ContentSlot] = Field(default_factory=list)
    rules: RulesConfig = Field(default_factory=RulesConfig)
    validation: ValidationOptions = Field(default_factory=ValidationOptions)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    integrations: dict[str, Any] = Field(
        default_factory=dict, description="External tool bindings"
    )
    export: ExportOptions = Field(default_factory=ExportOptions)
