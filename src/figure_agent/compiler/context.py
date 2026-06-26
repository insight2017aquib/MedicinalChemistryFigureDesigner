"""Compilation state and identifier management."""

from __future__ import annotations

from dataclasses import dataclass, field

from figure_agent.fsl.models import ContentSlot, Figure, Panel


@dataclass
class CompilationContext:
    """Mutable state tracked during FSL-to-ontology compilation.

    Attributes:
        figure: Source FSL figure being compiled.
        object_registry: Maps qualified FSL object keys to ontology entity IDs.
        generated_ids: Ontology entity IDs created during compilation.
        mapped_panels: Panel IDs successfully mapped to ontology entities.
        mapped_slots: Content slot IDs successfully mapped to ontology entities.
        referenced_slots: Content slot IDs referenced by at least one panel.
    """

    figure: Figure
    object_registry: dict[str, str] = field(default_factory=dict)
    generated_ids: set[str] = field(default_factory=set)
    mapped_panels: set[str] = field(default_factory=set)
    mapped_slots: set[str] = field(default_factory=set)
    referenced_slots: set[str] = field(default_factory=set)

    @property
    def figure_id(self) -> str:
        """Return the FSL figure metadata identifier."""
        return self.figure.metadata.id

    @staticmethod
    def object_key(kind: str, fsl_object_id: str) -> str:
        """Build a qualified registry key for an FSL object."""
        return f"{kind}:{fsl_object_id}"

    def register_mapping(
        self,
        kind: str,
        fsl_object_id: str,
        ontology_entity_id: str,
    ) -> None:
        """Record an FSL object to ontology entity mapping."""
        key = self.object_key(kind, fsl_object_id)
        self.object_registry[key] = ontology_entity_id
        self.generated_ids.add(ontology_entity_id)

    def get_entity_id(self, kind: str, fsl_object_id: str) -> str | None:
        """Return the ontology entity ID for a qualified FSL object."""
        return self.object_registry.get(self.object_key(kind, fsl_object_id))

    def make_entity_id(self, kind: str, fsl_id: str) -> str:
        """Generate a namespaced ontology entity identifier."""
        return f"{self.figure_id}:{kind}:{fsl_id}"

    def record_panel(self, panel: Panel) -> None:
        """Mark a panel as mapped."""
        self.mapped_panels.add(panel.id)

    def record_slot(self, slot: ContentSlot) -> None:
        """Mark a content slot as mapped."""
        self.mapped_slots.add(slot.id)

    def record_slot_reference(self, slot_id: str) -> None:
        """Mark a content slot as referenced by a panel."""
        self.referenced_slots.add(slot_id)

    def slot_by_id(self, slot_id: str) -> ContentSlot | None:
        """Look up a content slot by identifier."""
        for slot in self.figure.content_slots:
            if slot.id == slot_id:
                return slot
        return None

    def panel_by_id(self, panel_id: str) -> Panel | None:
        """Look up a panel by identifier."""
        for panel in self.figure.layout.panels:
            if panel.id == panel_id:
                return panel
        return None
