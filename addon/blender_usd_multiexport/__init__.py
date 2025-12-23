bl_info = {
    "name": "USD Multi Export",
    "author": "Blender USD Multi Export Project",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "Scene Properties; 3D Viewport > N-Panel",
    "description": "Export multiple USD component assets from Blender scenes using endpoint definitions.",
    "category": "Import-Export",
}

import importlib
from typing import List, Type

import bpy

from . import logging_utils, ops_export, path_resolver, props, state_manager, ui


MODULES = (ops_export, props, ui)


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
    ui.USDME_PT_main_panel,
)


def register() -> None:
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    props.register_scene_properties()


def unregister() -> None:
    from bpy.utils import unregister_class

    props.unregister_scene_properties()

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    _reload_modules()
    register()


