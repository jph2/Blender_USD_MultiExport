from __future__ import annotations

import bpy
from bpy.types import Context, Operator

from . import logging_utils, path_resolver, state_manager


class USDME_OT_export_endpoints(Operator):
    """Export all enabled USD Multi Export endpoints.

    This is an initial stub implementation. It does not yet isolate visibility
    or call the USD exporter; instead, it iterates endpoints and reports what
    would be exported. This keeps the addon safe to enable while the core
    export workflow is being implemented.
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

        enabled_endpoints = [ep for ep in settings.endpoints if ep.enabled]
        logger.log_step("endpoint_filtering", {
            "total_endpoints": len(settings.endpoints),
            "enabled_endpoints": len(enabled_endpoints)
        })

        if not enabled_endpoints:
            logger.log_warning(
                "All USD Multi Export endpoints are disabled; nothing to export.",
                suggestion="Enable at least one endpoint in the USD Multi Export panel."
            )
            self.report({"WARNING"}, "All USD Multi Export endpoints are disabled; nothing to export.")
            logger.end_operation(success=False, result_info={"reason": "all_disabled"})
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
                        "collection_name": endpoint.collection_name,
                        "filepath": endpoint.filepath
                    }

                    try:
                        logger.log_step("endpoint_processing_start", endpoint_context)

                        # Get the target collection
                        collection = bpy.data.collections.get(endpoint.collection_name)
                        if not collection:
                            logger.log_error(
                                f"Collection '{endpoint.collection_name}' not found for endpoint '{endpoint.name}'",
                                context={
                                    **endpoint_context,
                                    "available_collections": [c.name for c in bpy.data.collections]
                                },
                                recoverable=True
                            )
                            failed_count += 1
                            continue

                        logger.log_step("collection_found", {
                            **endpoint_context,
                            "collection_objects": len(collection.objects)
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

                        # Use ScopedIsolation to safely isolate and export this endpoint
                        with state_manager.ScopedIsolation(context, collection) as isolation:
                            logger.log_step("isolation_started", endpoint_context)

                            # USD export parameters - based on Blender 5.0 research
                            # Note: Second opinion analysis suggests verifying these parameter names
                            # against bpy.ops.wm.usd_export.get_rna_type().properties for Blender 5.0
                            export_params = {
                                "filepath": filepath,
                                "collection": endpoint.collection_name,
                                "export_materials": True,
                                "export_uvmaps": True,
                                "export_normals": True,
                                "export_animation": False,
                                "root_prim_path": f"/{endpoint.name}",
                            }

                            logger.log_step("usd_export_start", {
                                **endpoint_context,
                                "export_params": export_params
                            })

                            # Call Blender's USD export operator
                            result = bpy.ops.wm.usd_export(**export_params)

                            if result == {"FINISHED"}:
                                exported_count += 1
                                logger.log_step("usd_export_success", {
                                    **endpoint_context,
                                    "file_size_bytes": self._get_file_size(filepath)
                                })
                                self.report({"INFO"}, f"Successfully exported '{endpoint.name}' to '{filepath}'.")
                            else:
                                failed_count += 1
                                logger.log_error(
                                    f"USD export operator failed for endpoint '{endpoint.name}'",
                                    context={**endpoint_context, "operator_result": str(result)},
                                    recoverable=True
                                )
                                self.report({"ERROR"}, f"Failed to export '{endpoint.name}'.")

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


__all__ = ["USDME_OT_export_endpoints"]


