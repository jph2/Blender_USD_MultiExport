from __future__ import annotations

from typing import List

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup, Scene


class USDME_EndpointPropertyGroup(PropertyGroup):
    """Endpoint definition stored on the scene.

    This is a minimal v1 data model; additional fields like presets,
    export options, and root prim settings will be added as implementation progresses.
    """

    name: StringProperty(
        name="Endpoint Name",
        description="Logical name for this export endpoint",
        default="Endpoint",
    )

    collection_name: StringProperty(
        name="Collection",
        description="Name of the collection used as the export root for this endpoint",
        default="",
    )

    filepath: StringProperty(
        name="File Path",
        description=(
            "Target USD file path for this endpoint. "
            "Store as a Blender-style relative path (e.g. //export/asset.usd)"
        ),
        default="",
        subtype="FILE_PATH",
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Include this endpoint in batch exports",
        default=True,
    )


class USDME_SceneProperties(PropertyGroup):
    """Scene-level container for all USD Multi Export data."""

    endpoints: CollectionProperty(
        type=USDME_EndpointPropertyGroup,
        name="Endpoints",
        description="Export endpoints defined for this scene",
    )

    verbose_logging: BoolProperty(
        name="Verbose Logging",
        description="Enable detailed logging for debugging and bug reports",
        default=False,
    )


def register_scene_properties() -> None:
    """Attach project properties to bpy.types.Scene."""
    Scene.usdme_settings = PointerProperty(type=USDME_SceneProperties)


def unregister_scene_properties() -> None:
    """Remove project properties from bpy.types.Scene."""
    if hasattr(Scene, "usdme_settings"):
        del Scene.usdme_settings


__all__: List[str] = [
    "USDME_EndpointPropertyGroup",
    "USDME_SceneProperties",
    "register_scene_properties",
    "unregister_scene_properties",
]


