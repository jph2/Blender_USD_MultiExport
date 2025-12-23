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
        row.operator("usdme.add_endpoint", text="Add")
        row.operator("usdme.remove_endpoint", text="Remove")

        box = col.box()

        if not settings.endpoints:
            box.label(text="No endpoints defined for this scene.", icon="INFO")
        else:
            for idx, endpoint in enumerate(settings.endpoints):
                row_endpoint = box.row(align=True)
                row_endpoint.prop(endpoint, "enabled", text="")
                row_endpoint.prop(endpoint, "name", text="")
                row_endpoint.prop(endpoint, "collection_name", text="")

        layout.separator()

        # Verbose logging toggle
        layout.prop(settings, "verbose_logging")

        col_export = layout.column(align=True)
        col_export.operator("usdme.export_endpoints", icon="EXPORT")

        # Bug report controls
        layout.separator()
        col_bug = layout.column(align=True)
        col_bug.operator("usdme.generate_bug_report", text="Generate Bug Report")


class USDME_OT_add_endpoint(bpy.types.Operator):
    """Add a new USD Multi Export endpoint to the current scene."""

    bl_idname = "usdme.add_endpoint"
    bl_label = "Add Endpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings = context.scene.usdme_settings
        endpoint = settings.endpoints.add()
        endpoint.name = f"Endpoint {len(settings.endpoints)}"
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
    "USDME_OT_generate_bug_report",
    "USDME_OT_remove_endpoint",
]


