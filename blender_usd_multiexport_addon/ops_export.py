from __future__ import annotations

import re

import bpy
from bpy.types import Context, Operator

from . import logging_utils, path_resolver, state_manager


class USDME_OT_export_endpoints(Operator):
    """Export all enabled USD Multi Export endpoints.

    Exports each enabled endpoint to a USD file, with support for:
    - Collection or Object type endpoints
    - Subfolder creation (USD_Endpoint/)
    - Origin metadata tracking
    - Safe scene isolation during export
    """

    bl_idname = "usdme.export_endpoints"
    bl_label = "Export Endpoints"
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
                "total_endpoints": len(settings.endpoints),
                "verbose_mode": settings.verbose_logging
            }
        )

        if not settings.endpoints:
            logger.log_step("validation", {"result": "no_endpoints"})
            self.report({"INFO"}, "No USD Multi Export endpoints defined on this scene.")
            logger.end_operation(success=False, result_info={"reason": "no_endpoints"})
            return {"CANCELLED"}

        try:
            enabled_endpoints = [ep for ep in settings.endpoints if ep.enabled]
            logger.log_step("endpoint_filtering", {
                "total_endpoints": len(settings.endpoints),
                "enabled_endpoints": len(enabled_endpoints)
            })
        except Exception as e:
            logger.log_error(
                "Failed to filter endpoints",
                exception=e,
                context={"total_endpoints": len(settings.endpoints) if settings.endpoints else 0},
                recoverable=False
            )
            self.report({"ERROR"}, f"Failed to process endpoints: {str(e)}")
            logger.end_operation(success=False, result_info={"reason": "endpoint_filtering_error", "error": str(e)})
            return {"CANCELLED"}

        if not enabled_endpoints:
            logger.log_warning(
                "All USD Multi Export endpoints are disabled; nothing to export.",
                suggestion="Enable at least one endpoint in the USD Multi Export panel."
            )
            self.report({"WARNING"}, "All USD Multi Export endpoints are disabled; nothing to export.")
            logger.end_operation(success=False, result_info={"reason": "all_disabled"})
            return {"CANCELLED"}

        # Pre-flight validation: Check all enabled endpoints for completeness
        logger.log_step("preflight_validation_start", {
            "endpoint_count": len(enabled_endpoints)
        })
        
        try:
            invalid_endpoints = []
            for endpoint in enabled_endpoints:
                issues = []
                
                # Type-specific validation
                if endpoint.endpoint_type == 'COLLECTION':
                    if not endpoint.collection_name or not endpoint.collection_name.strip():
                        issues.append("missing collection")
                    elif not bpy.data.collections.get(endpoint.collection_name):
                        issues.append(f"collection '{endpoint.collection_name}' not found")
                elif endpoint.endpoint_type == 'OBJECT':
                    if not endpoint.object_name or not endpoint.object_name.strip():
                        issues.append("missing object")
                    elif not bpy.data.objects.get(endpoint.object_name):
                        issues.append(f"object '{endpoint.object_name}' not found")
                
                # Filepath validation (common to both types)
                if not endpoint.filepath or not endpoint.filepath.strip():
                    issues.append("missing filepath")
                
                if issues:
                    invalid_endpoints.append((endpoint.name, issues))
        except Exception as e:
            logger.log_error(
                "Exception during pre-flight validation",
                exception=e,
                context={"endpoint_count": len(enabled_endpoints)},
                recoverable=False
            )
            self.report({"ERROR"}, f"Error during validation: {str(e)}")
            logger.end_operation(success=False, result_info={"reason": "preflight_validation_exception", "error": str(e)})
            return {"CANCELLED"}
        
        logger.log_step("preflight_validation_complete", {
            "valid_endpoints": len(enabled_endpoints) - len(invalid_endpoints),
            "invalid_endpoints": len(invalid_endpoints)
        })
        
        if invalid_endpoints:
            logger.log_step("preflight_validation_failed", {
                "invalid_endpoints": [{"name": name, "issues": issues} for name, issues in invalid_endpoints]
            })
            error_msg = "Some endpoints are incomplete:\n"
            for name, issues in invalid_endpoints:
                error_msg += f"  • {name}: {', '.join(issues)}\n"
            error_msg += "\nPlease fix these issues before exporting."
            logger.log_error(
                "Pre-flight validation failed: incomplete endpoints detected",
                context={"invalid_endpoints": invalid_endpoints},
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
                    "endpoint_count": len(enabled_endpoints),
                    "state_backups": state_mgr.get_backup_count()
                })

                for i, endpoint in enumerate(enabled_endpoints, 1):
                    endpoint_context = {
                        "endpoint_index": i,
                        "endpoint_name": endpoint.name,
                        "endpoint_type": endpoint.endpoint_type,
                        "collection_name": endpoint.collection_name if endpoint.endpoint_type == 'COLLECTION' else None,
                        "object_name": endpoint.object_name if endpoint.endpoint_type == 'OBJECT' else None,
                        "filepath": endpoint.filepath
                    }

                    try:
                        logger.log_step("endpoint_processing_start", endpoint_context)

                        # Type-specific validation
                        if endpoint.endpoint_type == 'COLLECTION':
                            if not endpoint.collection_name or not endpoint.collection_name.strip():
                                logger.log_error(
                                    f"Endpoint '{endpoint.name}' has no collection specified. Please select a collection.",
                                    context={
                                        **endpoint_context,
                                        "available_collections": [c.name for c in bpy.data.collections]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Endpoint '{endpoint.name}': No collection specified.")
                                failed_count += 1
                                continue
                        elif endpoint.endpoint_type == 'OBJECT':
                            if not endpoint.object_name or not endpoint.object_name.strip():
                                logger.log_error(
                                    f"Endpoint '{endpoint.name}' has no object specified. Please select an object.",
                                    context={
                                        **endpoint_context,
                                        "available_objects": [o.name for o in bpy.data.objects]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Endpoint '{endpoint.name}': No object specified.")
                                failed_count += 1
                                continue

                        # Validate filepath is not empty
                        if not endpoint.filepath or not endpoint.filepath.strip():
                            logger.log_error(
                                f"Endpoint '{endpoint.name}' has no filepath specified. Please set an export filepath.",
                                context={
                                    **endpoint_context
                                },
                                recoverable=True
                            )
                            self.report({"WARNING"}, f"Endpoint '{endpoint.name}': No filepath specified.")
                            failed_count += 1
                            continue

                        # Get the target based on type
                        target = None
                        if endpoint.endpoint_type == 'COLLECTION':
                            target = bpy.data.collections.get(endpoint.collection_name)
                            if not target:
                                logger.log_error(
                                    f"Collection '{endpoint.collection_name}' not found for endpoint '{endpoint.name}'",
                                    context={
                                        **endpoint_context,
                                        "available_collections": [c.name for c in bpy.data.collections]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Endpoint '{endpoint.name}': Collection '{endpoint.collection_name}' not found.")
                                failed_count += 1
                                continue
                            logger.log_step("collection_found", {
                                **endpoint_context,
                                "collection_objects": len(target.objects)
                            })
                        elif endpoint.endpoint_type == 'OBJECT':
                            target = bpy.data.objects.get(endpoint.object_name)
                            if not target:
                                logger.log_error(
                                    f"Object '{endpoint.object_name}' not found for endpoint '{endpoint.name}'",
                                    context={
                                        **endpoint_context,
                                        "available_objects": [o.name for o in bpy.data.objects]
                                    },
                                    recoverable=True
                                )
                                self.report({"WARNING"}, f"Endpoint '{endpoint.name}': Object '{endpoint.object_name}' not found.")
                                failed_count += 1
                                continue
                            logger.log_step("object_found", {
                                **endpoint_context,
                                "object_type": target.type
                            })

                        # Resolve filepath using PathResolver
                        filepath = path_resolver.resolve_export_path(endpoint.filepath)
                        if not filepath:
                            logger.log_error(
                                f"Failed to resolve filepath for endpoint '{endpoint.name}': '{endpoint.filepath}'",
                                context={
                                    **endpoint_context,
                                    "original_filepath": endpoint.filepath
                                },
                                recoverable=True
                            )
                            failed_count += 1
                            continue

                        logger.log_step("filepath_resolved", {
                            **endpoint_context,
                            "resolved_filepath": filepath,
                            "relative_input": endpoint.filepath,
                            "directory_created": True  # PathResolver creates directories automatically
                        })

                        # Create subfolder if enabled
                        if endpoint.create_subfolder:
                            import os
                            from pathlib import Path
                            
                            # Get the target name (collection or object) for filename generation
                            target_name = endpoint.collection_name if endpoint.endpoint_type == 'COLLECTION' else endpoint.object_name
                            
                            # Get the parent directory of the resolved filepath
                            file_dir = Path(filepath).parent
                            
                            # Check if parent directory is already named "USD_Endpoint"
                            # If so, we don't need to create another subfolder
                            if file_dir.name == "USD_Endpoint":
                                # Already in USD_Endpoint folder, just ensure filename is correct
                                file_path_obj = Path(filepath)
                                if file_path_obj.is_dir() or not file_path_obj.name or file_path_obj.suffix == '':
                                    # Generate filename using target name
                                    if target_name:
                                        filename = f"{target_name}.usd"
                                    else:
                                        filename = f"{endpoint.name}.usd"
                                    filepath = str(file_dir / filename)
                                
                                logger.log_step("subfolder_already_exists", {
                                    **endpoint_context,
                                    "subfolder_path": str(file_dir),
                                    "updated_filepath": filepath
                                })
                            else:
                                # Create subfolder path: USD_Endpoint/ (just the name, no object/collection name)
                                subfolder_name = "USD_Endpoint"
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
                                        filename = f"{endpoint.name}.usd"
                                else:
                                    filename = file_path_obj.name
                                
                                filepath = str(subfolder_path / filename)
                                
                                logger.log_step("subfolder_created", {
                                    **endpoint_context,
                                    "subfolder_path": str(subfolder_path),
                                    "updated_filepath": filepath
                                })

                        # Use ScopedIsolation to safely isolate and export this endpoint
                        # Pass the target (Collection or Object) directly
                        with state_manager.ScopedIsolation(context, target, include_subcollections=endpoint.include_subcollections if endpoint.endpoint_type == 'COLLECTION' else True) as isolation:
                            logger.log_step("isolation_started", endpoint_context)

                            # USD export parameters - based on Blender 5.0 research
                            # Note: Second opinion analysis suggests verifying these parameter names
                            # against bpy.ops.wm.usd_export.get_rna_type().properties for Blender 5.0
                            
                            # Sanitize root_prim_path: USD prim paths must be valid identifiers
                            # Replace spaces and special characters with underscores
                            sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', endpoint.name)
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
                            # Reference: NVIDIA_BLender_BestPractise.md section 6.1
                            subdivision_modifiers_applied = []
                            if endpoint.export_subdivision:
                                # Following NVIDIA pattern: apply modifiers to bake geometry into mesh
                                if endpoint.endpoint_type == 'OBJECT':
                                    obj = bpy.data.objects.get(endpoint.object_name)
                                    if obj and obj.type == 'MESH':
                                        # Remove shape keys first (NVIDIA pattern)
                                        if obj.data.shape_keys:
                                            try:
                                                obj.select_set(True)
                                                context.view_layer.objects.active = obj
                                                bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                                                logger.log_step("shape_keys_removed", {
                                                    **endpoint_context,
                                                    "object_name": obj.name
                                                })
                                            except Exception as e:
                                                logger.log_warning(
                                                    f"Failed to remove shape keys from '{obj.name}': {str(e)}",
                                                    context=endpoint_context
                                                )
                                        
                                        # Apply subdivision modifiers (NVIDIA pattern)
                                        for mod in list(obj.modifiers):  # Use list() to avoid iteration issues
                                            if mod.type == 'SUBSURF':
                                                try:
                                                    obj.select_set(True)
                                                    context.view_layer.objects.active = obj
                                                    bpy.ops.object.modifier_apply(modifier=mod.name, single_user=True)
                                                    subdivision_modifiers_applied.append({
                                                        "object": obj.name,
                                                        "modifier": mod.name,
                                                        "levels": mod.levels if hasattr(mod, 'levels') else None,
                                                        "render_levels": mod.render_levels if hasattr(mod, 'render_levels') else None
                                                    })
                                                    logger.log_step("subdivision_modifier_applied", {
                                                        **endpoint_context,
                                                        "object_name": obj.name,
                                                        "modifier_name": mod.name
                                                    })
                                                except Exception as e:
                                                    logger.log_warning(
                                                        f"Failed to apply subdivision modifier '{mod.name}' on '{obj.name}': {str(e)}",
                                                        context=endpoint_context
                                                    )
                                        
                                elif endpoint.endpoint_type == 'COLLECTION':
                                    collection = bpy.data.collections.get(endpoint.collection_name)
                                    if collection:
                                        for obj in collection.all_objects:
                                            if obj.type == 'MESH':
                                                # Remove shape keys first
                                                if obj.data.shape_keys:
                                                    try:
                                                        obj.select_set(True)
                                                        context.view_layer.objects.active = obj
                                                        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                                                        logger.log_step("shape_keys_removed", {
                                                            **endpoint_context,
                                                            "object_name": obj.name
                                                        })
                                                    except Exception as e:
                                                        logger.log_warning(
                                                            f"Failed to remove shape keys from '{obj.name}': {str(e)}",
                                                            context=endpoint_context
                                                        )
                                                
                                                # Apply subdivision modifiers
                                                for mod in list(obj.modifiers):
                                                    if mod.type == 'SUBSURF':
                                                        try:
                                                            obj.select_set(True)
                                                            context.view_layer.objects.active = obj
                                                            bpy.ops.object.modifier_apply(modifier=mod.name, single_user=True)
                                                            subdivision_modifiers_applied.append({
                                                                "object": obj.name,
                                                                "modifier": mod.name,
                                                                "levels": mod.levels if hasattr(mod, 'levels') else None,
                                                                "render_levels": mod.render_levels if hasattr(mod, 'render_levels') else None
                                                            })
                                                            logger.log_step("subdivision_modifier_applied", {
                                                                **endpoint_context,
                                                                "object_name": obj.name,
                                                                "modifier_name": mod.name
                                                            })
                                                        except Exception as e:
                                                            logger.log_warning(
                                                                f"Failed to apply subdivision modifier '{mod.name}' on '{obj.name}': {str(e)}",
                                                                context=endpoint_context
                                                            )
                                
                                if subdivision_modifiers_applied:
                                    logger.log_step("subdivision_modifiers_applied", {
                                        **endpoint_context,
                                        "modifiers_applied": len(subdivision_modifiers_applied),
                                        "modifiers": subdivision_modifiers_applied
                                    })
                                else:
                                    logger.log_warning(
                                        "Subdivision export enabled but no subdivision modifiers found on target objects",
                                        context=endpoint_context
                                    )
                            
                            # Add type-specific parameter
                            if endpoint.endpoint_type == 'COLLECTION':
                                export_params["collection"] = endpoint.collection_name
                            else:
                                # For OBJECT type, use selected_objects_only to export only the isolated object
                                export_params["selected_objects_only"] = True

                            logger.log_step("usd_export_start", {
                                **endpoint_context,
                                "export_params": export_params,
                                "sanitized_root_prim": sanitized_name,
                                "subdivision_modifiers_applied": len(subdivision_modifiers_applied) if endpoint.export_subdivision else 0
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
                                    **endpoint_context,
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
                                    f"USD export operator raised exception for endpoint '{endpoint.name}'",
                                    exception=export_error,
                                    context={**endpoint_context, "export_params": export_params},
                                    recoverable=True
                                )
                                self.report({"ERROR"}, f"Failed to export '{endpoint.name}': {str(export_error)}")
                                continue

                            if result == {"FINISHED"}:
                                exported_count += 1
                                logger.log_step("usd_export_success", {
                                    **endpoint_context,
                                    "file_size_bytes": self._get_file_size(filepath)
                                })
                                
                                # Add origin metadata if enabled
                                if endpoint.include_origin_metadata:
                                    self._add_origin_metadata(filepath, endpoint, logger, endpoint_context)
                                
                                self.report({"INFO"}, f"Successfully exported '{endpoint.name}' to '{filepath}'.")
                            else:
                                failed_count += 1
                                # Try to get more detailed error information
                                error_details = str(result)
                                
                                # Check if there are any error messages in Blender's console/reports
                                # Blender operators often report errors via self.report() which we can't easily capture
                                # But we can at least log the result code
                                logger.log_error(
                                    f"USD export operator failed for endpoint '{endpoint.name}' (result: {result})",
                                    context={
                                        **endpoint_context, 
                                        "operator_result": str(result),
                                        "export_params": export_params,
                                        "sanitized_root_prim": sanitized_name
                                    },
                                    recoverable=True
                                )
                                self.report({"ERROR"}, f"Failed to export '{endpoint.name}'. Check console for details.")

                    except Exception as e:
                        failed_count += 1
                        logger.log_error(
                            f"Unexpected error processing endpoint '{endpoint.name}'",
                            exception=e,
                            context=endpoint_context,
                            recoverable=False
                        )
                        self.report({"ERROR"}, f"Error exporting '{endpoint.name}': {str(e)}")

                logger.log_step("batch_operation_complete", {
                    "exported_count": exported_count,
                    "failed_count": failed_count,
                    "total_processed": len(enabled_endpoints)
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
            "total_endpoints": len(enabled_endpoints)
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

    def _add_origin_metadata(self, filepath: str, endpoint, logger, endpoint_context: dict) -> None:
        """Add origin metadata as custom attributes to the root prim of the USD file.
        
        Args:
            filepath: Path to the exported USD file
            endpoint: The endpoint being exported
            logger: Logger instance for logging
            endpoint_context: Context dictionary for logging
        """
        try:
            from pxr import Usd, Sdf
            import getpass
            import socket
            from datetime import datetime
            import os
            
            # Open the USD stage
            stage = Usd.Stage.Open(filepath)
            
            # Get the root prim (using endpoint name)
            root_prim_path = f"/{endpoint.name}"
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
                
                # Add object name if endpoint type is OBJECT
                if endpoint.endpoint_type == 'OBJECT' and endpoint.object_name:
                    root_prim.CreateAttribute("usdme:origin_object_name", Sdf.ValueTypeNames.String).Set(
                        endpoint.object_name
                    )
                
                # Add collection name if endpoint type is COLLECTION
                if endpoint.endpoint_type == 'COLLECTION' and endpoint.collection_name:
                    root_prim.CreateAttribute("usdme:origin_collection_name", Sdf.ValueTypeNames.String).Set(
                        endpoint.collection_name
                    )
                
                # Save the stage
                stage.Save()
                
                logger.log_step("origin_metadata_added", {
                    **endpoint_context,
                    "root_prim_path": root_prim_path if root_prim.IsValid() else "defaultPrim",
                    "metadata_added": True
                })
            else:
                logger.log_warning(
                    f"Could not find root prim for metadata. Path: {root_prim_path}, Default prim: {stage.GetDefaultPrim()}",
                    context=endpoint_context
                )
                
        except ImportError:
            logger.log_warning(
                "USD Python API (pxr) not available. Origin metadata not added.",
                context=endpoint_context
            )
        except Exception as e:
            logger.log_error(
                f"Failed to add origin metadata: {str(e)}",
                exception=e,
                context=endpoint_context,
                recoverable=True
            )


__all__ = ["USDME_OT_export_endpoints"]


