from __future__ import annotations

import json
import math
import re

import bpy
import mathutils
from bpy.types import Context, Operator

from . import logging_utils, path_resolver, state_manager, usd_bake


# ============================================================
# v0.1.13: Modifier Visibility Mode Handling
# ============================================================
# Modifier types and their target object properties
# Used to ensure target objects are visible before applying modifiers
MODIFIER_TARGET_PROPERTIES = {
    'SHRINKWRAP': ['target'],
    'LATTICE': ['object'],
    'MESH_DEFORM': ['object'],
    'SURFACE_DEFORM': ['target'],
    'CURVE': ['object'],
    'BOOLEAN': ['object'],
    'ARMATURE': ['object'],
    'HOOK': ['object'],
    'WARP': ['object_from', 'object_to'],
    'CAST': ['object'],
    'WAVE': ['start_position_object'],
    'DATA_TRANSFER': ['object'],
    'NORMAL_EDIT': ['target'],
}


def should_apply_modifier(mod, logger=None, start_point_context=None):
    """Check if modifier should be applied during export.
    
    v0.1.15: Skip modifiers that are intentionally disabled.
    A modifier is considered disabled if BOTH show_render AND show_viewport are False.
    If either is True, the modifier should be applied (user wants it visible somewhere).
    
    Args:
        mod: The modifier to check
        logger: Optional logger for logging skipped modifiers
        start_point_context: Optional context dict for logging
        
    Returns:
        bool: True if modifier should be applied, False if it should be skipped
    """
    # If both render and viewport are disabled, skip this modifier
    if not mod.show_render and not mod.show_viewport:
        if logger:
            try:
                mod_name_safe = mod.name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            except:
                mod_name_safe = f"<modifier_{mod.type}>"
            logger.log_step("modifier_skipped_disabled", {
                **(start_point_context or {}),
                "modifier_name": mod_name_safe,
                "modifier_type": mod.type,
                "show_render": mod.show_render,
                "show_viewport": mod.show_viewport,
                "reason": "Both show_render and show_viewport are False - modifier is intentionally disabled"
            })
        return False
    
    # Modifier should be applied (at least one visibility mode is enabled)
    return True


def ensure_modifier_visibility(mod, logger=None, start_point_context=None):
    """Force-enable modifier viewport visibility for proper depsgraph evaluation.
    
    v0.1.13: Fixes inconsistent modifier application caused by show_viewport=False.
    When a modifier has show_viewport disabled, the depsgraph doesn't evaluate it,
    causing bpy.ops.object.modifier_apply() to produce incorrect geometry.
    
    Args:
        mod: The modifier to check and enable
        logger: Optional logger for logging visibility overrides
        start_point_context: Optional context dict for logging
        
    Returns:
        bool: True if visibility was forced (was False), False if already enabled
    """
    if not mod.show_viewport:
        mod.show_viewport = True
        if logger:
            try:
                mod_name_safe = mod.name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            except:
                mod_name_safe = f"<modifier_{mod.type}>"
            logger.log_step("modifier_visibility_forced", {
                **(start_point_context or {}),
                "modifier_name": mod_name_safe,
                "modifier_type": mod.type,
                "action": "forced show_viewport=True for proper evaluation"
            })
        return True
    return False


def ensure_modifier_target_visibility(context, mod, visibility_backups, logger=None, start_point_context=None):
    """Temporarily unhide target objects for modifier evaluation.
    
    v0.1.13: Expands target handling from just SHRINKWRAP to ALL modifier types
    that have target objects. If a target is hidden, the modifier cannot
    evaluate correctly.
    
    Args:
        context: Blender context
        mod: The modifier to check for targets
        visibility_backups: Dict to store original visibility states for restoration
        logger: Optional logger for logging visibility overrides
        start_point_context: Optional context dict for logging
    """
    mod_type = mod.type
    if mod_type not in MODIFIER_TARGET_PROPERTIES:
        return
    
    target_props = MODIFIER_TARGET_PROPERTIES[mod_type]
    
    for prop_name in target_props:
        target_obj = getattr(mod, prop_name, None)
        if target_obj and target_obj.name in context.view_layer.objects:
            if target_obj.hide_viewport:
                # Store original visibility for restoration
                if target_obj.name not in visibility_backups:
                    visibility_backups[target_obj.name] = True
                target_obj.hide_viewport = False
                
                if logger:
                    try:
                        mod_name_safe = mod.name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                    except:
                        mod_name_safe = f"<modifier_{mod.type}>"
                    logger.log_step("modifier_target_visibility_forced", {
                        **(start_point_context or {}),
                        "modifier_name": mod_name_safe,
                        "modifier_type": mod.type,
                        "target_property": prop_name,
                        "target_object": target_obj.name,
                        "action": "temporarily unhidden for modifier evaluation"
                    })


def restore_target_visibility(context, visibility_backups):
    """Restore original visibility states for target objects.
    
    Args:
        context: Blender context
        visibility_backups: Dict of {object_name: was_hidden} to restore
    """
    for obj_name, was_hidden in visibility_backups.items():
        try:
            if obj_name in context.view_layer.objects:
                context.view_layer.objects[obj_name].hide_viewport = was_hidden
        except Exception:
            pass


def _collection_pivot_enabled(start_point) -> bool:
    source = getattr(start_point, "collection_pivot_source", "NONE") or "NONE"
    return source != "NONE"


def _get_collection_pivot_vector(start_point, context: Context):
    source = getattr(start_point, "collection_pivot_source", "NONE") or "NONE"
    if source == "WORLD":
        return mathutils.Vector((0.0, 0.0, 0.0))
    if source == "CUSTOM":
        return mathutils.Vector(getattr(start_point, "collection_pivot_xyz", (0.0, 0.0, 0.0)))
    if source == "CURSOR" and context and context.scene:
        return context.scene.cursor.location.copy()
    if source == "OBJECT":
        pivot_obj = getattr(start_point, "collection_pivot_object", None)
        if pivot_obj:
            return pivot_obj.matrix_world.to_translation()
    return None


def _apply_normalization_to_objects(
    context: Context,
    objects,
    normalize_position: bool,
    normalize_rotation: bool,
    normalize_scale: bool,
    pivot_vector,
    logger,
    start_point_context: dict,
):
    """DEPRECATED: This function applies normalization directly to objects, breaking normals.
    
    Use _create_fake_parent_for_collection() instead for collection export.
    This function is kept for backward compatibility but should not be used for collections.
    """
    if not objects:
        return

    for obj in objects:
        if not obj or obj.name not in context.view_layer.objects:
            continue
        obj_ref = context.view_layer.objects[obj.name]
        try:
            if pivot_vector is not None:
                obj_ref.location = obj_ref.location - pivot_vector

            if normalize_position or normalize_rotation or normalize_scale:
                bpy.ops.object.select_all(action="DESELECT")
                obj_ref.select_set(True)
                context.view_layer.objects.active = obj_ref
                if obj_ref.mode != "OBJECT":
                    try:
                        bpy.ops.object.mode_set(mode="OBJECT")
                    except Exception:
                        pass
                bpy.ops.object.transform_apply(
                    location=normalize_position,
                    rotation=normalize_rotation,
                    scale=normalize_scale,
                )
        except Exception as exc:
            if logger:
                logger.log_warning(
                    f"Normalization failed for object '{obj_ref.name}': {exc}",
                    context=start_point_context,
                )


def _create_fake_parent_for_collection(
    context: Context,
    start_point,
    collection_objects: list,
    logger,
    start_point_context: dict,
):
    """Create a fake parent Empty for collection export.
    
    The fake parent provides a transform hierarchy for collections (which are Scopes in USD).
    This avoids modifying geometry directly, preventing broken normals.
    
    Args:
        context: Blender context
        start_point: Start point with collection settings
        collection_objects: List of objects to parent to fake parent
        logger: Logger instance
        start_point_context: Context dict for logging
        
    Returns:
        tuple: (fake_parent_object, parent_backups_dict) or (None, {}) if no pivot/normalization needed
    """
    # v0.1.65: DISABLED - Fake parent machinery has persistent bugs causing scattered/rotated objects
    # Reverting to v0.1.39-style direct export which preserves position correctly.
    # The fake parent approach needs fundamental rethinking before re-enabling.
    # TODO: Re-implement using the expert's "direct matrix multiplication" approach
    #       instead of Blender parenting, which has complex matrix_parent_inverse behavior.
    logger.log_step("fake_parent_disabled", {
        **start_point_context,
        "reason": "v0.1.65 - fake parent machinery disabled due to persistent bugs",
        "note": "Reverting to v0.1.39-style direct export"
    })
    return None, {}
    
    # --- DISABLED CODE BELOW (v0.1.65) ---
    # Check if we need fake parent
    pivot_enabled = _collection_pivot_enabled(start_point)
    pivot_only = getattr(start_point, "collection_pivot_only", False)
    normalize_position = getattr(start_point, "normalize_position", False)
    normalize_scale = getattr(start_point, "normalize_scale", False)
    normalize_rotation = getattr(start_point, "normalize_rotation", False)
    
    needs_fake_parent = (
        pivot_enabled
        or pivot_only
        or normalize_position
        or normalize_scale
        or normalize_rotation
    )
    
    if not needs_fake_parent:
        return None, {}
    
    # Get pivot location
    pivot_vector = _get_collection_pivot_vector(start_point, context)
    if pivot_vector is None:
        pivot_vector = mathutils.Vector((0.0, 0.0, 0.0))
    
    # Create fake parent Empty
    fake_parent_name = "__USDME_FAKE_PARENT"
    # Ensure unique name
    counter = 0
    while fake_parent_name in bpy.data.objects:
        fake_parent_name = f"__USDME_FAKE_PARENT_{counter:03d}"
        counter += 1
    
    fake_parent = bpy.data.objects.new(fake_parent_name, None)
    fake_parent.empty_display_type = 'PLAIN_AXES'
    fake_parent.empty_display_size = 1.0
    
    # Position fake parent at pivot location
    fake_parent.location = pivot_vector
    
    # Link to active collection (or scene collection)
    if context.collection:
        context.collection.objects.link(fake_parent)
    else:
        context.scene.collection.objects.link(fake_parent)
    
    # Make fake parent visible but ensure it's not exported
    # Hide it from viewport to exclude from export selection
    fake_parent.hide_viewport = True
    
    logger.log_step("fake_parent_created", {
        **start_point_context,
        "fake_parent_name": fake_parent_name,
        "pivot_location": (pivot_vector.x, pivot_vector.y, pivot_vector.z),
        "pivot_source": getattr(start_point, "collection_pivot_source", "NONE"),
    })
    
    # Parent all collection objects to fake parent
    # Store original parent relationships for cleanup
    parent_backups = {}
    
    # v0.1.64 FIX: Ensure fake_parent's matrix_world is fully evaluated before parenting
    context.view_layer.update()
    
    for obj in collection_objects:
        if not obj or obj.name not in context.view_layer.objects:
            continue
        
        obj_ref = context.view_layer.objects[obj.name]
        
        # Store original parent state
        parent_backups[obj_ref.name] = {
            "parent": obj_ref.parent,
            "matrix_parent_inverse": obj_ref.matrix_parent_inverse.copy() if obj_ref.parent else mathutils.Matrix.Identity(4),
        }
        
        # v0.1.64 FIX: CRITICAL - Preserve visual position when parenting
        # The bug was: setting matrix_parent_inverse = fake_parent.matrix_world.inverted()
        # doesn't preserve the child's visual position - it loses the original position!
        # 
        # Correct approach: save world matrix, set parent, restore world matrix.
        # When we set matrix_world, Blender recomputes matrix_local to achieve
        # the desired world position given the current parent relationship.
        orig_world_matrix = obj_ref.matrix_world.copy()
        obj_ref.parent = fake_parent
        obj_ref.matrix_world = orig_world_matrix
    
    logger.log_step("objects_parented_to_fake_parent", {
        **start_point_context,
        "fake_parent_name": fake_parent_name,
        "objects_parented": len(parent_backups),
    })
    
    # Apply normalization to fake parent (affects all children)
    if normalize_position:
        # Reset fake parent location to origin (children move relative to it)
        fake_parent.location = (0.0, 0.0, 0.0)
    
    if normalize_scale:
        # Reset fake parent scale to unit (children scale relative to it)
        fake_parent.scale = (1.0, 1.0, 1.0)
    
    if normalize_rotation:
        # Reset fake parent rotation to zero (children rotate relative to it)
        fake_parent.rotation_euler = (0.0, 0.0, 0.0)
    
    # EXPERT CORRECTION (v0.1.63): Do NOT update matrix_parent_inverse after normalization
    # Updating matrix_parent_inverse after normalization CANCELS the normalization effect:
    # - When fake parent is normalized to identity, inverted() gives identity matrix
    # - Setting children's matrix_parent_inverse to identity removes the compensation offset
    # - Result: children behave as if no normalization happened (explains "no difference" bug)
    # Only update matrix_parent_inverse if goal is "keep children fixed while parent changes" (NOT our use case)
    
    # Force view layer update after normalization to ensure transforms are current
    context.view_layer.update()
    
    if normalize_position or normalize_scale or normalize_rotation:
        logger.log_step("fake_parent_normalized", {
            **start_point_context,
            "fake_parent_name": fake_parent_name,
            "normalize_position": normalize_position,
            "normalize_scale": normalize_scale,
            "normalize_rotation": normalize_rotation,
            "matrix_parent_inverse_update": "SKIPPED (expert correction - would cancel normalization)",
        })
    
    return fake_parent, parent_backups


def _bake_fake_parent_transform_to_children(
    context: Context,
    fake_parent,
    child_objects: list,
    logger,
    start_point_context: dict,
):
    """Bake fake parent's transform into child objects' world transforms.
    
    CRITICAL: Blender's USD exporter doesn't respect parent hierarchies when exporting
    with selected_objects_only=True. It exports each object's world matrix, not its
    local matrix relative to the parent. This function bakes the parent transform
    into each child's world transform so the export preserves the correct spatial
    relationships.
    
    EXPERT CORRECTION (v0.1.63): Use evaluated depsgraph matrices when reading matrix_world.
    context.view_layer.update() is often not enough - freshly created objects and post-op
    transforms can have matrix_world values that aren't fully evaluated until the depsgraph
    updates. This was causing incorrect matrices to be baked.
    
    Args:
        context: Blender context
        fake_parent: Fake parent Empty object
        child_objects: List of child objects to bake transforms for
        logger: Logger instance
        start_point_context: Context dict for logging
        
    Returns:
        dict: {obj_name: {"world_matrix": Matrix, "original_parent": Object, "original_matrix_parent_inverse": Matrix}}
    """
    if not fake_parent or not child_objects:
        return {}
    
    baked_transforms = {}
    baked_count = 0
    
    # EXPERT CORRECTION: Use evaluated depsgraph for accurate matrix values
    # context.view_layer.update() is often not enough for freshly modified transforms
    depsgraph = context.evaluated_depsgraph_get()
    depsgraph.update()
    
    for obj in child_objects:
        if not obj or obj.name not in context.view_layer.objects:
            continue
        
        obj_ref = context.view_layer.objects[obj.name]
        
        # Skip if not actually parented to fake parent
        if obj_ref.parent != fake_parent:
            continue
        
        try:
            # EXPERT CORRECTION: Get EVALUATED world matrix (includes parent transform)
            # Using evaluated_get() ensures matrix is fully computed after all transforms
            evaluated_obj = obj_ref.evaluated_get(depsgraph)
            world_matrix = evaluated_obj.matrix_world.copy()
            
            # Store original parent info
            original_parent = obj_ref.parent
            original_matrix_parent_inverse = obj_ref.matrix_parent_inverse.copy()
            
            # Clear parent
            obj_ref.parent = None
            
            # Apply world matrix directly to object
            # This preserves the exact transform including parent contribution
            obj_ref.matrix_world = world_matrix
            
            baked_transforms[obj_ref.name] = {
                "world_matrix": world_matrix,
                "original_parent": original_parent,
                "original_matrix_parent_inverse": original_matrix_parent_inverse,
            }
            baked_count += 1
            
        except Exception as e:
            if logger:
                logger.log_warning(
                    f"Failed to bake transform for '{obj_ref.name}': {e}",
                    context=start_point_context,
                )
    
    # Force depsgraph update after baking to ensure all changes are reflected
    depsgraph.update()
    context.view_layer.update()
    
    logger.log_step("fake_parent_transform_baked", {
        **start_point_context,
        "fake_parent_name": fake_parent.name,
        "baked_count": baked_count,
        "total_children": len(child_objects),
        "evaluated_depsgraph": True,  # Log that we used evaluated matrices
    })
    
    return baked_transforms


def _restore_baked_transforms(
    context: Context,
    baked_transforms: dict,
    fake_parent,
    logger,
    start_point_context: dict,
):
    """Restore original parent relationships after baking.
    
    Args:
        context: Blender context
        baked_transforms: Dict from _bake_fake_parent_transform_to_children
        fake_parent: Fake parent Empty object (may be None if already deleted)
        logger: Logger instance
        start_point_context: Context dict for logging
    """
    if not baked_transforms:
        return
    
    restored_count = 0
    fake_parent_name = fake_parent.name if fake_parent else "None"
    
    for obj_name, baked_data in baked_transforms.items():
        obj_ref = bpy.data.objects.get(obj_name)
        if not obj_ref or obj_name not in context.view_layer.objects:
            continue
        
        try:
            # Restore original parent
            obj_ref.parent = baked_data["original_parent"]
            obj_ref.matrix_parent_inverse = baked_data["original_matrix_parent_inverse"]
            restored_count += 1
        except Exception as e:
            if logger:
                logger.log_warning(
                    f"Failed to restore parent for '{obj_name}': {e}",
                    context=start_point_context,
                )
    
    logger.log_step("baked_transforms_restored", {
        **start_point_context,
        "fake_parent_name": fake_parent_name,
        "restored_count": restored_count,
    })
    
    # Force view layer update after restoration
    context.view_layer.update()


def _cleanup_fake_parent(
    context: Context,
    fake_parent,
    parent_backups: dict,
    logger,
    start_point_context: dict,
):
    """Clean up fake parent and restore original parent relationships.
    
    Args:
        context: Blender context
        fake_parent: Fake parent Empty object to delete
        parent_backups: Dict of original parent relationships {obj_name: {parent, matrix_parent_inverse}}
        logger: Logger instance
        start_point_context: Context dict for logging
    """
    if not fake_parent:
        return
    
    fake_parent_name = fake_parent.name
    
    # Restore original parent relationships
    restored_count = 0
    for obj_name, backup in parent_backups.items():
        obj_ref = bpy.data.objects.get(obj_name)
        if not obj_ref or obj_name not in context.view_layer.objects:
            continue
        
        try:
            obj_ref.parent = backup["parent"]
            obj_ref.matrix_parent_inverse = backup["matrix_parent_inverse"]
            restored_count += 1
        except Exception as e:
            if logger:
                logger.log_warning(
                    f"Failed to restore parent for '{obj_name}': {e}",
                    context=start_point_context,
                )
    
    logger.log_step("parent_relationships_restored", {
        **start_point_context,
        "fake_parent_name": fake_parent_name,
        "restored_count": restored_count,
    })
    
    # Delete fake parent
    try:
        if fake_parent_name in bpy.data.objects:
            bpy.data.objects.remove(fake_parent, do_unlink=True)
            logger.log_step("fake_parent_deleted", {
                **start_point_context,
                "fake_parent_name": fake_parent_name,
            })
    except Exception as e:
        if logger:
            # Use string name instead of object reference in error message
            logger.log_warning(
                f"Failed to delete fake parent '{fake_parent_name}': {e}",
                context=start_point_context,
            )
    
    # Force view layer update after cleanup
    context.view_layer.update()


class USDME_OT_export_start_points(Operator):
    """Export all enabled USD Multi Export start points.

    Start points are the stable DCC origins for downstream USD pipeline and composition arcs.
    Exports each enabled start point to a USD file, with support for:
    - Collection or Object type start points
    - Subfolder creation (USD_StartPoint/)
    - Origin metadata tracking
    - Safe scene isolation during export
    """

    bl_idname = "usdme.export_start_points"
    bl_label = "Export Start Points"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        scene = getattr(context, "scene", None)
        return bool(scene and hasattr(scene, "usdme_settings"))

    def execute(self, context: Context):
        scene = context.scene
        settings = scene.usdme_settings
        logger = logging_utils.get_logger()
        logger.set_verbose(settings.verbose_logging)

        # Start operation logging
        logger.start_operation(
            "batch_export",
            {
                "total_start_points": len(settings.start_points),
                "verbose_mode": settings.verbose_logging
            }
        )
        duplicate_counter = 0

        if not settings.start_points:
            logger.log_step("validation", {"result": "no_start_points"})
            self.report({"INFO"}, "No USD Multi Export start points defined on this scene.")
            logger.end_operation(success=False, result_info={"reason": "no_start_points"})
            return {"CANCELLED"}

        try:
            enabled_start_points = [ep for ep in settings.start_points if ep.enabled]
            logger.log_step("start_point_filtering", {
                "total_start_points": len(settings.start_points),
                "enabled_start_points": len(enabled_start_points)
            })
        except Exception as e:
            logger.log_error(
                "Failed to filter start points",
                exception=e,
                context={"total_start_points": len(settings.start_points) if settings.start_points else 0},
                recoverable=False
            )
            self.report({"ERROR"}, f"Failed to process start points: {str(e)}")
            logger.end_operation(success=False, result_info={"reason": "start_point_filtering_error", "error": str(e)})
            return {"CANCELLED"}

        if not enabled_start_points:
            logger.log_warning(
                "All USD Multi Export start points are disabled; nothing to export.",
                suggestion="Enable at least one start point in the USD Multi Export panel."
            )
            self.report({"WARNING"}, "All USD Multi Export start points are disabled; nothing to export.")
            logger.end_operation(success=False, result_info={"reason": "all_disabled"})
            return {"CANCELLED"}

        # Pre-flight validation: Check all enabled start points for completeness
        logger.log_step("preflight_validation_start", {
            "start_point_count": len(enabled_start_points)
        })
        
        try:
            invalid_start_points = []
            for start_point in enabled_start_points:
                issues = []
                
                # Type-specific validation
                if start_point.start_point_type == 'COLLECTION':
                    if not start_point.collection_name or not start_point.collection_name.strip():
                        issues.append("missing collection")
                    elif not bpy.data.collections.get(start_point.collection_name):
                        issues.append(f"collection '{start_point.collection_name}' not found")
                elif start_point.start_point_type == 'OBJECT':
                    if not start_point.object_name or not start_point.object_name.strip():
                        issues.append("missing object")
                    elif not bpy.data.objects.get(start_point.object_name):
                        issues.append(f"object '{start_point.object_name}' not found")
                
                # Filepath validation (common to both types)
                if not start_point.filepath or not start_point.filepath.strip():
                    issues.append("missing filepath")
                
                if issues:
                    invalid_start_points.append((start_point.name, issues))
        except Exception as e:
            logger.log_error(
                "Exception during pre-flight validation",
                exception=e,
                context={"start_point_count": len(enabled_start_points)},
                recoverable=False
            )
            self.report({"ERROR"}, f"Error during validation: {str(e)}")
            logger.end_operation(success=False, result_info={"reason": "preflight_validation_exception", "error": str(e)})
            return {"CANCELLED"}
        
        logger.log_step("preflight_validation_complete", {
            "valid_start_points": len(enabled_start_points) - len(invalid_start_points),
            "invalid_start_points": len(invalid_start_points)
        })
        
        if invalid_start_points:
            logger.log_step("preflight_validation_failed", {
                "invalid_start_points": [{"name": name, "issues": issues} for name, issues in invalid_start_points]
            })
            error_msg = "Some start points are incomplete:\n"
            for name, issues in invalid_start_points:
                error_msg += f"  • {name}: {', '.join(issues)}\n"
            error_msg += "\nPlease fix these issues before exporting."
            logger.log_error(
                "Pre-flight validation failed: incomplete start points detected",
                context={"invalid_start_points": invalid_start_points},
                recoverable=True
            )
            self.report({"ERROR"}, error_msg)
            logger.end_operation(success=False, result_info={"reason": "preflight_validation_failed"})
            return {"CANCELLED"}

        # Initialize state manager for safe batch operations
        state_mgr = state_manager.StateManager(context)
        logger.log_step("state_manager_init", {"backups_supported": True})

        exported_count = 0
        failed_count = 0

        try:
            with state_mgr.safe_batch_operation():
                logger.log_step("batch_operation_started", {
                    "start_point_count": len(enabled_start_points),
                    "state_backups": state_mgr.get_backup_count()
                })

                for i, start_point in enumerate(enabled_start_points, 1):
                    start_point_context = {
                        "start_point_index": i,
                        "start_point_name": start_point.name,
                        "start_point_type": start_point.start_point_type,
                        "collection_name": start_point.collection_name if start_point.start_point_type == 'COLLECTION' else None,
                        "object_name": start_point.object_name if start_point.start_point_type == 'OBJECT' else None,
                        "filepath": start_point.filepath
                    }

                    try:
                        logger.log_step("start_point_processing_start", start_point_context)

                        # Type-specific validation
                        if start_point.start_point_type == 'COLLECTION':
                            if not start_point.collection_name or not start_point.collection_name.strip():
                                logger.log_error(
                                    f"Start point '{start_point.name}' has no collection specified. Please select a collection.",
                                    context={
                                        **start_point_context,
                                        "available_collections": [c.name for c in bpy.data.collections]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Start point '{start_point.name}': No collection specified.")
                                failed_count += 1
                                continue
                        elif start_point.start_point_type == 'OBJECT':
                            if not start_point.object_name or not start_point.object_name.strip():
                                logger.log_error(
                                    f"Start point '{start_point.name}' has no object specified. Please select an object.",
                                    context={
                                        **start_point_context,
                                        "available_objects": [o.name for o in bpy.data.objects]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Start point '{start_point.name}': No object specified.")
                                failed_count += 1
                                continue

                        # Validate filepath is not empty
                        if not start_point.filepath or not start_point.filepath.strip():
                            logger.log_error(
                                f"Start point '{start_point.name}' has no filepath specified. Please set an export filepath.",
                                context={
                                    **start_point_context
                                },
                                recoverable=True
                            )
                            self.report({"WARNING"}, f"Start point '{start_point.name}': No filepath specified.")
                            failed_count += 1
                            continue

                        # Get the target based on type
                        target = None
                        if start_point.start_point_type == 'COLLECTION':
                            target = bpy.data.collections.get(start_point.collection_name)
                            if not target:
                                logger.log_error(
                                    f"Collection '{start_point.collection_name}' not found for start point '{start_point.name}'",
                                    context={
                                        **start_point_context,
                                        "available_collections": [c.name for c in bpy.data.collections]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Start point '{start_point.name}': Collection '{start_point.collection_name}' not found.")
                                failed_count += 1
                                continue
                            logger.log_step("collection_found", {
                                **start_point_context,
                                "collection_objects": len(target.objects)
                            })
                        elif start_point.start_point_type == 'OBJECT':
                            target = bpy.data.objects.get(start_point.object_name)
                            if not target:
                                logger.log_error(
                                    f"Object '{start_point.object_name}' not found for start point '{start_point.name}'",
                                    context={
                                        **start_point_context,
                                        "available_objects": [o.name for o in bpy.data.objects]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Start point '{start_point.name}': Object '{start_point.object_name}' not found.")
                                failed_count += 1
                                continue
                            logger.log_step("object_found", {
                                **start_point_context,
                                "object_type": target.type
                            })

                        # Resolve filepath using PathResolver
                        filepath = path_resolver.resolve_export_path(start_point.filepath)
                        if not filepath:
                            logger.log_error(
                                f"Failed to resolve filepath for start point '{start_point.name}': '{start_point.filepath}'",
                                context={
                                    **start_point_context,
                                    "original_filepath": start_point.filepath
                                },
                                recoverable=True
                            )
                            failed_count += 1
                            continue

                        logger.log_step("filepath_resolved", {
                            **start_point_context,
                            "resolved_filepath": filepath,
                            "relative_input": start_point.filepath,
                            "directory_created": True  # PathResolver creates directories automatically
                        })

                        # Create subfolder if enabled
                        if start_point.create_subfolder:
                            import os
                            from pathlib import Path
                            
                            # Get the target name (collection or object) for filename generation
                            target_name = start_point.collection_name if start_point.start_point_type == 'COLLECTION' else start_point.object_name
                            
                            # Get the parent directory of the resolved filepath
                            file_dir = Path(filepath).parent
                            
                            # Check if parent directory is already named "USD_StartPoint"
                            # If so, we don't need to create another subfolder
                            if file_dir.name == "USD_StartPoint":
                                # Already in USD_StartPoint folder, just ensure filename is correct
                                file_path_obj = Path(filepath)
                                if file_path_obj.is_dir() or not file_path_obj.name or file_path_obj.suffix == '':
                                    # Generate filename using target name
                                    if target_name:
                                        filename = f"{target_name}.usd"
                                    else:
                                        filename = f"{start_point.name}.usd"
                                    filepath = str(file_dir / filename)
                                
                                logger.log_step("subfolder_already_exists", {
                                    **start_point_context,
                                    "subfolder_path": str(file_dir),
                                    "updated_filepath": filepath
                                })
                            else:
                                # Create subfolder path: USD_StartPoint/ (just the name, no object/collection name)
                                subfolder_name = "USD_StartPoint"
                                subfolder_path = file_dir / subfolder_name
                                subfolder_path.mkdir(parents=True, exist_ok=True)
                                
                                # Update filepath to be inside subfolder
                                # If filepath is a directory or has no filename, generate one using target name
                                file_path_obj = Path(filepath)
                                if file_path_obj.is_dir() or not file_path_obj.name or file_path_obj.suffix == '':
                                    # Generate filename using target name
                                    if target_name:
                                        filename = f"{target_name}.usd"
                                    else:
                                        filename = f"{start_point.name}.usd"
                                else:
                                    filename = file_path_obj.name
                                
                                filepath = str(subfolder_path / filename)
                                
                                logger.log_step("subfolder_created", {
                                    **start_point_context,
                                    "subfolder_path": str(subfolder_path),
                                    "updated_filepath": filepath
                                })

                        # Track duplicated objects OUTSIDE ScopedIsolation so cleanup can happen after isolation exits
                        duplicated_objects_for_cleanup = []
                        # v0.1.14: Track mesh data name swaps for cleanup
                        mesh_swaps_for_cleanup = {}
                        # v0.1.17: Track name swaps for cleanup (OBJECT and COLLECTION types)
                        name_swaps_for_cleanup = {}
                        
                        # v0.1.17: Clean up any leftover objects from previous failed exports
                        # This prevents accumulation of __USDME_ORIG_* objects or _dup* duplicates
                        leftover_objects_cleaned = []
                        for obj_name in list(bpy.data.objects.keys()):
                            if obj_name.startswith("__USDME_ORIG_"):
                                obj = bpy.data.objects.get(obj_name)
                                if obj:
                                    # Try to restore the original name
                                    original_name = obj_name.replace("__USDME_ORIG_", "", 1)
                                    # Check if original name is already taken
                                    if original_name not in bpy.data.objects:
                                        try:
                                            obj.name = original_name
                                            leftover_objects_cleaned.append(f"{obj_name} -> {original_name}")
                                        except:
                                            pass
                        
                        # Also clean up any _dup* objects that might be left over
                        for obj_name in list(bpy.data.objects.keys()):
                            if "_dup" in obj_name and obj_name.endswith(("_dup1", "_dup2", "_dup3", "_dup4", "_dup5")):
                                obj = bpy.data.objects.get(obj_name)
                                if obj:
                                    try:
                                        bpy.data.objects.remove(obj)
                                        leftover_objects_cleaned.append(f"Deleted leftover duplicate: {obj_name}")
                                    except:
                                        pass
                        
                        if leftover_objects_cleaned:
                            logger.log_step("leftover_objects_cleaned", {
                                **start_point_context,
                                "cleaned_count": len(leftover_objects_cleaned),
                                "cleaned_objects": leftover_objects_cleaned
                            })
                        
                        # Use ScopedIsolation to safely isolate and export this start point
                        # Pass the target (Collection or Object) directly
                        with state_manager.ScopedIsolation(context, target, include_subcollections=start_point.include_subcollections if start_point.start_point_type == 'COLLECTION' else True) as isolation:
                            logger.log_step("isolation_started", start_point_context)

                            # USD export parameters - based on Blender 5.0 research
                            # Note: Second opinion analysis suggests verifying these parameter names
                            # against bpy.ops.wm.usd_export.get_rna_type().properties for Blender 5.0
                            
                            # Sanitize root_prim_path: USD prim paths must be valid identifiers
                            # Replace spaces and special characters with underscores
                            sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', start_point.name)
                            # Remove leading/trailing underscores and multiple consecutive underscores
                            sanitized_name = re.sub(r'_+', '_', sanitized_name).strip('_')
                            if not sanitized_name:
                                sanitized_name = "RootPrim"  # Fallback if name becomes empty
                            
                            export_params = {
                                "filepath": filepath,
                                "export_materials": True,
                                "export_uvmaps": True,
                                "export_normals": True,
                                "export_animation": False,
                                "export_lights": False,  # Exclude lights from export
                                "root_prim_path": f"/{sanitized_name}",
                            }
                            
                            # Apply subdivision modifiers before export (following NVIDIA best practices)
                            # USD exports actual geometry, not modifier stacks, so modifiers must be applied
                            # IMPORTANT: We duplicate objects first to avoid permanently modifying originals
                            # Reference: NVIDIA_BLender_BestPractise.md section 6.1
                            duplicated_objects = []  # Track duplicated objects for cleanup
                            mesh_objects = []  # Track all mesh objects for export (populated for collections)
                            # Track name swaps for rollback: {hidden_name: original_name}
                            name_swaps = {}  # Used for both OBJECT and COLLECTION types
                            # Track mesh data name swaps for cleanup (v0.1.14)
                            mesh_swaps = {}  # Used for both OBJECT and COLLECTION types

                            # Collection-specific logic (only for COLLECTION type)
                            # Object export path should NOT touch this logic
                            collection_needs_normalization = False
                            if start_point.start_point_type == 'COLLECTION':
                                pivot_only = getattr(start_point, "collection_pivot_only", False)
                                collection_needs_normalization = (
                                    getattr(start_point, "normalize_position", False)
                                    or getattr(start_point, "normalize_scale", False)
                                    or getattr(start_point, "normalize_rotation", False)
                                    or pivot_only
                                    or _collection_pivot_enabled(start_point)
                                )
                            
                            # #region agent log
                            try:
                                with open(r"e:\SynologyDrive\9999_LocalRepo\General_Dev\Master_Rules\.cursor\debug.log", "a", encoding="utf-8") as f:
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ops_export.py:353","message":"duplicated_objects initialized","data":{"start_point_name":start_point.name,"duplicated_objects_count":0},"timestamp":__import__("time").time()*1000})+"\n")
                            except: pass
                            # #endregion
                            
                            # Object export: only check export_modifiers (no collection logic)
                            # Collection export: check export_modifiers OR collection normalization
                            should_process_modifiers = (
                                start_point.export_modifiers 
                                or (start_point.start_point_type == 'COLLECTION' and collection_needs_normalization)
                            )
                            
                            if should_process_modifiers:
                                # v0.1.16: Unified modifier export - includes ALL modifiers (Subdivision, Shrinkwrap, Array, etc.)
                                # Following NVIDIA pattern: apply modifiers to bake geometry into mesh
                                # But we duplicate objects first to preserve originals (like CTRL+Z after export)
                                
                                if start_point.start_point_type == 'OBJECT':
                                    obj = bpy.data.objects.get(start_point.object_name)
                                    if obj and obj.type == 'MESH':
                                        # v0.1.30: REMOVED duplicate detection logic that was switching to "base" objects
                                        # The user explicitly selected THIS object to export, so we export it with its modifiers
                                        # Previous bug: Objects like "Kayak.002" would switch to "Kayak" which might not have modifiers
                                        obj_name = obj.name
                                        
                                        # v0.1.30: Log modifier check for debugging
                                        modifier_names = [mod.name for mod in obj.modifiers]
                                        logger.log_step("object_modifier_check", {
                                            **start_point_context,
                                            "object_name": obj_name,
                                            "modifier_count": len(modifier_names),
                                            "modifiers": modifier_names,
                                            "export_modifiers_enabled": start_point.export_modifiers
                                        })
                                        
                                        # Check if we need to duplicate for modifiers
                                        # v0.1.29: Unified check - same as COLLECTION type
                                        # Process ANY modifiers, not just those with show_render/show_viewport
                                        # The should_apply_modifier() function will handle visibility filtering later
                                        needs_duplication = False
                                        reason = []
                                        
                                        # Object export: ONLY check for modifiers (no collection/normalization logic)
                                        # This matches v0.1.48 behavior exactly
                                        if start_point.export_modifiers:
                                            if any(mod for mod in obj.modifiers):
                                                needs_duplication = True
                                                reason.append("modifiers")
                                        
                                        if needs_duplication:
                                            # === NAME-SWAP STRATEGY (v0.1.17) ===
                                            # Same as COLLECTION type: rename original first, then duplicate gets original name
                                            # This ensures duplicates always have original names, not _dup1 suffixes
                                            # 1. Rename original to hidden name
                                            # 2. Duplicate (gets original name since it's now free)
                                            # 3. Apply modifiers to duplicate
                                            # 4. Export duplicate (with original name!)
                                            # 5. Delete duplicate, rename original back
                                            
                                            original_name = obj.name
                                            hidden_name = f"__USDME_ORIG_{original_name}"
                                            
                                            # Step 1: Rename original to hidden name
                                            try:
                                                obj.name = hidden_name
                                                name_swaps[hidden_name] = original_name
                                            except Exception as e:
                                                logger.log_warning(
                                                    f"Failed to rename '{original_name}' to '{hidden_name}': {e}",
                                                    context=start_point_context
                                                )
                                                continue
                                            
                                            # Step 2: Duplicate (should get original_name since it's now free)
                                            try:
                                                # v0.1.14: Get original mesh data name BEFORE duplication
                                                original_mesh_name = None
                                                original_mesh = None
                                                if obj.data and hasattr(obj.data, 'name'):
                                                    original_mesh = obj.data
                                                    original_mesh_name = obj.data.name
                                                
                                                bpy.ops.object.select_all(action='DESELECT')
                                                obj.select_set(True)
                                                context.view_layer.objects.active = obj
                                                bpy.ops.object.duplicate(linked=False)
                                                dup_obj = context.view_layer.objects.active
                                                
                                                # Force the duplicate to have the original name
                                                # (Blender might have given it .001 if there was a race condition)
                                                if dup_obj.name != original_name:
                                                    dup_obj.name = original_name
                                                
                                                # v0.1.14: MESH DATA NAME-SWAP STRATEGY
                                                # The duplicate's mesh data also needs the original name for USD consistency
                                                if original_mesh_name and dup_obj.data and dup_obj.data != original_mesh:
                                                    dup_mesh = dup_obj.data
                                                    dup_mesh_name = dup_mesh.name  # e.g., "Plane.011"
                                                    
                                                    # Rename original mesh data to hidden name
                                                    hidden_mesh_name = f"__USDME_MESH_{original_mesh_name}"
                                                    original_mesh.name = hidden_mesh_name
                                                    
                                                    # Rename duplicate mesh data to original name
                                                    dup_mesh.name = original_mesh_name
                                                    
                                                    # Track for cleanup
                                                    mesh_swaps[hidden_mesh_name] = {
                                                        'original_name': original_mesh_name,
                                                        'original_mesh': original_mesh,
                                                        'dup_mesh': dup_mesh
                                                    }
                                                    
                                                    logger.log_step("mesh_data_name_swapped", {
                                                        **start_point_context,
                                                        "object_name": original_name,
                                                        "original_mesh_name": original_mesh_name,
                                                        "hidden_mesh_name": hidden_mesh_name,
                                                        "dup_mesh_old_name": dup_mesh_name,
                                                        "dup_mesh_new_name": dup_mesh.name
                                                    })
                                                
                                                # Ensure duplicate is visible and selected for export
                                                dup_obj.hide_viewport = False
                                                dup_obj.select_set(True)
                                                
                                                # Link duplicate to same collection(s) as original
                                                for collection in obj.users_collection:
                                                    if dup_obj.name not in collection.objects:
                                                        collection.objects.link(dup_obj)
                                                
                                                duplicated_objects.append({
                                                    "original": obj,
                                                    "duplicate": dup_obj,
                                                    "type": "object",
                                                    "reason": ", ".join(reason),
                                                    "original_name": original_name,
                                                    "hidden_name": hidden_name
                                                })
                                            except Exception as e:
                                                # Rollback: restore original name if duplication failed
                                                try:
                                                    obj.name = original_name
                                                    if hidden_name in name_swaps:
                                                        del name_swaps[hidden_name]
                                                except:
                                                    pass
                                                logger.log_warning(
                                                    f"Failed to duplicate object '{original_name}': {e}",
                                                    context=start_point_context
                                                )
                                                continue
                                            
                                            # #region agent log
                                            try:
                                                with open(r"e:\SynologyDrive\9999_LocalRepo\General_Dev\Master_Rules\.cursor\debug.log", "a", encoding="utf-8") as f:
                                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"ops_export.py:381","message":"duplicate created for OBJECT","data":{"start_point_name":start_point.name,"original_name":obj.name,"duplicate_name":dup_obj.name,"duplicated_objects_count":len(duplicated_objects),"reason":", ".join(reason)},"timestamp":__import__("time").time()*1000})+"\n")
                                            except: pass
                                            # #endregion
                                            
                                            if start_point.export_modifiers:
                                                # Remove shape keys from duplicate first (NVIDIA pattern)
                                                if dup_obj.data.shape_keys:
                                                    try:
                                                        dup_obj.select_set(True)
                                                        context.view_layer.objects.active = dup_obj
                                                        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                                                        logger.log_step("shape_keys_removed", {
                                                            **start_point_context,
                                                            "object_name": dup_obj.name,
                                                            "original_object": obj.name,
                                                            "is_duplicate": True
                                                        })
                                                    except Exception as e:
                                                        logger.log_warning(
                                                            f"Failed to remove shape keys from duplicate '{dup_obj.name}': {str(e)}",
                                                            context=start_point_context
                                                        )
                                                
                                                # v0.1.18: Apply modifiers in STACK ORDER (top to bottom)
                                                # CRITICAL: Modifiers must be applied in the order they appear in the stack,
                                                # not by type. Stack order determines the final geometry result.
                                                # v0.1.13: Track target visibility for restoration
                                                target_visibility_backups = {}
                                                modifiers_applied = []
                                                
                                                # Apply modifiers in stack order (top to bottom)
                                                # dup_obj.modifiers iterates in stack order from top to bottom
                                                for mod in list(dup_obj.modifiers):
                                                    # v0.1.15: Skip intentionally disabled modifiers
                                                    if not should_apply_modifier(mod, logger, start_point_context):
                                                        continue
                                                    
                                                    try:
                                                        # Safely get modifier name
                                                        try:
                                                            mod_name_safe = mod.name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                                                        except:
                                                            mod_name_safe = f"<modifier_{mod.type}>"
                                                        
                                                        # v0.1.13: Force-enable modifier viewport visibility
                                                        ensure_modifier_visibility(mod, logger, start_point_context)
                                                        
                                                        # v0.1.13: Ensure target objects are visible for ALL modifier types with targets
                                                        ensure_modifier_target_visibility(context, mod, target_visibility_backups, logger, start_point_context)
                                                        
                                                        # Force depsgraph update after visibility changes
                                                        context.view_layer.update()
                                                        
                                                        dup_obj.select_set(True)
                                                        context.view_layer.objects.active = dup_obj
                                                        bpy.ops.object.modifier_apply(modifier=mod.name, single_user=True)
                                                        
                                                        modifiers_applied.append({
                                                            "object": dup_obj.name,
                                                            "original_object": obj.name,
                                                            "modifier": mod_name_safe,
                                                            "modifier_type": mod.type,
                                                            "is_duplicate": True
                                                        })
                                                        
                                                        logger.log_step("modifier_applied", {
                                                            **start_point_context,
                                                            "object_name": dup_obj.name,
                                                            "original_object_name": obj.name,
                                                            "modifier_name": mod_name_safe,
                                                            "modifier_type": mod.type
                                                        })
                                                    except Exception as e:
                                                        # Safely get modifier name for error message
                                                        try:
                                                            mod_name_safe = mod.name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                                                        except:
                                                            mod_name_safe = f"<modifier_{mod.type}>"
                                                        
                                                        logger.log_warning(
                                                            f"Failed to apply modifier '{mod_name_safe}' ({mod.type}) on duplicate '{dup_obj.name}': {str(e)}",
                                                            context=start_point_context
                                                        )
                                                
                                                # v0.1.13: Restore target visibility after all modifiers applied
                                                restore_target_visibility(context, target_visibility_backups)
                                                
                                                if modifiers_applied:
                                                    logger.log_step("modifiers_applied", {
                                                        **start_point_context,
                                                        "modifiers_applied": len(modifiers_applied),
                                                        "modifiers": modifiers_applied,
                                                        "duplicates_created": len(duplicated_objects)
                                                    })
                                                else:
                                                    # Log if export_modifiers is enabled but no modifiers found/applied
                                                    logger.log_warning(
                                                        "Export modifiers enabled but no modifiers found or applied on target object",
                                                        context=start_point_context
                                                    )
                                        
                                elif start_point.start_point_type == 'COLLECTION':
                                    collection = bpy.data.collections.get(start_point.collection_name)
                                    if collection:
                                        # ============================================================
                                        # CLEAN REWRITE v0.1.11: Deterministic object processing
                                        # ============================================================
                                        # Design principles:
                                        # 1. Process ALL mesh objects in collection - no skipping
                                        # 2. Use name-swap strategy for clean USD prim names
                                        # 3. Track everything by object reference, not by name
                                        # 4. Robust cleanup with rollback on errors
                                        # ============================================================
                                        
                                        def get_safe_collection_objects(coll, include_children=True):
                                            """Safely get objects from a collection recursively."""
                                            objects = []
                                            try:
                                                for obj in coll.objects:
                                                    try:
                                                        if obj.name in bpy.data.objects:
                                                            objects.append(obj)
                                                    except (ReferenceError, AttributeError, RuntimeError):
                                                        continue
                                            except Exception:
                                                pass
                                            
                                            if include_children:
                                                try:
                                                    for child_coll in coll.children:
                                                        try:
                                                            objects.extend(get_safe_collection_objects(child_coll, include_children))
                                                        except Exception:
                                                            continue
                                                except Exception:
                                                    pass
                                            return objects
                                        
                                        # Get all objects from collection
                                        include_subs = start_point.include_subcollections if hasattr(start_point, 'include_subcollections') else True
                                        objects_to_process = get_safe_collection_objects(collection, include_children=include_subs)
                                        
                                        logger.log_step("collection_objects_gathered", {
                                            **start_point_context,
                                            "total_objects": len(objects_to_process),
                                            "object_names": [o.name for o in objects_to_process if o]
                                        })
                                        
                                        # Filter to MESH objects only
                                        mesh_objects = []
                                        for obj in objects_to_process:
                                            try:
                                                if obj and obj.name in bpy.data.objects and obj.type == 'MESH':
                                                    mesh_objects.append(obj)
                                            except (ReferenceError, AttributeError, RuntimeError):
                                                continue
                                        
                                        logger.log_step("mesh_objects_filtered", {
                                            **start_point_context,
                                            "mesh_count": len(mesh_objects),
                                            "mesh_names": [o.name for o in mesh_objects]
                                        })
                                        
                                        # Track name swaps for rollback: {hidden_name: original_name}
                                        name_swaps = {}
                                        # v0.1.14: Track mesh data name swaps for cleanup
                                        mesh_swaps = {}
                                        
                                        # Process each mesh object
                                        for obj in mesh_objects:
                                            try:
                                                if not obj or obj.name not in bpy.data.objects:
                                                    continue
                                                
                                                original_name = obj.name
                                                
                                                # Check if this object needs modifier baking
                                                needs_duplication = False
                                                reason = []
                                                
                                                # v0.1.16: Unified modifier check - includes ALL modifiers (including subdivision)
                                                # Collection normalization is now handled via fake parent, so we only duplicate for modifiers
                                                if start_point.export_modifiers:
                                                    try:
                                                        if any(mod for mod in obj.modifiers):
                                                            needs_duplication = True
                                                            reason.append("modifiers")
                                                    except (ReferenceError, AttributeError, RuntimeError):
                                                        continue
                                                
                                                if needs_duplication:
                                                    # === NAME-SWAP STRATEGY ===
                                                    # 1. Rename original to hidden name
                                                    # 2. Duplicate (gets original name since it's now free)
                                                    # 3. Apply modifiers to duplicate
                                                    # 4. Export duplicate (with original name!)
                                                    # 5. Delete duplicate, rename original back
                                                    
                                                    hidden_name = f"__USDME_ORIG_{original_name}"
                                                    
                                                    # Step 1: Rename original to hidden name
                                                    try:
                                                        obj.name = hidden_name
                                                        name_swaps[hidden_name] = original_name
                                                    except Exception as e:
                                                        logger.log_warning(
                                                            f"Failed to rename '{original_name}' to '{hidden_name}': {e}",
                                                            context=start_point_context
                                                        )
                                                        continue
                                                    
                                                    # Step 2: Duplicate (should get original_name since it's now free)
                                                    try:
                                                        # v0.1.14: Get original mesh data name BEFORE duplication
                                                        original_mesh_name = None
                                                        original_mesh = None
                                                        if obj.data and hasattr(obj.data, 'name'):
                                                            original_mesh = obj.data
                                                            original_mesh_name = obj.data.name
                                                        
                                                        bpy.ops.object.select_all(action='DESELECT')
                                                        obj.select_set(True)
                                                        context.view_layer.objects.active = obj
                                                        bpy.ops.object.duplicate(linked=False)
                                                        dup_obj = context.view_layer.objects.active
                                                        
                                                        # Force the duplicate to have the original name
                                                        # (Blender might have given it .001 if there was a race condition)
                                                        if dup_obj.name != original_name:
                                                            dup_obj.name = original_name
                                                        
                                                        # v0.1.14: MESH DATA NAME-SWAP STRATEGY
                                                        # The duplicate's mesh data also needs the original name for USD consistency
                                                        if original_mesh_name and dup_obj.data and dup_obj.data != original_mesh:
                                                            dup_mesh = dup_obj.data
                                                            dup_mesh_name = dup_mesh.name  # e.g., "Plane.011"
                                                            
                                                            # Rename original mesh data to hidden name
                                                            hidden_mesh_name = f"__USDME_MESH_{original_mesh_name}"
                                                            original_mesh.name = hidden_mesh_name
                                                            
                                                            # Rename duplicate mesh data to original name
                                                            dup_mesh.name = original_mesh_name
                                                            
                                                            # Track for cleanup (mesh_swaps is initialized at higher scope)
                                                            mesh_swaps[hidden_mesh_name] = {
                                                                'original_name': original_mesh_name,
                                                                'original_mesh': original_mesh,
                                                                'dup_mesh': dup_mesh
                                                            }
                                                            
                                                            logger.log_step("mesh_data_name_swapped", {
                                                                **start_point_context,
                                                                "object_name": original_name,
                                                                "original_mesh_name": original_mesh_name,
                                                                "hidden_mesh_name": hidden_mesh_name,
                                                                "dup_mesh_old_name": dup_mesh_name,
                                                                "dup_mesh_new_name": dup_mesh.name
                                                            })
                                                        
                                                        # Ensure duplicate is visible
                                                        dup_obj.hide_viewport = False
                                                        dup_obj.select_set(True)
                                                        
                                                        # Link duplicate to same collections as original
                                                        try:
                                                            for coll in obj.users_collection:
                                                                if dup_obj.name not in coll.objects:
                                                                    coll.objects.link(dup_obj)
                                                        except Exception:
                                                            pass
                                                        
                                                        duplicated_objects.append({
                                                            "original": obj,
                                                            "duplicate": dup_obj,
                                                            "original_name": original_name,
                                                            "hidden_name": hidden_name,
                                                            "original_mesh_name": original_mesh_name,
                                                            "type": "collection",
                                                            "reason": ", ".join(reason)
                                                        })
                                                        
                                                        logger.log_step("object_duplicated_with_name_swap", {
                                                            **start_point_context,
                                                            "original_name": original_name,
                                                            "hidden_name": hidden_name,
                                                            "duplicate_name": dup_obj.name,
                                                            "mesh_name": dup_obj.data.name if dup_obj.data else None,
                                                            "reason": ", ".join(reason)
                                                        })
                                                        
                                                    except Exception as e:
                                                        # Rollback: restore original name
                                                        try:
                                                            obj.name = original_name
                                                            if hidden_name in name_swaps:
                                                                del name_swaps[hidden_name]
                                                        except Exception:
                                                            pass
                                                        logger.log_warning(
                                                            f"Failed to duplicate '{original_name}': {e}",
                                                            context=start_point_context
                                                        )
                                                        continue
                                                    
                                                    if start_point.export_modifiers:
                                                        # Step 3: Remove shape keys from duplicate
                                                        if dup_obj.data.shape_keys:
                                                            try:
                                                                dup_obj.select_set(True)
                                                                context.view_layer.objects.active = dup_obj
                                                                bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                                                            except Exception as e:
                                                                logger.log_warning(
                                                                    f"Failed to remove shape keys from '{dup_obj.name}': {e}",
                                                                    context=start_point_context
                                                                )
                                                        
                                                        # Step 4: Apply modifiers (v0.1.18: In STACK ORDER - top to bottom)
                                                        # CRITICAL: Modifiers must be applied in the order they appear in the stack,
                                                        # not by type. Stack order determines the final geometry result.
                                                        # v0.1.13: Track target visibility for restoration
                                                        coll_target_visibility_backups = {}
                                                        modifiers_applied = []
                                                        
                                                        # Apply modifiers in stack order (top to bottom)
                                                        # dup_obj.modifiers iterates in stack order from top to bottom
                                                        for mod in list(dup_obj.modifiers):
                                                            # v0.1.15: Skip intentionally disabled modifiers
                                                            if not should_apply_modifier(mod, logger, start_point_context):
                                                                continue
                                                            
                                                            try:
                                                                mod_name = mod.name
                                                                mod_type = mod.type
                                                                
                                                                # v0.1.13: Force-enable modifier viewport visibility
                                                                ensure_modifier_visibility(mod, logger, start_point_context)
                                                                
                                                                # v0.1.13: Ensure target objects are visible for ALL modifier types
                                                                ensure_modifier_target_visibility(context, mod, coll_target_visibility_backups, logger, start_point_context)
                                                                
                                                                # Force depsgraph update after visibility changes
                                                                context.view_layer.update()
                                                                
                                                                dup_obj.select_set(True)
                                                                context.view_layer.objects.active = dup_obj
                                                                bpy.ops.object.modifier_apply(modifier=mod_name, single_user=True)
                                                                
                                                                modifiers_applied.append({
                                                                    "object": dup_obj.name,
                                                                    "original_object": original_name,
                                                                    "modifier": mod_name,
                                                                    "modifier_type": mod_type,
                                                                    "is_duplicate": True
                                                                })
                                                                
                                                                logger.log_step("modifier_applied", {
                                                                    **start_point_context,
                                                                    "object_name": dup_obj.name,
                                                                    "original_object_name": original_name,
                                                                    "modifier_name": mod_name,
                                                                    "modifier_type": mod_type
                                                                })
                                                            except Exception as e:
                                                                logger.log_warning(
                                                                    f"Failed to apply modifier '{mod.name}' ({mod.type}) on '{dup_obj.name}': {e}",
                                                                    context=start_point_context
                                                                )
                                                        
                                                        # v0.1.13: Restore target visibility after all modifiers applied
                                                        restore_target_visibility(context, coll_target_visibility_backups)
                                                
                                            except (ReferenceError, AttributeError, RuntimeError) as e:
                                                logger.log_warning(
                                                    f"Object became invalid during processing: {e}",
                                                    context=start_point_context
                                                )
                                                continue
                                        
                                        logger.log_step("duplication_phase_complete", {
                                            **start_point_context,
                                            "duplicates_created": len(duplicated_objects),
                                            "name_swaps": len(name_swaps)
                                        })
                            
                            # ============================================================
                            # EXPORT SELECTION: Build list of ALL objects to export
                            # - Duplicates (for objects that needed modifier baking)
                            # - Originals (for objects that DIDN'T need modifier baking)
                            # ============================================================
                            
                            # Capture visibility state before we start modifying
                            visibility_snapshot = {
                                obj.name: obj.hide_viewport
                                for obj in context.view_layer.objects
                            }
                            
                            # Build set of original objects that were duplicated (now hidden as __USDME_ORIG_*)
                            duplicated_original_names = set()
                            for dup_info in duplicated_objects:
                                original_name = dup_info.get("original_name")
                                if original_name:
                                    duplicated_original_names.add(original_name)
                            
                            # Build list of objects to export:
                            # 1. All duplicates (with applied modifiers, using original names)
                            # 2. All mesh objects from collection that WEREN'T duplicated
                            # 3. For OBJECT type: original object if it wasn't duplicated
                            objects_to_export = []
                            
                            # Add duplicates
                            for dup_info in duplicated_objects:
                                dup_obj = dup_info.get("duplicate")
                                if dup_obj and dup_obj.name in context.view_layer.objects:
                                    objects_to_export.append(context.view_layer.objects[dup_obj.name])
                            
                            # Add original objects that weren't duplicated (no modifier baking needed)
                            # For COLLECTION type: These are mesh objects from the collection
                            for obj in mesh_objects:
                                try:
                                    if obj and obj.name in bpy.data.objects:
                                        # Skip if this object was duplicated (it's now named __USDME_ORIG_*)
                                        if obj.name in duplicated_original_names:
                                            continue
                                        # Skip if it's a hidden original (starts with __USDME_ORIG_)
                                        if obj.name.startswith("__USDME_ORIG_"):
                                            continue
                                        # This object wasn't duplicated, include it directly
                                        if obj.name in context.view_layer.objects:
                                            objects_to_export.append(context.view_layer.objects[obj.name])
                                except (ReferenceError, AttributeError, RuntimeError):
                                    continue
                            
                            # v0.1.16: For OBJECT type, ensure the object is always in objects_to_export
                            # FIXED: Always check for OBJECT type and ensure object is added
                            if start_point.start_point_type == 'OBJECT':
                                target_obj_name = start_point.object_name
                                obj_already_added = False
                                
                                # Check if object (or its duplicate) is already in the list
                                for exp_obj in objects_to_export:
                                    # Check if this is the target object or a duplicate of it
                                    if (exp_obj.name == target_obj_name or 
                                        exp_obj.name == f"__USDME_ORIG_{target_obj_name}" or
                                        target_obj_name in exp_obj.name):
                                        obj_already_added = True
                                        break
                                
                                # If not already added, add the object
                                if not obj_already_added:
                                    obj = bpy.data.objects.get(target_obj_name)
                                    if obj and obj.type == 'MESH' and obj.name in context.view_layer.objects:
                                        # Only add if it's not hidden as __USDME_ORIG_*
                                        if not obj.name.startswith("__USDME_ORIG_"):
                                            objects_to_export.append(context.view_layer.objects[obj.name])
                                    else:
                                        # Object might be hidden, try to find it
                                        logger.log_warning(
                                            f"OBJECT type start point: Could not find object '{target_obj_name}' in view layer",
                                            context=start_point_context
                                        )
                            
                            # CRITICAL: Capture object names as strings NOW, before any transforms or visibility changes
                            # Object references can become stale after view_layer.update() or visibility changes
                            object_names_to_export = [o.name for o in objects_to_export if o and hasattr(o, 'name')]
                            
                            logger.log_step("export_objects_prepared", {
                                **start_point_context,
                                "total_objects_to_export": len(objects_to_export),
                                "duplicates_count": len(duplicated_objects),
                                "originals_without_modifiers": len(objects_to_export) - len(duplicated_objects),
                                "object_names": object_names_to_export
                            })

                            # Collection export: Use fake parent approach (avoids modifying geometry directly)
                            fake_parent = None
                            fake_parent_backups = {}
                            baked_transforms = {}  # Store baked transforms for restoration
                            if start_point.start_point_type == 'COLLECTION':
                                # Create fake parent and parent collection objects to it
                                # This provides transform hierarchy without modifying geometry (prevents broken normals)
                                fake_parent, fake_parent_backups = _create_fake_parent_for_collection(
                                    context=context,
                                    start_point=start_point,
                                    collection_objects=objects_to_export,
                                    logger=logger,
                                    start_point_context=start_point_context,
                                )
                                
                                # CRITICAL: Bake fake parent transform into child objects' world transforms
                                # Blender's USD exporter doesn't respect parent hierarchies when exporting
                                # with selected_objects_only=True. It exports each object's world matrix.
                                # By baking the parent transform into each child's world transform, we ensure
                                # the export preserves the correct spatial relationships.
                                if fake_parent:
                                    baked_transforms = _bake_fake_parent_transform_to_children(
                                        context=context,
                                        fake_parent=fake_parent,
                                        child_objects=objects_to_export,
                                        logger=logger,
                                        start_point_context=start_point_context,
                                    )

                            # Object export: NO normalization logic (matches v0.1.48 behavior)
                            # Collection normalization is handled above for COLLECTION type only
                            
                            # Apply Y-up rotation BEFORE selection (if enabled)
                            # This ensures transforms are applied before we select objects for export
                            # 
                            # NOTE v0.1.28: DISABLED location scaling for unit conversion
                            # Blender's obj.location is ALWAYS stored in meters internally,
                            # regardless of scene unit display settings. Scaling locations
                            # breaks exports because Blender's USD exporter already handles
                            # unit conversion correctly. Only Y-up rotation is applied.
                            #
                            # CRITICAL v0.1.61: Skip Y-up transform for collection exports with fake parent
                            # The fake parent transform baking already includes all necessary transforms.
                            # Applying Y-up rotation here would overwrite the baked fake parent transforms.
                            # Y-up conversion will be handled in the post-export USD bake step.
                            transform_backups = {}  # {obj_name: {"location": Vector, "rotation_euler": Euler, "scale": Vector}}
                            
                            # v0.1.28: Disabled - scale_factor should NOT be applied to locations
                            # scale_factor = start_point.get_scale_factor()
                            scale_factor = 1.0  # Force 1.0 - do not scale locations
                            
                            # Skip Y-up transform for collection exports with fake parent
                            # Fake parent baking already handles all transforms correctly
                            skip_yup_transform = (start_point.start_point_type == 'COLLECTION' and fake_parent is not None)
                            needs_transform = start_point.y_is_up and not skip_yup_transform  # Only transform if Y-up is needed and not skipped
                            
                            if needs_transform and object_names_to_export:
                                logger.log_step("transform_start", {
                                    **start_point_context,
                                    "scale_factor": scale_factor,
                                    "y_is_up": start_point.y_is_up,
                                    "source_unit": start_point.source_unit,
                                    "target_unit": start_point.target_unit,
                                    "objects_to_transform": len(object_names_to_export)
                                })
                                
                                # Backup and apply transforms for all objects to export
                                # Use object names and get fresh references from view_layer
                                for obj_name in object_names_to_export:
                                    if obj_name in context.view_layer.objects:
                                        obj = context.view_layer.objects[obj_name]
                                        # Backup original transform
                                        original_loc = obj.location.copy()
                                        original_rot = obj.rotation_euler.copy()
                                        original_scale = obj.scale.copy()
                                        
                                        transform_backups[obj.name] = {
                                            "location": original_loc,
                                            "rotation_euler": original_rot,
                                            "scale": original_scale
                                        }
                                        
                                        # Apply transforms in correct order:
                                        # 1. First apply Y-up rotation (if needed) to original location
                                        # 2. Then apply scale to the rotated location
                                        
                                        current_loc = original_loc.copy()
                                        current_rot = original_rot.copy()
                                        
                                        # NOTE: Pre-export Y-up rotation is disabled for testing (v0.1.37)
                                        # Testing if Omniverse compositor handles upAxis metadata without rotation
                                        # The upAxis metadata alone should tell viewers/compositors to interpret
                                        # the geometry in Y-up coordinate space.
                                        # TODO: Re-enable pre-export rotation if metadata-only approach doesn't work
                                        
                                        # Apply scale factor if needed (to already-rotated location if Y-up was applied)
                                        # IMPORTANT: Only scale location/position, NOT the scale transform itself
                                        # Unit conversion scales positions (2700mm → 2.7m) but geometry scale stays (1,1,1)
                                        if scale_factor != 1.0:
                                            current_loc = current_loc * scale_factor
                                            
                                            logger.log_step("scale_transform_applied", {
                                                **start_point_context,
                                                "object_name": obj.name,
                                                "original_location": tuple(original_loc),
                                                "scaled_location": tuple(current_loc),
                                                "scale_factor": scale_factor,
                                                "note": "Only location scaled, object scale remains unchanged"
                                            })
                                        
                                        # Keep original scale (don't modify obj.scale for unit conversion)
                                        current_scale = original_scale.copy()
                                        
                                        # Apply transforms to object
                                        obj.location = current_loc
                                        obj.rotation_euler = current_rot
                                        obj.scale = current_scale  # Keep original scale unchanged
                                
                                # Force update after transform changes
                                context.view_layer.update()
                            
                            if object_names_to_export:
                                export_params["selected_objects_only"] = True
                                
                                # REWRITTEN SELECTION LOGIC v0.1.27
                                # Previous approaches failed because:
                                # 1. Hiding all objects makes select_set() fail silently
                                # 2. bpy.ops.object.select_all() requires visible objects
                                # 
                                # New approach:
                                # 1. Deselect everything FIRST (while visible)
                                # 2. Then hide everything EXCEPT our targets
                                # 3. Select our targets directly
                                
                                # Step 1: Deselect all objects (while they're still visible)
                                for obj in context.view_layer.objects:
                                    try:
                                        obj.select_set(False)
                                    except:
                                        pass
                                
                                # Step 2: Ensure our target objects are visible, selected, and one is active
                                first_obj_set = False
                                for obj_name in object_names_to_export:
                                    if obj_name in context.view_layer.objects:
                                        view_layer_obj = context.view_layer.objects[obj_name]
                                        # Ensure object is visible
                                        view_layer_obj.hide_viewport = False
                                        view_layer_obj.hide_set(False)  # Also unhide in outliner
                                        # Set as active object first (required for selection to work reliably)
                                        if not first_obj_set:
                                            context.view_layer.objects.active = view_layer_obj
                                            first_obj_set = True
                                        # Now select it
                                        view_layer_obj.select_set(True)
                                
                                # Step 3: Force view layer update
                                context.view_layer.update()
                                
                                # Step 4: NOW hide all other objects (after selection is done)
                                for obj in context.view_layer.objects:
                                    if obj.name not in object_names_to_export:
                                        try:
                                            obj.hide_viewport = True
                                        except:
                                            pass
                                
                                # Verify selection worked
                                logger.log_step("selection_verification", {
                                    **start_point_context,
                                    "expected_objects": object_names_to_export,
                                    "selected_count": len(context.selected_objects),
                                    "selected_names": [o.name for o in context.selected_objects],
                                    "active_object": context.view_layer.objects.active.name if context.view_layer.objects.active else None
                                })
                            else:
                                # Fallback: no objects to export, use collection-based export
                                export_params["selected_objects_only"] = start_point.start_point_type != 'COLLECTION'
                            
                            # Add type-specific parameter
                            if start_point.start_point_type == 'COLLECTION':
                                export_params["collection"] = start_point.collection_name
                            else:
                                # For OBJECT type, use selected_objects_only to export only the isolated object
                                export_params["selected_objects_only"] = True

                            logger.log_step("usd_export_start", {
                                **start_point_context,
                                "export_params": export_params,
                                "sanitized_root_prim": sanitized_name,
                                "export_modifiers_enabled": start_point.export_modifiers,
                                "selected_objects_count": len(context.selected_objects),
                                "selected_object_names": [obj.name for obj in context.selected_objects]
                            })

                            # Safety check: Deselect any lights to ensure they're not exported
                            # This is in addition to export_lights=False parameter
                            lights_deselected = []
                            for obj in context.selected_objects:
                                if obj.type == 'LIGHT':
                                    obj.select_set(False)
                                    lights_deselected.append(obj.name)
                            
                            if lights_deselected:
                                logger.log_step("lights_deselected", {
                                    **start_point_context,
                                    "lights_deselected": lights_deselected
                                })

                            # Call Blender's USD export operator
                            # Capture any error messages from Blender's operator
                            try:
                                result = bpy.ops.wm.usd_export(**export_params)
                                
                                # Check for error messages in Blender's operator reports
                                error_messages = []
                                if hasattr(bpy.context, 'operator_properties_last'):
                                    # Try to get error from operator
                                    pass
                                
                                # Also check Blender's report system
                                if hasattr(bpy.context, 'window_manager'):
                                    reports = bpy.context.window_manager.popup_menu
                                
                            except Exception as export_error:
                                # Capture exception from operator call
                                failed_count += 1
                                logger.log_error(
                                    f"USD export operator raised exception for start point '{start_point.name}'",
                                    exception=export_error,
                                    context={**start_point_context, "export_params": export_params},
                                    recoverable=True
                                )
                                self.report({"ERROR"}, f"Failed to export '{start_point.name}': {str(export_error)}")
                                # Continue to cleanup even on export error
                            else:
                                if result == {"FINISHED"}:
                                    exported_count += 1
                                    logger.log_step("usd_export_success", {
                                        **start_point_context,
                                        "file_size_bytes": self._get_file_size(filepath)
                                    })
                                    
                                    # Add origin metadata if enabled
                                    if start_point.include_origin_metadata:
                                        self._add_origin_metadata(filepath, start_point, logger, start_point_context)
                                    
                                    # Apply stage metadata (metersPerUnit, upAxis) based on start point settings
                                    # v0.1.69: Use SAME bake approach for both OBJECT and COLLECTION exports
                                    # Root prim transforms (v0.1.67-68) caused mismatch when referencing together.
                                    # Baking transforms into geometry ensures consistent behavior.
                                    self._apply_stage_metadata(filepath, start_point, logger, start_point_context)
                                    
                                    self.report({"INFO"}, f"Successfully exported '{start_point.name}' to '{filepath}'.")
                                else:
                                    failed_count += 1
                                    # Try to get more detailed error information
                                    error_details = str(result)
                                    
                                    # Check if there are any error messages in Blender's console/reports
                                    # Blender operators often report errors via self.report() which we can't easily capture
                                    # But we can at least log the result code
                                    logger.log_error(
                                        f"USD export operator failed for start point '{start_point.name}' (result: {result})",
                                        context={
                                            **start_point_context, 
                                            "operator_result": str(result),
                                            "export_params": export_params,
                                            "sanitized_root_prim": sanitized_name
                                        },
                                        recoverable=True
                                    )
                                    self.report({"ERROR"}, f"Failed to export '{start_point.name}'. Check console for details.")
                            
                            # Restore transforms if they were applied
                            if transform_backups:
                                logger.log_step("transform_restore_start", {
                                    **start_point_context,
                                    "transforms_to_restore": len(transform_backups)
                                })
                                
                                for obj_name, backup in transform_backups.items():
                                    obj_ref = bpy.data.objects.get(obj_name)
                                    if obj_ref and obj_ref.name in context.view_layer.objects:
                                        try:
                                            obj_ref.location = backup["location"]
                                            obj_ref.rotation_euler = backup["rotation_euler"]
                                            obj_ref.scale = backup["scale"]
                                            logger.log_step("transform_restored", {
                                                **start_point_context,
                                                "object_name": obj_name
                                            })
                                        except Exception as e:
                                            logger.log_warning(
                                                f"Failed to restore transform for '{obj_name}': {e}",
                                                context=start_point_context
                                            )
                                
                                # Force update after transform restoration
                                context.view_layer.update()
                            
                            # Restore visibility state so the rest of the scene returns to normal
                            for obj_name, was_hidden in visibility_snapshot.items():
                                obj_ref = bpy.data.objects.get(obj_name)
                                if obj_ref:
                                    obj_ref.hide_viewport = was_hidden

                            # Restore baked transforms (collection export only)
                            # Must happen BEFORE cleanup to restore parent relationships
                            if baked_transforms and fake_parent:
                                _restore_baked_transforms(
                                    context=context,
                                    baked_transforms=baked_transforms,
                                    fake_parent=fake_parent,
                                    logger=logger,
                                    start_point_context=start_point_context,
                                )

                            # Cleanup fake parent (collection export only)
                            # Must happen BEFORE ScopedIsolation exits to restore parent relationships
                            if fake_parent:
                                _cleanup_fake_parent(
                                    context=context,
                                    fake_parent=fake_parent,
                                    parent_backups=fake_parent_backups,
                                    logger=logger,
                                    start_point_context=start_point_context,
                                )

                            # Store duplicated objects for cleanup AFTER ScopedIsolation exits
                            # This prevents ScopedIsolation from trying to restore state using deleted objects
                            duplicated_objects_for_cleanup.extend(duplicated_objects)
                            
                            # v0.1.14: Store mesh swaps for cleanup
                            if 'mesh_swaps' in dir() and mesh_swaps:
                                mesh_swaps_for_cleanup.update(mesh_swaps)
                            
                            # v0.1.17: Store name swaps for cleanup (OBJECT and COLLECTION types)
                            if 'name_swaps' in dir() and name_swaps:
                                name_swaps_for_cleanup.update(name_swaps)
                        
                        # ============================================================
                        # CLEANUP PHASE: Delete duplicates and restore original names
                        # ============================================================
                        if duplicated_objects_for_cleanup:
                            logger.log_step("cleanup_started", {
                                **start_point_context,
                                "duplicates_to_cleanup": len(duplicated_objects_for_cleanup)
                            })
                            
                            try:
                                # Step 1: Delete all duplicates
                                bpy.ops.object.select_all(action='DESELECT')
                                
                                duplicates_deleted = []
                                for dup_info in duplicated_objects_for_cleanup:
                                    dup_obj = dup_info.get("duplicate")
                                    if dup_obj:
                                        # Find the duplicate by its current name (which is the original name after swap)
                                        dup_ref = bpy.data.objects.get(dup_obj.name)
                                        if dup_ref:
                                            dup_ref.select_set(True)
                                            duplicates_deleted.append(dup_obj.name)
                                
                                if context.selected_objects:
                                    bpy.ops.object.delete(use_global=False)
                                
                                logger.log_step("duplicates_deleted", {
                                    **start_point_context,
                                    "count": len(duplicates_deleted),
                                    "names": duplicates_deleted
                                })
                                
                                # Step 2: Restore original names (rename __USDME_ORIG_* back to original)
                                names_restored = []
                                for dup_info in duplicated_objects_for_cleanup:
                                    original_obj = dup_info.get("original")
                                    original_name = dup_info.get("original_name")
                                    hidden_name = dup_info.get("hidden_name")
                                    
                                    if original_obj and original_name and hidden_name:
                                        # Find the object by its hidden name
                                        obj_ref = bpy.data.objects.get(hidden_name)
                                        if obj_ref:
                                            try:
                                                obj_ref.name = original_name
                                                names_restored.append({
                                                    "from": hidden_name,
                                                    "to": original_name
                                                })
                                            except Exception as e:
                                                logger.log_warning(
                                                    f"Failed to restore name '{hidden_name}' -> '{original_name}': {e}",
                                                    context=start_point_context
                                                )
                                
                                logger.log_step("names_restored", {
                                    **start_point_context,
                                    "count": len(names_restored),
                                    "restorations": names_restored
                                })
                                
                                # v0.1.14: Step 3: Restore mesh data names
                                mesh_names_restored = []
                                if mesh_swaps_for_cleanup:
                                    for hidden_mesh_name, swap_info in mesh_swaps_for_cleanup.items():
                                        original_mesh_name = swap_info.get('original_name')
                                        original_mesh = swap_info.get('original_mesh')
                                        dup_mesh = swap_info.get('dup_mesh')
                                        
                                        # The duplicate mesh (which had the original name) should be deleted
                                        # when we deleted the duplicate object, so we just need to restore
                                        # the original mesh's name
                                        if original_mesh and original_mesh.name in bpy.data.meshes:
                                            try:
                                                # Find the mesh by its hidden name
                                                mesh_ref = bpy.data.meshes.get(hidden_mesh_name)
                                                if mesh_ref:
                                                    mesh_ref.name = original_mesh_name
                                                    mesh_names_restored.append({
                                                        "from": hidden_mesh_name,
                                                        "to": original_mesh_name
                                                    })
                                            except Exception as e:
                                                logger.log_warning(
                                                    f"Failed to restore mesh name '{hidden_mesh_name}' -> '{original_mesh_name}': {e}",
                                                    context=start_point_context
                                                )
                                    
                                    logger.log_step("mesh_names_restored", {
                                        **start_point_context,
                                        "count": len(mesh_names_restored),
                                        "restorations": mesh_names_restored
                                    })
                                
                                logger.log_step("cleanup_complete", {
                                    **start_point_context,
                                    "duplicates_removed": len(duplicates_deleted),
                                    "names_restored": len(names_restored),
                                    "mesh_names_restored": len(mesh_names_restored)
                                })
                                
                            except Exception as e:
                                logger.log_error(
                                    f"Failed during cleanup: {str(e)}",
                                    context=start_point_context,
                                    recoverable=True
                                )
                                # Attempt emergency name restoration
                                try:
                                    for dup_info in duplicated_objects_for_cleanup:
                                        hidden_name = dup_info.get("hidden_name")
                                        original_name = dup_info.get("original_name")
                                        if hidden_name and original_name:
                                            obj_ref = bpy.data.objects.get(hidden_name)
                                            if obj_ref:
                                                obj_ref.name = original_name
                                except Exception:
                                    pass

                    except Exception as e:
                        failed_count += 1
                        
                        # #region agent log
                        try:
                            with open(r"e:\SynologyDrive\9999_LocalRepo\General_Dev\Master_Rules\.cursor\debug.log", "a", encoding="utf-8") as f:
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ops_export.py:638","message":"outer exception handler","data":{"start_point_name":start_point.name,"exception_type":type(e).__name__,"exception_msg":str(e)[:100],"duplicated_objects_count":len(duplicated_objects) if 'duplicated_objects' in locals() else 0},"timestamp":__import__("time").time()*1000})+"\n")
                        except: pass
                        # #endregion
                        
                        # ============================================================
                        # EXCEPTION CLEANUP: Cleanup fake parent, duplicates, and restore names
                        # ============================================================
                        # Restore baked transforms first (if they exist)
                        if 'baked_transforms' in locals() and baked_transforms and 'fake_parent' in locals() and fake_parent:
                            try:
                                _restore_baked_transforms(
                                    context=context,
                                    baked_transforms=baked_transforms,
                                    fake_parent=fake_parent,
                                    logger=logger,
                                    start_point_context=start_point_context,
                                )
                            except Exception as restore_error:
                                logger.log_warning(
                                    f"Failed to restore baked transforms during exception handling: {restore_error}",
                                    context=start_point_context,
                                )
                        
                        # Cleanup fake parent (if it exists)
                        if 'fake_parent' in locals() and fake_parent:
                            try:
                                _cleanup_fake_parent(
                                    context=context,
                                    fake_parent=fake_parent,
                                    parent_backups=fake_parent_backups if 'fake_parent_backups' in locals() else {},
                                    logger=logger,
                                    start_point_context=start_point_context,
                                )
                            except Exception as cleanup_error:
                                logger.log_warning(
                                    f"Failed to cleanup fake parent during exception handling: {cleanup_error}",
                                    context=start_point_context,
                                )
                        
                        cleanup_needed = []
                        if 'duplicated_objects' in locals() and duplicated_objects:
                            cleanup_needed.extend(duplicated_objects)
                        if 'duplicated_objects_for_cleanup' in locals() and duplicated_objects_for_cleanup:
                            cleanup_needed.extend(duplicated_objects_for_cleanup)
                        
                        if cleanup_needed:
                            logger.log_step("exception_cleanup_started", {
                                **start_point_context,
                                "duplicates_to_cleanup": len(cleanup_needed)
                            })
                            
                            try:
                                # Step 1: Delete all duplicates
                                bpy.ops.object.select_all(action='DESELECT')
                                
                                duplicates_deleted = []
                                for dup_info in cleanup_needed:
                                    dup_obj = dup_info.get("duplicate")
                                    if dup_obj:
                                        dup_ref = bpy.data.objects.get(dup_obj.name)
                                        if dup_ref:
                                            dup_ref.select_set(True)
                                            duplicates_deleted.append(dup_obj.name)
                                
                                if context.selected_objects:
                                    bpy.ops.object.delete(use_global=False)
                                
                                # Step 2: Restore original names
                                names_restored = []
                                for dup_info in cleanup_needed:
                                    hidden_name = dup_info.get("hidden_name")
                                    original_name = dup_info.get("original_name")
                                    
                                    if hidden_name and original_name:
                                        obj_ref = bpy.data.objects.get(hidden_name)
                                        if obj_ref:
                                            try:
                                                obj_ref.name = original_name
                                                names_restored.append(original_name)
                                            except Exception:
                                                pass
                                
                                logger.log_step("exception_cleanup_complete", {
                                    **start_point_context,
                                    "duplicates_removed": len(duplicates_deleted),
                                    "names_restored": len(names_restored),
                                    "exception_occurred": True
                                })
                                
                            except Exception as cleanup_error:
                                logger.log_error(
                                    f"Failed during exception cleanup: {str(cleanup_error)}",
                                    context=start_point_context,
                                    recoverable=True
                                )
                                # Emergency name restoration attempt
                                try:
                                    for dup_info in cleanup_needed:
                                        hidden_name = dup_info.get("hidden_name")
                                        original_name = dup_info.get("original_name")
                                        if hidden_name and original_name:
                                            obj_ref = bpy.data.objects.get(hidden_name)
                                            if obj_ref:
                                                obj_ref.name = original_name
                                except Exception:
                                    pass
                        
                        logger.log_error(
                            f"Unexpected error processing start point '{start_point.name}'",
                            exception=e,
                            context=start_point_context,
                            recoverable=False
                        )
                        self.report({"ERROR"}, f"Error exporting '{start_point.name}': {str(e)}")

                logger.log_step("batch_operation_complete", {
                    "exported_count": exported_count,
                    "failed_count": failed_count,
                    "total_processed": len(enabled_start_points)
                })

        except Exception as e:
            logger.log_error(
                "Critical error during batch export operation",
                exception=e,
                context={"exported_count": exported_count, "failed_count": failed_count},
                recoverable=False
            )
            self.report({"ERROR"}, f"Critical export error: {str(e)}")
            logger.end_operation(success=False, result_info={"critical_error": str(e)})
            return {"CANCELLED"}

        # Final summary
        success = exported_count > 0
        result_info = {
            "exported_count": exported_count,
            "failed_count": failed_count,
            "total_start_points": len(enabled_start_points)
        }

        if success:
            logger.log_step("operation_success", result_info)
            self.report({"INFO"}, f"USD Multi Export completed: {exported_count} successful, {failed_count} failed.")
        else:
            logger.log_step("operation_failed", result_info)

        logger.end_operation(success=success, result_info=result_info)
        return {"FINISHED"} if success else {"CANCELLED"}

    def _get_file_size(self, filepath: str) -> int:
        """Get file size in bytes, return 0 if file doesn't exist or can't be read."""
        try:
            import os
            return os.path.getsize(filepath)
        except (OSError, IOError):
            return 0

    def _add_origin_metadata(self, filepath: str, start_point, logger, start_point_context: dict) -> None:
        """Add origin metadata as custom attributes to the root prim of the USD file.
        
        Args:
            filepath: Path to the exported USD file
            start_point: The start point being exported
            logger: Logger instance for logging
            start_point_context: Context dictionary for logging
        """
        try:
            from pxr import Usd, Sdf
            import getpass
            import socket
            from datetime import datetime
            import os
            
            # Open the USD stage
            stage = Usd.Stage.Open(filepath)
            
            # Get the root prim (using start point name)
            root_prim_path = f"/{start_point.name}"
            root_prim = stage.GetPrimAtPath(root_prim_path)
            
            # Fallback to default prim if root prim not found
            if not root_prim.IsValid():
                root_prim = stage.GetDefaultPrim()
            
            if root_prim.IsValid():
                blend_filepath = bpy.data.filepath
                
                # Add custom attributes with usdme: namespace
                root_prim.CreateAttribute("usdme:origin_file", Sdf.ValueTypeNames.String).Set(
                    blend_filepath if blend_filepath else "Unsaved"
                )
                root_prim.CreateAttribute("usdme:origin_filename", Sdf.ValueTypeNames.String).Set(
                    os.path.basename(blend_filepath) if blend_filepath else "Unsaved"
                )
                root_prim.CreateAttribute("usdme:origin_username", Sdf.ValueTypeNames.String).Set(
                    getpass.getuser()
                )
                root_prim.CreateAttribute("usdme:origin_computer", Sdf.ValueTypeNames.String).Set(
                    socket.gethostname()
                )
                root_prim.CreateAttribute("usdme:export_timestamp", Sdf.ValueTypeNames.String).Set(
                    datetime.now().isoformat()
                )
                
                # Add object name if start point type is OBJECT
                if start_point.start_point_type == 'OBJECT' and start_point.object_name:
                    root_prim.CreateAttribute("usdme:origin_object_name", Sdf.ValueTypeNames.String).Set(
                        start_point.object_name
                    )
                
                # Add collection name if start point type is COLLECTION
                if start_point.start_point_type == 'COLLECTION' and start_point.collection_name:
                    root_prim.CreateAttribute("usdme:origin_collection_name", Sdf.ValueTypeNames.String).Set(
                        start_point.collection_name
                    )
                
                # Save the stage
                stage.Save()
                
                logger.log_step("origin_metadata_added", {
                    **start_point_context,
                    "root_prim_path": root_prim_path if root_prim.IsValid() else "defaultPrim",
                    "metadata_added": True
                })
            else:
                logger.log_warning(
                    f"Could not find root prim for metadata. Path: {root_prim_path}, Default prim: {stage.GetDefaultPrim()}",
                    context=start_point_context
                )
                
        except ImportError:
            logger.log_warning(
                "USD Python API (pxr) not available. Origin metadata not added.",
                context=start_point_context
            )
        except Exception as e:
            logger.log_error(
                f"Failed to add origin metadata: {str(e)}",
                exception=e,
                context=start_point_context,
                recoverable=True
            )


    def _apply_stage_metadata(self, filepath: str, start_point, logger, start_point_context: dict) -> None:
        """Apply stage-level metadata (metersPerUnit, upAxis) and coordinate transforms to the USD file.
        
        This post-processes the exported USD file to:
        1. Set correct unit scale (metersPerUnit) based on target_unit setting
        2. Set up-axis metadata and apply geometric rotation if y_is_up is enabled
        
        For Y-up conversion: Blender uses Z-up, so we rotate -90° around X axis
        to convert geometry to Y-up coordinate system.
        
        Args:
            filepath: Path to the exported USD file
            start_point: The start point being exported (contains y_is_up, target_unit)
            logger: Logger instance for logging
            start_point_context: Context dictionary for logging
        """
        try:
            # Map target_unit to metersPerUnit value
            unit_to_meters = {
                'MILLIMETERS': 0.001,
                'CENTIMETERS': 0.01,
                'METERS': 1.0,
                'KILOMETERS': 1000.0,
            }

            target_unit = getattr(start_point, 'target_unit', 'METERS')
            meters_per_unit = unit_to_meters.get(target_unit, 1.0)

            # Determine up-axis
            y_is_up = getattr(start_point, 'y_is_up', False)

            source_unit = getattr(start_point, 'source_unit', 'METERS')
            scale_factor = start_point.get_scale_factor() if hasattr(start_point, 'get_scale_factor') else 1.0

            bake_result = usd_bake.bake_usd_geometry(
                filepath=filepath,
                scale_factor=scale_factor,
                y_is_up=y_is_up,
                meters_per_unit=meters_per_unit,
                logger=logger,
                start_point_context=start_point_context,
            )

            if not bake_result.get("success"):
                logger.log_warning(
                    "USD bake step did not complete successfully.",
                    context={
                        **start_point_context,
                        "bake_result": bake_result,
                    }
                )
                return

            # Clean up any temp files left by USD library
            # These have the same base name but random suffixes like .1dqzwk, .634rf1
            import os
            import glob
            base_path = os.path.splitext(filepath)[0]
            temp_pattern = f"{base_path}.*"
            valid_extensions = {'.usd', '.usda', '.usdc', '.usdz'}
            for temp_file in glob.glob(temp_pattern):
                ext = os.path.splitext(temp_file)[1].lower()
                if ext not in valid_extensions and os.path.isfile(temp_file):
                    try:
                        os.remove(temp_file)
                        logger.log_step("temp_file_cleaned", {
                            **start_point_context,
                            "temp_file": temp_file,
                        })
                    except OSError:
                        pass  # Ignore cleanup failures

            logger.log_step("stage_bake_applied", {
                **start_point_context,
                "approach": "geometry_bake_and_metadata",
                "approach_note": "Geometry baked to target units/axis, metadata matches - no Omniverse Resolve needed",
                "meters_per_unit": meters_per_unit,
                "source_unit": source_unit,
                "target_unit": target_unit,
                "scale_factor": scale_factor,
                "up_axis": "Y" if y_is_up else "Z",
                "y_is_up": y_is_up,
                "bake_result": bake_result,
            })

        except Exception as e:
            logger.log_error(
                f"Failed to apply stage metadata: {str(e)}",
                exception=e,
                context=start_point_context,
                recoverable=True
            )

    def _apply_collection_root_transforms(self, filepath: str, start_point, logger, start_point_context: dict) -> None:
        """Apply scale and rotation transforms to the USD root prim for collection exports.
        
        v0.1.68: Instead of baking transforms into geometry (which caused issues for collections),
        we apply the scale and Y-up rotation to the root Xform/Scope in the USD file.
        This preserves the original geometry while providing correct transforms.
        
        Args:
            filepath: Path to the exported USD file
            start_point: The start point being exported
            logger: Logger instance
            start_point_context: Context dict for logging
        """
        try:
            from pxr import Usd, UsdGeom, Gf
            
            # Get settings
            y_is_up = getattr(start_point, 'y_is_up', False)
            source_unit = getattr(start_point, 'source_unit', 'METERS')
            target_unit = getattr(start_point, 'target_unit', 'METERS')
            
            # v0.1.68 FIX: Calculate scale factor directly from source/target units
            # The get_scale_factor() was returning 1.0 because it's designed for Blender transforms,
            # not for unit conversion. We need to calculate the conversion ourselves.
            unit_scale = {
                'MILLIMETERS': 1000.0,  # 1 meter = 1000 millimeters
                'CENTIMETERS': 100.0,   # 1 meter = 100 centimeters
                'METERS': 1.0,          # 1 meter = 1 meter
                'KILOMETERS': 0.001,    # 1 meter = 0.001 kilometers
            }
            source_scale = unit_scale.get(source_unit, 1.0)
            target_scale = unit_scale.get(target_unit, 1.0)
            # Convert from source to target: if source is meters (1.0) and target is cm (100.0),
            # we need to multiply by 100 to convert meter values to centimeter values
            scale_factor = target_scale / source_scale
            
            # Map target_unit to metersPerUnit
            unit_to_meters = {
                'MILLIMETERS': 0.001,
                'CENTIMETERS': 0.01,
                'METERS': 1.0,
                'KILOMETERS': 1000.0,
            }
            meters_per_unit = unit_to_meters.get(target_unit, 1.0)
            
            # Open stage
            stage = Usd.Stage.Open(filepath)
            if not stage:
                logger.log_error("Could not open stage for root transform application", context=start_point_context)
                return
            
            # v0.1.68 FIX: Use default prim directly instead of trying to construct path
            root_prim = stage.GetDefaultPrim()
                
            if not root_prim or not root_prim.IsValid():
                logger.log_warning("Could not find root prim for transform application", context=start_point_context)
                return
            
            # Apply transforms to root prim
            xformable = UsdGeom.Xformable(root_prim)
            if not xformable:
                logger.log_warning("Root prim is not Xformable", context=start_point_context)
                return
            
            # Clear existing xformOps and create new ones
            xformable.ClearXformOpOrder()
            
            # Build the combined transform:
            # Order matters! We want to first rotate to Y-up, then scale
            # This is because USD applies transforms in order: first in list applies first
            
            if y_is_up:
                # Rotate -90° around X to convert Z-up to Y-up
                rotate_op = xformable.AddRotateXYZOp()
                rotate_op.Set(Gf.Vec3f(-90.0, 0.0, 0.0))
            
            if scale_factor != 1.0:
                scale_op = xformable.AddScaleOp()
                scale_op.Set(Gf.Vec3f(scale_factor, scale_factor, scale_factor))
            
            # Set stage metadata
            UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y if y_is_up else UsdGeom.Tokens.z)
            
            stage.Save()
            
            logger.log_step("collection_root_transforms_applied", {
                **start_point_context,
                "root_prim_path": str(root_prim.GetPath()),
                "scale_factor": scale_factor,
                "y_is_up": y_is_up,
                "meters_per_unit": meters_per_unit,
                "source_unit": source_unit,
                "target_unit": target_unit,
            })
            
        except Exception as e:
            logger.log_error(
                f"Failed to apply collection root transforms: {str(e)}",
                exception=e,
                context=start_point_context,
                recoverable=True
            )

    def _build_duplicate_name(self, base_name: str, index: int) -> str:
        """Create a deterministic duplicate name for USD exports."""
        sanitized = re.sub(r"[^0-9A-Za-z_]", "_", base_name or "Object")
        sanitized = sanitized.strip("_")
        if not sanitized:
            sanitized = "USDME_Object"
        return f"{sanitized}_dup{index}"


__all__ = ["USDME_OT_export_start_points"]


