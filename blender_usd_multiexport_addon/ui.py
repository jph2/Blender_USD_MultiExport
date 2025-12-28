from __future__ import annotations

import bpy
from bpy.types import Context, Panel


class USDME_PT_main_panel(Panel):
    """Main UI panel for Blender USD Multi Export.

    Provides a minimal endpoint list and a single \"Export Endpoints\" button.
    More controls (presets, validation feedback, logs) will be added as
    implementation progresses.
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
        col.label(text="Endpoints")

        row = col.row(align=True)
        row.operator("usdme.add_endpoint", text="Add", icon="ADD")
        row.operator("usdme.remove_endpoint", text="Remove", icon="REMOVE")

        box = col.box()

        if not settings.endpoints:
            box.label(text="No endpoints defined for this scene.", icon="INFO")
        else:
            for idx, endpoint in enumerate(settings.endpoints):
                # Check if endpoint is complete (type-specific)
                is_complete = False
                if endpoint.endpoint_type == 'COLLECTION':
                    is_complete = (
                        endpoint.collection_name and endpoint.collection_name.strip() and
                        endpoint.filepath and endpoint.filepath.strip()
                    )
                elif endpoint.endpoint_type == 'OBJECT':
                    is_complete = (
                        endpoint.object_name and endpoint.object_name.strip() and
                        endpoint.filepath and endpoint.filepath.strip()
                    )
                
                row_endpoint = box.row(align=True)
                row_endpoint.prop(endpoint, "enabled", text="")
                
                # Show type icon and warning/checkmark
                if endpoint.endpoint_type == 'COLLECTION':
                    row_endpoint.label(text="", icon="OUTLINER_COLLECTION")
                else:
                    row_endpoint.label(text="", icon="OBJECT_DATA")
                
                if not is_complete:
                    row_endpoint.label(text="", icon="ERROR")
                else:
                    row_endpoint.label(text="", icon="CHECKMARK")
                
                row_endpoint.prop(endpoint, "name", text="")
                
                # Type selector
                row_type = box.row()
                row_type.label(text="Type:", icon="SETTINGS")
                row_type.prop(endpoint, "endpoint_type", expand=True)
                
                # Conditional selectors based on type
                if endpoint.endpoint_type == 'COLLECTION':
                    # Collection selector with searchable dropdown - use split for label visibility
                    row_collection = box.split(factor=0.25, align=True)
                    row_collection.label(text="Collection:", icon="OUTLINER_COLLECTION")
                    row_collection.prop_search(
                        endpoint,
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
                    row_subcol.prop(endpoint, "include_subcollections", text="Include Sub-collections")
                else:
                    # Object selector with searchable dropdown - use split for label visibility
                    row_object = box.split(factor=0.25, align=True)
                    row_object.label(text="Object:", icon="OBJECT_DATA")
                    row_object.prop_search(
                        endpoint,
                        "object_name",
                        bpy.data,
                        "objects",
                        text="",
                        icon="OBJECT_DATA"
                    )
                    # Increase width for long object names
                    row_object.scale_x = 2.0
                
                # Filepath selector - use split for label visibility
                row_filepath = box.split(factor=0.25, align=True)
                row_filepath.label(text="Filepath:", icon="FILEBROWSER")
                row_filepath.prop(endpoint, "filepath", text="")
                # Increase width for long filepaths
                row_filepath.scale_x = 2.0
                
                # Subfolder creation option
                row_subfolder = box.row(align=True)
                row_subfolder.prop(endpoint, "create_subfolder", text="Create Subfolder (USD_Endpoint)")
                
                # Origin metadata option
                row_metadata = box.row(align=True)
                row_metadata.prop(endpoint, "include_origin_metadata", text="Include Origin Metadata")
                
                # Subdivision export option
                row_subdivision = box.row(align=True)
                row_subdivision.prop(endpoint, "export_subdivision", text="Export Subdivision (Baked)")
                
                # Selection button - allows user to track which endpoint belongs to what
                row_select = box.row(align=True)
                select_op = row_select.operator(
                    "usdme.select_endpoint_target",
                    text="Select",
                    icon="RESTRICT_SELECT_OFF"
                )
                select_op.endpoint_index = idx
                
                # Show warning message if incomplete
                if not is_complete:
                    warning_row = box.row()
                    warning_row.alert = True
                    missing = []
                    if endpoint.endpoint_type == 'COLLECTION':
                        if not endpoint.collection_name or not endpoint.collection_name.strip():
                            missing.append("collection")
                    else:
                        if not endpoint.object_name or not endpoint.object_name.strip():
                            missing.append("object")
                    if not endpoint.filepath or not endpoint.filepath.strip():
                        missing.append("filepath")
                    warning_row.label(text=f"  ⚠ Missing: {', '.join(missing)}", icon="ERROR")
                
                box.separator()

        layout.separator()

        # Verbose logging toggle
        layout.prop(settings, "verbose_logging")

        col_export = layout.column(align=True)
        col_export.operator("usdme.export_endpoints", icon="EXPORT")

        # Bug report controls
        layout.separator()
        col_bug = layout.column(align=True)
        col_bug.operator("usdme.generate_bug_report", text="Generate Bug Report")


class USDME_OT_select_endpoint_target(bpy.types.Operator):
    """Select the collection or object associated with this endpoint in the viewport."""
    
    bl_idname = "usdme.select_endpoint_target"
    bl_label = "Select Endpoint Target"
    bl_options = {"REGISTER", "UNDO"}
    
    endpoint_index: bpy.props.IntProperty(
        name="Endpoint Index",
        description="Index of the endpoint to select",
        default=0
    )
    
    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        
        if self.endpoint_index < 0 or self.endpoint_index >= len(settings.endpoints):
            self.report({"ERROR"}, f"Invalid endpoint index: {self.endpoint_index}")
            return {"CANCELLED"}
        
        endpoint = settings.endpoints[self.endpoint_index]
        
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        if endpoint.endpoint_type == 'COLLECTION':
            # Select collection objects
            if endpoint.collection_name and endpoint.collection_name in bpy.data.collections:
                collection = bpy.data.collections[endpoint.collection_name]
                
                # Get all objects in collection (and sub-collections if enabled)
                objects_to_select = []
                if endpoint.include_subcollections:
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
                self.report({"WARNING"}, f"Collection '{endpoint.collection_name}' not found")
                return {"CANCELLED"}
        
        elif endpoint.endpoint_type == 'OBJECT':
            # Select single object
            if endpoint.object_name and endpoint.object_name in bpy.data.objects:
                obj = bpy.data.objects[endpoint.object_name]
                
                if obj.name in context.view_layer.objects:
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    self.report({"INFO"}, f"Selected object: {obj.name}")
                else:
                    self.report({"WARNING"}, f"Object '{obj.name}' is not in the current view layer")
                    return {"CANCELLED"}
            else:
                self.report({"WARNING"}, f"Object '{endpoint.object_name}' not found")
                return {"CANCELLED"}
        
        return {"FINISHED"}


class USDME_OT_add_endpoint(bpy.types.Operator):
    """Add a new USD Multi Export endpoint to the current scene.
    
    Automatically detects and uses:
    - Active collection (if available)
    - Or creates a collection from selected objects (if objects are selected)
    - Or creates an empty endpoint if nothing is selected
    """

    bl_idname = "usdme.add_endpoint"
    bl_label = "Add Endpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        endpoint = settings.endpoints.add()
        endpoint.name = f"Endpoint {len(settings.endpoints)}"
        
        # Auto-detect type and target based on context
        # Priority: Single object selected → Object type, Collection active → Collection type
        
        # Check if single object is selected (prefer Object type)
        if len(context.selected_objects) == 1:
            obj = context.selected_objects[0]
            endpoint.endpoint_type = 'OBJECT'
            endpoint.object_name = obj.name
            endpoint.name = obj.name  # Auto-name endpoint
            self.report({"INFO"}, f"Added endpoint with object: {obj.name}")
        # Check if collection is active
        elif hasattr(context, 'view_layer') and context.view_layer.active_layer_collection:
            collection = context.view_layer.active_layer_collection.collection
            endpoint.endpoint_type = 'COLLECTION'
            endpoint.collection_name = collection.name
            endpoint.name = collection.name  # Auto-name endpoint
            self.report({"INFO"}, f"Added endpoint with collection: {collection.name}")
        # Check if multiple objects selected (default to Collection type)
        elif context.selected_objects:
            # Get collection from first selected object
            obj = context.selected_objects[0]
            if obj.users_collection:
                # Prefer non-scene collection if available
                for coll in obj.users_collection:
                    if coll != context.scene.collection:
                        endpoint.endpoint_type = 'COLLECTION'
                        endpoint.collection_name = coll.name
                        endpoint.name = coll.name  # Auto-name endpoint
                        self.report({"INFO"}, f"Added endpoint with collection: {coll.name}")
                        break
                # Fallback to first collection
                if not endpoint.collection_name and obj.users_collection:
                    endpoint.endpoint_type = 'COLLECTION'
                    endpoint.collection_name = obj.users_collection[0].name
                    endpoint.name = obj.users_collection[0].name  # Auto-name endpoint
                    self.report({"INFO"}, f"Added endpoint with collection: {obj.users_collection[0].name}")
            else:
                # No collection found, default to Collection type, user must select
                endpoint.endpoint_type = 'COLLECTION'
                self.report({"INFO"}, "Added endpoint. Please select a collection or object.")
        else:
            # Nothing selected, default to Collection type
            endpoint.endpoint_type = 'COLLECTION'
            self.report({"INFO"}, "Added endpoint. Please select a collection or object.")
        
        return {"FINISHED"}


class USDME_OT_remove_endpoint(bpy.types.Operator):
    """Remove the last USD Multi Export endpoint from the current scene."""

    bl_idname = "usdme.remove_endpoint"
    bl_label = "Remove Endpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        if settings.endpoints:
            settings.endpoints.remove(len(settings.endpoints) - 1)
        else:
            self.report({"INFO"}, "No endpoints to remove.")
        return {"FINISHED"}


class USDME_OT_create_collection_from_selected(bpy.types.Operator):
    """Create a new collection from selected objects and optionally add it to an endpoint."""

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
    "USDME_OT_add_endpoint",
    "USDME_OT_create_collection_from_selected",
    "USDME_OT_generate_bug_report",
    "USDME_OT_remove_endpoint",
    "USDME_OT_select_endpoint_target",
]


