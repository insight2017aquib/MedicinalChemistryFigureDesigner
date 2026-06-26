"""FSL-to-ontology figure compilation layer."""

from figure_agent.compiler.compiler import FigureCompiler, compile_figure
from figure_agent.compiler.context import CompilationContext
from figure_agent.compiler.exceptions import (
    CompilationError,
    CompilationMappingError,
    CompilationValidationError,
)
from figure_agent.compiler.mapping import (
    SLOT_TYPE_TO_ENTITY_TYPE,
    resolve_slot_entity_type,
)
from figure_agent.compiler.validator import CompilerValidator

__all__ = [
    "CompilationContext",
    "CompilationError",
    "CompilationMappingError",
    "CompilationValidationError",
    "CompilerValidator",
    "FigureCompiler",
    "SLOT_TYPE_TO_ENTITY_TYPE",
    "compile_figure",
    "resolve_slot_entity_type",
]
