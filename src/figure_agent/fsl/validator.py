"""Semantic validation for parsed FSL figure documents."""

from __future__ import annotations

from figure_agent.core.constants import (
    KNOWN_LAYOUT_TYPES,
    KNOWN_TEMPLATES,
    LAYOUT_PANEL_RULES,
    SUPPORTED_FSL_VERSIONS,
)
from figure_agent.fsl.exceptions import FSLValidationError
from figure_agent.fsl.models import Figure


class FSLValidator:
    """Validate structural consistency of a parsed ``Figure`` document.

    Performs semantic checks beyond Pydantic schema validation. Does not
    validate scientific content.
    """

    def validate(self, figure: Figure) -> None:
        """Run all semantic validation checks.

        Args:
            figure: Parsed figure specification.

        Raises:
            FSLValidationError: If one or more validation checks fail.
        """
        errors: list[str] = []
        errors.extend(self._check_fsl_version(figure))
        errors.extend(self._check_template_reference(figure))
        errors.extend(self._check_duplicate_panel_ids(figure))
        errors.extend(self._check_duplicate_slot_ids(figure))
        errors.extend(self._check_layout_consistency(figure))
        errors.extend(self._check_panel_object_references(figure))

        if errors:
            raise FSLValidationError("FSL semantic validation failed", errors=errors)

    def _check_fsl_version(self, figure: Figure) -> list[str]:
        """Ensure the document declares a supported FSL version."""
        if figure.fsl_version not in SUPPORTED_FSL_VERSIONS:
            supported = ", ".join(sorted(SUPPORTED_FSL_VERSIONS))
            return [
                f"fsl_version '{figure.fsl_version}' is unsupported; "
                f"expected one of: {supported}"
            ]
        return []

    def _check_template_reference(self, figure: Figure) -> list[str]:
        """Ensure the template reference points to a known repository template."""
        template_ref = _normalize_path(figure.template.ref)
        known = {_normalize_path(item) for item in KNOWN_TEMPLATES}
        if template_ref not in known:
            known_list = ", ".join(sorted(KNOWN_TEMPLATES))
            return [
                f"template.ref '{figure.template.ref}' is unknown; "
                f"expected one of: {known_list}"
            ]
        return []

    def _check_duplicate_panel_ids(self, figure: Figure) -> list[str]:
        """Detect duplicate panel identifiers."""
        seen: set[str] = set()
        errors: list[str] = []
        for panel in figure.layout.panels:
            if panel.id in seen:
                errors.append(f"duplicate panel id '{panel.id}'")
            seen.add(panel.id)
        return errors

    def _check_duplicate_slot_ids(self, figure: Figure) -> list[str]:
        """Detect duplicate content slot identifiers."""
        seen: set[str] = set()
        errors: list[str] = []
        for slot in figure.content_slots:
            if slot.id in seen:
                errors.append(f"duplicate content slot id '{slot.id}'")
            seen.add(slot.id)
        return errors

    def _check_layout_consistency(self, figure: Figure) -> list[str]:
        """Validate panel counts against the declared layout type."""
        layout_type = figure.layout.type
        panel_count = len(figure.layout.panels)

        if layout_type not in KNOWN_LAYOUT_TYPES:
            return [
                f"layout.type '{layout_type}' is unknown; "
                f"expected one of: {', '.join(sorted(KNOWN_LAYOUT_TYPES))}"
            ]

        minimum, maximum = LAYOUT_PANEL_RULES[layout_type]
        errors: list[str] = []

        if panel_count < minimum:
            errors.append(
                f"layout.type '{layout_type}' requires at least {minimum} panel(s), "
                f"found {panel_count}"
            )
        if maximum is not None and panel_count > maximum:
            errors.append(
                f"layout.type '{layout_type}' allows at most {maximum} panel(s), "
                f"found {panel_count}"
            )

        return errors

    def _check_panel_object_references(self, figure: Figure) -> list[str]:
        """Ensure panel object references point to defined content slots."""
        slot_ids = {slot.id for slot in figure.content_slots}
        errors: list[str] = []

        for panel in figure.layout.panels:
            for object_ref in panel.object_refs:
                if object_ref not in slot_ids:
                    errors.append(
                        f"panel '{panel.id}' references unknown object '{object_ref}'; "
                        f"defined content slots: {sorted(slot_ids) or ['(none)']}"
                    )

        return errors


def _normalize_path(path: str) -> str:
    """Normalize repository-style paths for comparison."""
    return path.replace("\\", "/").strip().lower()
