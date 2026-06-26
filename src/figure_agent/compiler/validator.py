"""Validation for FSL-to-ontology compilation output."""

from __future__ import annotations

from figure_agent.compiler.context import CompilationContext
from figure_agent.compiler.exceptions import CompilationValidationError
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.ontology.validator import OntologyValidator


class CompilerValidator:
    """Validate compilation mappings and resulting ontology graphs.

    Performs structural checks only. Does not validate scientific content.
    """

    def validate_context(self, context: CompilationContext) -> None:
        """Validate compilation mappings before graph assembly.

        Args:
            context: Compilation state after mapping.

        Raises:
            CompilationValidationError: If mapping validation fails.
        """
        errors: list[str] = []
        errors.extend(self._check_all_panels_mapped(context))
        errors.extend(self._check_all_slots_mapped(context))
        errors.extend(self._check_missing_panel_references(context))
        errors.extend(self._check_orphan_slots(context))
        errors.extend(self._check_duplicate_generated_ids(context))

        if errors:
            raise CompilationValidationError(
                "Compilation mapping validation failed",
                errors=errors,
            )

    def validate_graph(self, graph: OntologyGraph) -> None:
        """Validate the compiled ontology graph structure.

        Args:
            graph: Compiled ontology graph.

        Raises:
            CompilationValidationError: If ontology validation fails.
        """
        try:
            OntologyValidator().validate(graph)
        except Exception as exc:
            raise CompilationValidationError(
                "Compiled ontology graph failed validation",
                errors=[str(exc)],
            ) from exc

    def _check_all_panels_mapped(self, context: CompilationContext) -> list[str]:
        errors: list[str] = []
        for panel in context.figure.layout.panels:
            if panel.id not in context.mapped_panels:
                errors.append(
                    f"panel '{panel.id}' was not mapped to an ontology entity"
                )
            elif context.get_entity_id("panel", panel.id) is None:
                errors.append(
                    f"panel '{panel.id}' has no ontology entity ID in object registry"
                )
        return errors

    def _check_all_slots_mapped(self, context: CompilationContext) -> list[str]:
        errors: list[str] = []
        for slot in context.figure.content_slots:
            if slot.id not in context.mapped_slots:
                errors.append(
                    f"content slot '{slot.id}' was not mapped to an ontology entity"
                )
            elif context.get_entity_id("slot", slot.id) is None:
                errors.append(
                    f"content slot '{slot.id}' has no ontology entity ID in object registry"
                )
        return errors

    def _check_missing_panel_references(self, context: CompilationContext) -> list[str]:
        errors: list[str] = []
        slot_ids = {slot.id for slot in context.figure.content_slots}

        for panel in context.figure.layout.panels:
            for object_ref in panel.object_refs:
                if object_ref not in slot_ids:
                    errors.append(
                        f"panel '{panel.id}' references unknown content slot "
                        f"'{object_ref}'"
                    )
                elif context.get_entity_id("slot", object_ref) is None:
                    errors.append(
                        f"panel '{panel.id}' references unmapped content slot "
                        f"'{object_ref}'"
                    )
        return errors

    def _check_orphan_slots(self, context: CompilationContext) -> list[str]:
        errors: list[str] = []
        for slot in context.figure.content_slots:
            if slot.id not in context.referenced_slots:
                errors.append(
                    f"content slot '{slot.id}' is orphaned (not referenced by any panel)"
                )
        return errors

    def _check_duplicate_generated_ids(self, context: CompilationContext) -> list[str]:
        if len(context.generated_ids) != len(set(context.object_registry.values())):
            return ["duplicate ontology entity IDs were generated during compilation"]
        return []
