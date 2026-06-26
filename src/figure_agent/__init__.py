"""Figure Agent — scientific figure specification toolkit."""

from figure_agent.fsl.models import Figure
from figure_agent.fsl.parser import load_json, load_yaml, parse, validate_schema
from figure_agent.fsl.serializer import to_json, to_yaml
from figure_agent.fsl.validator import FSLValidator

__all__ = [
    "Figure",
    "FSLValidator",
    "load_json",
    "load_yaml",
    "parse",
    "to_json",
    "to_yaml",
    "validate_schema",
]

__version__ = "0.3.0"
