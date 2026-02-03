from __future__ import annotations

from typing import List

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup, Scene


class USDME_StartPointPropertyGroup(PropertyGroup):
    """Start point definition stored on the scene.

    A start point is the stable origin in the DCC for downstream USD pipeline and
    composition arcs. This is a minimal v1 data model; additional fields like
    presets, export options, and root prim settings will be added as implementation progresses.
    """

    name: StringProperty(
        name="Start Point Name",
        description="Logical name for this export start point (pipeline origin)",
        default="Start Point",
    )

    start_point_type: EnumProperty(
        name="Start Point Type",
        description=(
            "Collection: bulk export of multiple objects (requires pivot selection). "
            "Object: single explicit object export."
        ),
        items=[
            ('COLLECTION', "Collection", "Export entire collection or sub-collection"),
            ('OBJECT', "Object", "Export single object"),
        ],
        default='COLLECTION',
    )

    collection_name: StringProperty(
        name="Collection",
        description="Name of the collection used as the export root for this start point",
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
        """Auto-update start point name and filepath when target (collection/object) is selected."""
        # Auto-update start point name based on selected target
        if self.start_point_type == 'COLLECTION' and self.collection_name:
            self.name = self.collection_name
        elif self.start_point_type == 'OBJECT' and self.object_name:
            self.name = self.object_name
        
        # Also update filepath if needed
        self._update_filepath_for_target(context)
    
    def _update_filepath_for_target(self, context):
        """Auto-populate filepath when target (collection/object) is selected and create_subfolder is enabled."""
        if self.create_subfolder and not self.filepath:
            # Get target name
            target_name = self.collection_name if self.start_point_type == 'COLLECTION' else self.object_name
            
            if target_name:
                # Use relative path by default: ./USD_StartPoint/{target_name}.usd
                self.filepath = f"./USD_StartPoint/{target_name}.usd"

    include_subcollections: BoolProperty(
        name="Include Sub-collections",
        description="Include objects from child collections (only for Collection type)",
        default=True,
    )

    normalize_position: BoolProperty(
        name="Normalize Position",
        description="Collection only: bake translation into geometry and reset location to origin",
        default=False,
    )

    normalize_scale: BoolProperty(
        name="Normalize Scale",
        description=(
            "Apply scale to geometry, reset to 1.0; "
            "post-export bake sets child prim scale (1,1,1) in USD. "
            "Currently disabled (upcoming): breaks collection/decals — see 04_Implementation_Plan.md"
        ),
        default=False,
    )

    normalize_rotation: BoolProperty(
        name="Normalize Rotation",
        description=(
            "Bake rotation into geometry, reset to 0; "
            "post-export bake sets child prim rotation (0,0,0) in USD. "
            "Currently disabled (upcoming): breaks collection/decals — see 04_Implementation_Plan.md"
        ),
        default=False,
    )

    collection_pivot_source: EnumProperty(
        name="Collection Pivot",
        description="Collection only: pivot source used for export alignment",
        items=[
            ('NONE', "Preserve", "Preserve existing transforms/pivot"),
            ('WORLD', "World Origin", "Use world origin (0,0,0) as pivot"),
            ('CUSTOM', "Custom XYZ", "Use custom XYZ pivot"),
            ('CURSOR', "3D Cursor", "Use scene 3D cursor location"),
            ('OBJECT', "Object Pivot", "Use another object as a fake parent pivot"),
        ],
        default='NONE',
    )

    collection_pivot_only: BoolProperty(
        name="Pivot Only (no normalize)",
        description="Collection only: rebase to pivot without normalizing transforms",
        default=False,
    )

    collection_pivot_xyz: FloatVectorProperty(
        name="Pivot XYZ",
        description="Custom pivot location for collection export",
        size=3,
        subtype="TRANSLATION",
        default=(0.0, 0.0, 0.0),
    )

    collection_pivot_object: PointerProperty(
        name="Pivot Object",
        description="Object whose pivot is used as a fake parent reference",
        type=bpy.types.Object,
    )

    create_subfolder: BoolProperty(
        name="Create Subfolder",
        description="Create a subfolder named 'USD_StartPoint' in the file location",
        default=True,
        update=lambda self, context: self._update_filepath_for_subfolder(context)
    )
    
    def _update_filepath_for_subfolder(self, context):
        """Auto-populate filepath when create_subfolder is enabled and filepath is empty."""
        if self.create_subfolder and not self.filepath:
            # Get target name
            target_name = self.collection_name if self.start_point_type == 'COLLECTION' else self.object_name
            
            if target_name:
                # Use relative path by default: ./USD_StartPoint/{target_name}.usd
                self.filepath = f"./USD_StartPoint/{target_name}.usd"

    include_origin_metadata: BoolProperty(
        name="Include Origin Metadata",
        description="Add origin file information as custom attributes to root prim",
        default=True,
    )

    export_modifiers: BoolProperty(
        name="Export Modifiers",
        description="Apply all modifiers (including Shrinkwrap, Array, etc.) to the mesh during export",
        default=False,
    )

    object_pivot_normalize: BoolProperty(
        name="Normalize Object Pivot",
        description="Object only: bake location into geometry and reset pivot to origin",
        default=False,
    )

    # Unit conversion system (metric only)
    source_unit: EnumProperty(
        name="Source Unit",
        description="Unit system used in Blender scene (auto-detected from scene scale)",
        items=[
            ('MILLIMETERS', "Millimeters (mm)", "Source unit: millimeters"),
            ('CENTIMETERS', "Centimeters (cm)", "Source unit: centimeters"),
            ('METERS', "Meters (m)", "Source unit: meters"),
            ('KILOMETERS', "Kilometers (km)", "Source unit: kilometers"),
        ],
        default='MILLIMETERS',
    )
    
    target_unit: EnumProperty(
        name="Target Unit",
        description="Unit system for exported USD file",
        items=[
            ('MILLIMETERS', "Millimeters (mm)", "Target unit: millimeters"),
            ('CENTIMETERS', "Centimeters (cm)", "Target unit: centimeters"),
            ('METERS', "Meters (m)", "Target unit: meters"),
            ('KILOMETERS', "Kilometers (km)", "Target unit: kilometers"),
        ],
        default='METERS',
    )
    
    def detect_source_unit(self, context) -> str:
        """Auto-detect source unit from Blender scene unit settings."""
        if not context or not context.scene:
            return 'MILLIMETERS'  # Default fallback
        
        scene = context.scene
        unit_settings = scene.unit_settings
        
        # Blender's unit_settings.scale_length is the scale relative to meters
        # For example: 0.001 = millimeters, 0.01 = centimeters, 1.0 = meters, 1000.0 = kilometers
        scale_length = unit_settings.scale_length
        
        # Detect unit based on scale_length (with tolerance for floating point)
        if abs(scale_length - 0.001) < 0.0001:
            return 'MILLIMETERS'
        elif abs(scale_length - 0.01) < 0.0001:
            return 'CENTIMETERS'
        elif abs(scale_length - 1.0) < 0.0001:
            return 'METERS'
        elif abs(scale_length - 1000.0) < 100.0:  # Allow some tolerance for km
            return 'KILOMETERS'
        else:
            # Fallback: try to determine from unit system
            unit_system = unit_settings.system
            if unit_system == 'METRIC':
                # Try to infer from scale_length
                if scale_length < 0.01:
                    return 'MILLIMETERS'
                elif scale_length < 0.1:
                    return 'CENTIMETERS'
                elif scale_length < 100:
                    return 'METERS'
                else:
                    return 'KILOMETERS'
            else:
                # Non-metric or unknown, default to millimeters
                return 'MILLIMETERS'
    
    def get_scale_factor(self) -> float:
        """Calculate scale factor from source_unit to target_unit conversion."""
        # Metric conversion factors (relative to meters)
        unit_factors = {
            'MILLIMETERS': 0.001,   # 1mm = 0.001m
            'CENTIMETERS': 0.01,    # 1cm = 0.01m
            'METERS': 1.0,          # 1m = 1m
            'KILOMETERS': 1000.0,   # 1km = 1000m
        }
        
        source_factor = unit_factors.get(self.source_unit, 1.0)
        target_factor = unit_factors.get(self.target_unit, 1.0)
        
        # Convert: source_value * (source_factor / target_factor) = target_value
        # Example: 2700mm to meters: 2700 * (0.001 / 1.0) = 2.7m
        if target_factor == 0:
            return 1.0
        return source_factor / target_factor
    
    # Up-axis conversion (for Omniverse compatibility)
    y_is_up: BoolProperty(
        name="Y is Up",
        description=(
            "Convert from Blender's Z-up to Y-up (for Omniverse compatibility). "
            "Rotates scene -90° around X axis during export."
        ),
        default=False,
    )

    filepath: StringProperty(
        name="File Path",
        description=(
            "Target USD file path for this start point. "
            "Store as a Blender-style relative path (e.g. //export/asset.usd)"
        ),
        default="",
        subtype="FILE_PATH",
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Include this start point in batch exports",
        default=True,
    )


class USDME_SceneProperties(PropertyGroup):
    """Scene-level container for all USD Multi Export data."""

    start_points: CollectionProperty(
        type=USDME_StartPointPropertyGroup,
        name="Start Points",
        description="Export start points defined for this scene (pipeline origins)",
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
    "USDME_StartPointPropertyGroup",
    "USDME_SceneProperties",
    "register_scene_properties",
    "unregister_scene_properties",
]


