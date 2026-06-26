"""Renderer-independent visual scene layer."""

from figure_agent.renderers.scene.builder import (
    build_visual_scene,
    build_visual_scene_from_layout,
)
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import (
    SCENE_VERSION,
    ConnectorKind,
    LabelAnchor,
    PrimitiveKind,
    ScenePalette,
    SceneStyle,
    StyleReference,
    VisualConnector,
    VisualGroup,
    VisualLabel,
    VisualPanel,
    VisualPrimitive,
    VisualScene,
)

__all__ = [
    "SCENE_VERSION",
    "ConnectorKind",
    "LabelAnchor",
    "PrimitiveKind",
    "SceneBuildError",
    "ScenePalette",
    "SceneStyle",
    "StyleReference",
    "VisualConnector",
    "VisualGroup",
    "VisualLabel",
    "VisualPanel",
    "VisualPrimitive",
    "VisualScene",
    "build_visual_scene",
    "build_visual_scene_from_layout",
]