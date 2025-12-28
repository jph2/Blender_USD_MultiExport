bl_info = {
    "name": "USD Multi Export",
    "author": "Blender USD Multi Export Project",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "Scene Properties; 3D Viewport > N-Panel",
    "description": "Export multiple USD component assets from Blender scenes using endpoint definitions.",
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/jph2/Blender_USD_MultiExport",
    "tracker_url": "https://github.com/jph2/Blender_USD_MultiExport/issues",
}

import importlib
from typing import List, Type

import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.types import AddonPreferences

from . import logging_utils, ops_export, path_resolver, props, state_manager, ui


MODULES = (ops_export, props, ui)


class USDMultiExportPreferences(AddonPreferences):
    """Addon preferences for USD Multi Export."""

    bl_idname = __name__

    def update_log_level(self, context):
        """Update logger when preference changes."""
        from . import logging_utils
        logger = logging_utils.get_logger()
        logger.set_console_level(self.log_level)

    # Logging level preference
    log_level: EnumProperty(
        name="Console Log Level",
        description="Logging level for Blender console output",
        items=[
            ('DEBUG', "Debug", "Show all debug messages"),
            ('INFO', "Info", "Show info, warnings, and errors"),
            ('WARNING', "Warning", "Show warnings and errors only"),
            ('ERROR', "Error", "Show errors only"),
        ],
        default='INFO',
        update=update_log_level,  # Connect to logger
    )

    # Default export settings
    default_import_materials: BoolProperty(
        name="Default: Import Materials",
        description="Default value for importing materials when exporting USD files",
        default=True,
    )

    default_relative_path: BoolProperty(
        name="Default: Relative Paths",
        description="Default value for using relative paths in USD exports",
        default=False,
    )

    def draw(self, context):
        """Draw the preferences UI."""
        layout = self.layout

        # Logging section
        box = layout.box()
        box.label(text="Logging", icon='TEXT')
        box.prop(self, "log_level", text="Console Log Level")
        box.label(text="Higher levels reduce console noise but may hide debug info")

        # Export defaults section
        box = layout.box()
        box.label(text="Default Export Settings", icon='EXPORT')
        box.prop(self, "default_import_materials", text="Import Materials")
        box.prop(self, "default_relative_path", text="Use Relative Paths")
        box.label(text="These settings apply to new endpoints by default")


def _reload_modules() -> None:
    """Support live-reload during development inside Blender."""
    for module in MODULES:
        if module.__name__ in globals():
            importlib.reload(module)


classes: List[Type[bpy.types.PropertyGroup | bpy.types.Operator | bpy.types.Panel]] = (
    props.USDME_EndpointPropertyGroup,
    props.USDME_SceneProperties,
    ops_export.USDME_OT_export_endpoints,
    ui.USDME_OT_add_endpoint,
    ui.USDME_OT_generate_bug_report,
    ui.USDME_OT_remove_endpoint,
    ui.USDME_OT_select_endpoint_target,
    ui.USDME_PT_main_panel,
)


def register() -> None:
    """Register the addon and all its components."""
    from bpy.utils import register_class

    try:
        # Setup logging first (used by all modules)
        from . import logging_utils
        logger = logging_utils.setup_logging()
        logger.info("Starting USD Multi Export addon registration")

        # Register preferences first (needed by other components)
        register_class(USDMultiExportPreferences)

        # Apply user's log level preference from addon preferences
        # Note: This requires context, so we'll apply it after preferences are registered
        # The preference will be applied when user changes it in the UI
        # For initial load, we use the default from preferences
        try:
            prefs = bpy.context.preferences.addons[__name__].preferences
            if hasattr(prefs, 'log_level'):
                logger.set_console_level(prefs.log_level)
                logger.debug(f"Applied log level preference: {prefs.log_level}")
        except (AttributeError, KeyError):
            # Preferences not available yet (first load), use default
            logger.debug("Preferences not available yet, using default log level")

        # Register all classes
        for cls in classes:
            register_class(cls)

        # Register scene properties
        props.register_scene_properties()

        # Log successful registration
        logger.info("USD Multi Export addon registered successfully")
        logger.info("Access via: Scene Properties > USD Multi Export panel")

    except Exception as e:
        print(f"ERROR: Failed to register USD Multi Export addon: {e}")
        raise


def unregister() -> None:
    """Unregister the addon and all its components."""
    from bpy.utils import unregister_class

    try:
        # Import logging utilities
        from . import logging_utils
        logger = logging_utils.get_logger()
        logger.info("Starting USD Multi Export addon unregistration")

        # Unregister scene properties
        props.unregister_scene_properties()

        # Unregister all classes in reverse order
        for cls in reversed(classes):
            unregister_class(cls)

        # Unregister preferences last
        unregister_class(USDMultiExportPreferences)

        logger.info("USD Multi Export addon unregistered successfully")

    except Exception as e:
        print(f"ERROR: Failed to unregister USD Multi Export addon: {e}")
        raise


if __name__ == "__main__":
    _reload_modules()
    register()


