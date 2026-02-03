from __future__ import annotations

import bpy
from bpy.types import Context, Panel


class USDME_PT_main_panel(Panel):
    """Main UI panel for Blender USD Multi Export.

    Provides a minimal start point list and a single \"Export Start Points\" button.
    Start points are the stable DCC origins for downstream USD pipeline and composition arcs.
    """

    bl_label = "USD Multi Export"
    bl_idname = "USDME_PT_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return hasattr(context.scene, "usdme_settings")

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        settings = scene.usdme_settings

        col = layout.column(align=True)
        col.label(text="Start Points")

        row = col.row(align=True)
        row.operator("usdme.add_start_point", text="Add", icon="ADD")
        row.operator("usdme.remove_start_point", text="Remove", icon="REMOVE")

        box = col.box()

        if not settings.start_points:
            box.label(text="No start points defined for this scene.", icon="INFO")
        else:
            for idx, start_point in enumerate(settings.start_points):
                # Check if start point is complete (type-specific)
                is_complete = False
                if start_point.start_point_type == 'COLLECTION':
                    is_complete = (
                        start_point.collection_name and start_point.collection_name.strip() and
                        start_point.filepath and start_point.filepath.strip()
                    )
                elif start_point.start_point_type == 'OBJECT':
                    is_complete = (
                        start_point.object_name and start_point.object_name.strip() and
                        start_point.filepath and start_point.filepath.strip()
                    )
                
                row_sp = box.row(align=True)
                row_sp.prop(start_point, "enabled", text="")
                
                # Show type icon and warning/checkmark
                if start_point.start_point_type == 'COLLECTION':
                    row_sp.label(text="", icon="OUTLINER_COLLECTION")
                else:
                    row_sp.label(text="", icon="OBJECT_DATA")
                
                if not is_complete:
                    row_sp.label(text="", icon="ERROR")
                else:
                    row_sp.label(text="", icon="CHECKMARK")
                
                row_sp.prop(start_point, "name", text="")
                
                # Type selector
                row_type = box.row()
                row_type.label(text="Type:", icon="SETTINGS")
                row_type.prop(start_point, "start_point_type", expand=True)

                info_row = box.row()
                info_row.scale_y = 0.8
                info_row.label(
                    text="Collection = bulk export with pivot. Object = single asset.",
                    icon="INFO"
                )
                
                # Conditional selectors based on type
                if start_point.start_point_type == 'COLLECTION':
                    # Collection selector with searchable dropdown - use split for label visibility
                    row_collection = box.split(factor=0.25, align=True)
                    row_collection.label(text="Collection:", icon="OUTLINER_COLLECTION")
                    row_collection.prop_search(
                        start_point,
                        "collection_name",
                        bpy.data,
                        "collections",
                        text="",
                        icon="OUTLINER_COLLECTION"
                    )
                    # Increase width for long collection names
                    row_collection.scale_x = 2.0
                    
                    # Sub-collection toggle (only for Collection type)
                    row_subcol = box.row(align=True)
                    row_subcol.prop(start_point, "include_subcollections", text="Include Sub-collections")

                    box_norm = box.box()
                    box_norm.label(text="Collection Normalize / Pivot", icon="PIVOT_MEDIAN")
                    info_norm = box_norm.row()
                    info_norm.scale_y = 0.8
                    info_norm.label(
                        text="Use pivot for alignment; normalize for clean transforms.",
                        icon="INFO"
                    )
                    row_norm = box_norm.row(align=True)
                    row_norm.prop(start_point, "normalize_position", text="Normalize Position")
                    row_norm.prop(start_point, "normalize_scale", text="Normalize Scale")
                    row_norm.prop(start_point, "normalize_rotation", text="Normalize Rotation")

                    row_pivot = box_norm.row(align=True)
                    row_pivot.prop(start_point, "collection_pivot_source", text="Pivot")
                    row_pivot_only = box_norm.row(align=True)
                    row_pivot_only.prop(start_point, "collection_pivot_only", text="Pivot Only (no normalize)")

                    if start_point.collection_pivot_source == 'CUSTOM':
                        row_custom = box_norm.row(align=True)
                        row_custom.prop(start_point, "collection_pivot_xyz", text="Pivot XYZ")
                    elif start_point.collection_pivot_source == 'OBJECT':
                        row_obj = box_norm.row(align=True)
                        row_obj.prop(start_point, "collection_pivot_object", text="Pivot Object")
                else:
                    # Object selector with searchable dropdown - use split for label visibility
                    row_object = box.split(factor=0.25, align=True)
                    row_object.label(text="Object:", icon="OBJECT_DATA")
                    row_object.prop_search(
                        start_point,
                        "object_name",
                        bpy.data,
                        "objects",
                        text="",
                        icon="OBJECT_DATA"
                    )
                    # Increase width for long object names
                    row_object.scale_x = 2.0

                    row_obj_norm = box.row(align=True)
                    row_obj_norm.prop(start_point, "object_pivot_normalize", text="Normalize Object Pivot (to 0,0,0)")
                
                # Filepath selector - use split for label visibility
                row_filepath = box.split(factor=0.25, align=True)
                row_filepath.label(text="Filepath:", icon="FILEBROWSER")
                row_filepath.prop(start_point, "filepath", text="")
                # Increase width for long filepaths
                row_filepath.scale_x = 2.0
                
                # Subfolder creation option
                row_subfolder = box.row(align=True)
                row_subfolder.prop(start_point, "create_subfolder", text="Create Subfolder (USD_StartPoint)")
                
                # Origin metadata option
                row_metadata = box.row(align=True)
                row_metadata.prop(start_point, "include_origin_metadata", text="Include Origin Metadata")
                
                # Modifiers export option (includes all modifiers: Subdivision, Shrinkwrap, Array, etc.)
                row_modifiers = box.row(align=True)
                row_modifiers.prop(start_point, "export_modifiers", text="Export Modifiers (Subdivision, Shrinkwrap, Array, etc.)")
                
                # Unit conversion system
                box_unit = box.box()
                box_unit.label(text="Unit Conversion (Metric)", icon="ARROW_LEFTRIGHT")
                
                # Source unit (auto-detect from scene)
                row_source = box_unit.row(align=True)
                row_source.label(text="From:", icon="IMPORT")
                row_source.prop(start_point, "source_unit", text="")
                # Add button to auto-detect from scene
                detect_op = row_source.operator(
                    "usdme.detect_source_unit",
                    text="Auto",
                    icon="VIEWZOOM"
                )
                detect_op.start_point_index = idx
                
                # Target unit
                row_target = box_unit.row(align=True)
                row_target.label(text="To:", icon="EXPORT")
                row_target.prop(start_point, "target_unit", text="")
                
                # Show calculated scale factor and example
                scale_factor = start_point.get_scale_factor()
                if scale_factor != 1.0:
                    example_row = box_unit.row(align=True)
                    example_row.scale_y = 0.8
                    # Show example conversion with proper unit abbreviations
                    example_value = 2700  # Example: 2700mm
                    converted_value = example_value * scale_factor
                    
                    # Map unit enum to proper abbreviations
                    unit_abbrevs = {
                        'MILLIMETERS': 'mm',
                        'CENTIMETERS': 'cm',
                        'METERS': 'm',
                        'KILOMETERS': 'km',
                    }
                    source_abbrev = unit_abbrevs.get(start_point.source_unit, 'mm')
                    target_abbrev = unit_abbrevs.get(start_point.target_unit, 'm')
                    
                    example_row.label(
                        text=f"  Example: {example_value}{source_abbrev} → {converted_value:.2f}{target_abbrev} (×{scale_factor:.6f})",
                        icon="INFO"
                    )
                else:
                    same_unit_row = box_unit.row(align=True)
                    same_unit_row.scale_y = 0.8
                    same_unit_row.label(text="  No scaling (same units)", icon="INFO")
                
                # Up-axis conversion (Y is up for Omniverse)
                row_yup = box.row(align=True)
                row_yup.prop(start_point, "y_is_up", text="Y is Up (for Omniverse - converts Z-up to Y-up)")
                
                # Selection button - allows user to track which start point belongs to what
                row_select = box.row(align=True)
                select_op = row_select.operator(
                    "usdme.select_start_point_target",
                    text="Select",
                    icon="RESTRICT_SELECT_OFF"
                )
                select_op.start_point_index = idx
                
                # Show warning message if incomplete
                if not is_complete:
                    warning_row = box.row()
                    warning_row.alert = True
                    missing = []
                    if start_point.start_point_type == 'COLLECTION':
                        if not start_point.collection_name or not start_point.collection_name.strip():
                            missing.append("collection")
                    else:
                        if not start_point.object_name or not start_point.object_name.strip():
                            missing.append("object")
                    if not start_point.filepath or not start_point.filepath.strip():
                        missing.append("filepath")
                    warning_row.label(text=f"  ⚠ Missing: {', '.join(missing)}", icon="ERROR")
                
                box.separator()

        layout.separator()

        # Verbose logging toggle
        layout.prop(settings, "verbose_logging")

        col_export = layout.column(align=True)
        col_export.operator("usdme.export_start_points", icon="EXPORT")

        # Bug report controls
        layout.separator()
        col_bug = layout.column(align=True)
        col_bug.operator("usdme.generate_bug_report", text="Generate Bug Report")


class USDME_OT_select_start_point_target(bpy.types.Operator):
    """Select the collection or object associated with this start point in the viewport."""
    
    bl_idname = "usdme.select_start_point_target"
    bl_label = "Select Start Point Target"
    bl_options = {"REGISTER", "UNDO"}
    
    start_point_index: bpy.props.IntProperty(
        name="Start Point Index",
        description="Index of the start point to select",
        default=0
    )
    
    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        
        if self.start_point_index < 0 or self.start_point_index >= len(settings.start_points):
            self.report({"ERROR"}, f"Invalid start point index: {self.start_point_index}")
            return {"CANCELLED"}
        
        start_point = settings.start_points[self.start_point_index]
        
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        if start_point.start_point_type == 'COLLECTION':
            # Select collection objects
            if start_point.collection_name and start_point.collection_name in bpy.data.collections:
                collection = bpy.data.collections[start_point.collection_name]
                
                # Get all objects in collection (and sub-collections if enabled)
                objects_to_select = []
                if start_point.include_subcollections:
                    # Recursive: get all objects from collection and child collections
                    def get_all_objects(coll):
                        objects = list(coll.objects)
                        for child_coll in coll.children:
                            objects.extend(get_all_objects(child_coll))
                        return objects
                    objects_to_select = get_all_objects(collection)
                else:
                    # Only direct objects
                    objects_to_select = list(collection.objects)
                
                # Select objects
                for obj in objects_to_select:
                    if obj.name in context.view_layer.objects:
                        obj.select_set(True)
                
                # Make first object active
                if objects_to_select:
                    context.view_layer.objects.active = objects_to_select[0]
                
                self.report({"INFO"}, f"Selected {len(objects_to_select)} object(s) from collection: {collection.name}")
            else:
                self.report({"WARNING"}, f"Collection '{start_point.collection_name}' not found")
                return {"CANCELLED"}
        
        elif start_point.start_point_type == 'OBJECT':
            # Select single object
            if start_point.object_name and start_point.object_name in bpy.data.objects:
                obj = bpy.data.objects[start_point.object_name]
                
                if obj.name in context.view_layer.objects:
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    self.report({"INFO"}, f"Selected object: {obj.name}")
                else:
                    self.report({"WARNING"}, f"Object '{obj.name}' is not in the current view layer")
                    return {"CANCELLED"}
            else:
                self.report({"WARNING"}, f"Object '{start_point.object_name}' not found")
                return {"CANCELLED"}
        
        return {"FINISHED"}


class USDME_OT_add_start_point(bpy.types.Operator):
    """Add a new USD Multi Export start point to the current scene.
    
    Start points are the stable DCC origins for downstream USD pipeline and composition arcs.
    Automatically detects and uses:
    - Active collection (if available)
    - Or creates a collection from selected objects (if objects are selected)
    - Or creates an empty start point if nothing is selected
    """

    bl_idname = "usdme.add_start_point"
    bl_label = "Add Start Point"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        start_point = settings.start_points.add()
        start_point.name = f"Start Point {len(settings.start_points)}"
        
        # Auto-detect source unit from scene settings
        start_point.source_unit = start_point.detect_source_unit(context)
        
        # Auto-detect type and target based on context
        # Priority: Single object selected → Object type, Collection active → Collection type
        
        # Check if single object is selected (prefer Object type)
        if len(context.selected_objects) == 1:
            obj = context.selected_objects[0]
            start_point.start_point_type = 'OBJECT'
            start_point.object_name = obj.name
            start_point.name = obj.name  # Auto-name start point
            self.report({"INFO"}, f"Added start point with object: {obj.name}")
        # Check if collection is active
        elif hasattr(context, 'view_layer') and context.view_layer.active_layer_collection:
            collection = context.view_layer.active_layer_collection.collection
            start_point.start_point_type = 'COLLECTION'
            start_point.collection_name = collection.name
            start_point.name = collection.name  # Auto-name start point
            self.report({"INFO"}, f"Added start point with collection: {collection.name}")
        # Check if multiple objects selected (default to Collection type)
        elif context.selected_objects:
            # Get collection from first selected object
            obj = context.selected_objects[0]
            if obj.users_collection:
                # Prefer non-scene collection if available
                for coll in obj.users_collection:
                    if coll != context.scene.collection:
                        start_point.start_point_type = 'COLLECTION'
                        start_point.collection_name = coll.name
                        start_point.name = coll.name  # Auto-name start point
                        self.report({"INFO"}, f"Added start point with collection: {coll.name}")
                        break
                # Fallback to first collection
                if not start_point.collection_name and obj.users_collection:
                    start_point.start_point_type = 'COLLECTION'
                    start_point.collection_name = obj.users_collection[0].name
                    start_point.name = obj.users_collection[0].name  # Auto-name start point
                    self.report({"INFO"}, f"Added start point with collection: {obj.users_collection[0].name}")
            else:
                # No collection found, default to Collection type, user must select
                start_point.start_point_type = 'COLLECTION'
                self.report({"INFO"}, "Added start point. Please select a collection or object.")
        else:
            # Nothing selected, default to Collection type
            start_point.start_point_type = 'COLLECTION'
            self.report({"INFO"}, "Added start point. Please select a collection or object.")
        
        return {"FINISHED"}


class USDME_OT_remove_start_point(bpy.types.Operator):
    """Remove the last USD Multi Export start point from the current scene."""

    bl_idname = "usdme.remove_start_point"
    bl_label = "Remove Start Point"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        if settings.start_points:
            settings.start_points.remove(len(settings.start_points) - 1)
        else:
            self.report({"INFO"}, "No start points to remove.")
        return {"FINISHED"}


class USDME_OT_create_collection_from_selected(bpy.types.Operator):
    """Create a new collection from selected objects and optionally add it to a start point."""

    bl_idname = "usdme.create_collection_from_selected"
    bl_label = "Create Collection from Selected"
    bl_description = "Create a new collection from selected objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Only enable if objects are selected."""
        return bool(context.selected_objects)

    def execute(self, context: Context):
        if not context.selected_objects:
            self.report({"WARNING"}, "No objects selected. Please select objects first.")
            return {"CANCELLED"}
        
        # Generate a unique collection name
        base_name = "USD_Export"
        collection_name = base_name
        counter = 1
        while collection_name in bpy.data.collections:
            collection_name = f"{base_name}_{counter:03d}"
            counter += 1
        
        # Create the collection
        collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(collection)
        
        # Move selected objects to the new collection
        moved_count = 0
        for obj in context.selected_objects:
            # Remove from current collections (but keep in scene collection)
            for coll in list(obj.users_collection):
                if coll != context.scene.collection:
                    coll.objects.unlink(obj)
            # Add to new collection
            collection.objects.link(obj)
            moved_count += 1
        
        self.report({"INFO"}, f"Created collection '{collection_name}' with {moved_count} object(s).")
        return {"FINISHED"}


class USDME_OT_detect_source_unit(bpy.types.Operator):
    """Auto-detect source unit from Blender scene unit settings."""
    
    bl_idname = "usdme.detect_source_unit"
    bl_label = "Detect Source Unit"
    bl_options = {"REGISTER", "UNDO"}
    
    start_point_index: bpy.props.IntProperty(
        name="Start Point Index",
        description="Index of the start point to update",
        default=0
    )
    
    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        
        if self.start_point_index < 0 or self.start_point_index >= len(settings.start_points):
            self.report({"ERROR"}, f"Invalid start point index: {self.start_point_index}")
            return {"CANCELLED"}
        
        start_point = settings.start_points[self.start_point_index]
        detected_unit = start_point.detect_source_unit(context)
        start_point.source_unit = detected_unit
        
        unit_names = {
            'MILLIMETERS': 'millimeters',
            'CENTIMETERS': 'centimeters',
            'METERS': 'meters',
            'KILOMETERS': 'kilometers',
        }
        self.report({"INFO"}, f"Detected source unit: {unit_names.get(detected_unit, detected_unit)}")
        return {"FINISHED"}


class USDME_OT_generate_bug_report(bpy.types.Operator):
    """Generate a comprehensive bug report for USD Multi Export issues."""

    bl_idname = "usdme.generate_bug_report"
    bl_label = "Generate Bug Report"
    bl_options = {"REGISTER"}

    def execute(self, context: Context):
        from . import logging_utils

        filepath = logging_utils.log_bug_report()
        if filepath:
            self.report({"INFO"}, f"Bug report saved to: {filepath}")
            # Also show in a popup dialog
            def draw_popup(self, context):
                self.layout.label(text="Bug Report Generated")
                self.layout.label(text=f"Saved to: {filepath}")
                self.layout.label(text="Please attach this file when reporting bugs.")
                self.layout.operator("wm.path_open", text="Open Report Location").filepath = str(filepath)

            context.window_manager.popup_menu(draw_popup, title="Bug Report", icon='INFO')
        else:
            self.report({"ERROR"}, "Failed to generate bug report")

        return {"FINISHED"}


__all__ = [
    "USDME_PT_main_panel",
    "USDME_OT_add_start_point",
    "USDME_OT_create_collection_from_selected",
    "USDME_OT_detect_source_unit",
    "USDME_OT_generate_bug_report",
    "USDME_OT_remove_start_point",
    "USDME_OT_select_start_point_target",
]


