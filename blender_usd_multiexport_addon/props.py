from __future__ import annotations

from typing import List

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
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

    endpoint_type: EnumProperty(
        name="Endpoint Type",
        description="Type of export target",
        items=[
            ('COLLECTION', "Collection", "Export entire collection or sub-collection"),
            ('OBJECT', "Object", "Export single object"),
        ],
        default='COLLECTION',
    )

    collection_name: StringProperty(
        name="Collection",
        description="Name of the collection used as the export root for this endpoint",
        default="",
        update=lambda self, context: self._update_name_and_filepath(context)
    )

    object_name: StringProperty(
        name="Object",
        description="Name of the object used as export target",
        default="",
        update=lambda self, context: self._update_name_and_filepath(context)
    )
    
    def _update_name_and_filepath(self, context):
        """Auto-update endpoint name and filepath when target (collection/object) is selected."""
        # Auto-update endpoint name based on selected target
        if self.endpoint_type == 'COLLECTION' and self.collection_name:
            self.name = self.collection_name
        elif self.endpoint_type == 'OBJECT' and self.object_name:
            self.name = self.object_name
        
        # Also update filepath if needed
        self._update_filepath_for_target(context)
    
    def _update_filepath_for_target(self, context):
        """Auto-populate filepath when target (collection/object) is selected and create_subfolder is enabled."""
        if self.create_subfolder and not self.filepath:
            # Get target name
            target_name = self.collection_name if self.endpoint_type == 'COLLECTION' else self.object_name
            
            if target_name:
                # Use relative path by default: ./USD_Endpoint/{target_name}.usd
                self.filepath = f"./USD_Endpoint/{target_name}.usd"

    include_subcollections: BoolProperty(
        name="Include Sub-collections",
        description="Include objects from child collections (only for Collection type)",
        default=True,
    )

    create_subfolder: BoolProperty(
        name="Create Subfolder",
        description="Create a subfolder named 'USD_Endpoint' in the file location",
        default=True,
        update=lambda self, context: self._update_filepath_for_subfolder(context)
    )
    
    def _update_filepath_for_subfolder(self, context):
        """Auto-populate filepath when create_subfolder is enabled and filepath is empty."""
        if self.create_subfolder and not self.filepath:
            # Get target name
            target_name = self.collection_name if self.endpoint_type == 'COLLECTION' else self.object_name
            
            if target_name:
                # Use relative path by default: ./USD_Endpoint/{target_name}.usd
                self.filepath = f"./USD_Endpoint/{target_name}.usd"

    include_origin_metadata: BoolProperty(
        name="Include Origin Metadata",
        description="Add origin file information as custom attributes to root prim",
        default=True,
    )

    export_subdivision: BoolProperty(
        name="Export Subdivision",
        description="Bake subdivision surfaces into the mesh during export (uses RENDER evaluation mode)",
        default=True,
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


