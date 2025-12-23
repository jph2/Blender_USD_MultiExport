# Blender USD Multi Export - Logging Utilities
"""
Comprehensive logging utilities for debugging and bug reporting.

Provides:
- Verbose mode toggle
- Detailed operation logging with timestamps
- System/environment info collection
- Export operation step tracking
- Error context and actionable advice
"""

import bpy
import datetime
import platform
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List


class USDME_Logger:
    """Centralized logging utility for USD Multi Export operations."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.log_entries: List[Dict[str, Any]] = []
        self.operation_start_time: Optional[datetime.datetime] = None
        self.current_operation: Optional[str] = None

    def set_verbose(self, verbose: bool):
        """Enable or disable verbose logging."""
        self.verbose = verbose

    def start_operation(self, operation_name: str, context_info: Optional[Dict[str, Any]] = None):
        """Start tracking a major operation."""
        self.operation_start_time = datetime.datetime.now()
        self.current_operation = operation_name
        self.log_entries = []  # Reset for new operation

        self._log("INFO", f"Started operation: {operation_name}", context_info)

        if self.verbose:
            self._log_system_info()
            if context_info:
                self._log_context_info(context_info)

    def end_operation(self, success: bool = True, result_info: Optional[Dict[str, Any]] = None):
        """End tracking of the current operation."""
        if not self.operation_start_time or not self.current_operation:
            return

        duration = datetime.datetime.now() - self.operation_start_time
        status = "SUCCESS" if success else "FAILED"

        self._log("INFO", f"Completed operation: {self.current_operation} ({status}) - Duration: {duration}", result_info)

        # Reset
        self.operation_start_time = None
        self.current_operation = None

    def log_step(self, step_name: str, details: Optional[Dict[str, Any]] = None, level: str = "INFO"):
        """Log a specific step in the current operation."""
        if not self.current_operation:
            self._log(level, f"Step: {step_name}", details)
            return

        context = {"operation": self.current_operation, "step": step_name}
        if details:
            context.update(details)

        self._log(level, f"[{self.current_operation}] {step_name}", context)

    def log_error(self, error_msg: str, exception: Optional[Exception] = None,
                  context: Optional[Dict[str, Any]] = None, recoverable: bool = True):
        """Log an error with full context for bug reporting."""
        error_context = {
            "error_type": type(exception).__name__ if exception else "Unknown",
            "recoverable": recoverable,
            "blender_version": self._get_blender_version(),
            "scene_info": self._get_scene_info()
        }

        if context:
            error_context.update(context)

        if exception:
            error_context["traceback"] = str(exception)
            error_context["exception_details"] = {
                "message": str(exception),
                "type": type(exception).__name__,
                "module": getattr(exception, '__module__', 'builtins')
            }

        self._log("ERROR", error_msg, error_context)

        # In verbose mode, also log to Blender console for immediate visibility
        if self.verbose:
            print(f"[USDME ERROR] {error_msg}")
            if exception:
                print(f"[USDME ERROR] Exception: {exception}")

    def log_warning(self, warning_msg: str, suggestion: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None):
        """Log a warning with optional suggestion."""
        warning_context = {}
        if suggestion:
            warning_context["suggestion"] = suggestion
        if context:
            warning_context.update(context)

        self._log("WARNING", warning_msg, warning_context)

    def get_bug_report_data(self) -> Dict[str, Any]:
        """Generate comprehensive bug report data."""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "blender_info": self._get_blender_info(),
            "addon_info": self._get_addon_info(),
            "scene_info": self._get_scene_info(),
            "operation_log": self.log_entries[-50:],  # Last 50 entries
            "recent_errors": [entry for entry in self.log_entries[-20:] if entry.get("level") == "ERROR"]
        }

    def export_log_to_file(self, filepath: str) -> bool:
        """Export the current log to a file for bug reporting."""
        try:
            import json

            log_data = {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "bug_report_data": self.get_bug_report_data()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Failed to export log to {filepath}: {e}")
            return False

    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Internal logging method."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }

        self.log_entries.append(entry)

        # Always report to Blender's info system for user visibility
        # Note: bpy.ops.wm.report_message doesn't exist; using print for console output
        # In operator contexts, use self.report() instead

        # In verbose mode, also print to console
        if self.verbose:
            print(f"[USDME {level}] {message}")
            if context:
                for key, value in context.items():
                    print(f"  {key}: {value}")

    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_path": sys.executable
        }

    def _get_blender_info(self) -> Dict[str, Any]:
        """Get Blender-specific information."""
        return {
            "version": self._get_blender_version(),
            "build_info": bpy.app.build_info if hasattr(bpy.app, 'build_info') else "N/A",
            "binary_path": bpy.app.binary_path,
            "tempdir": bpy.app.tempdir
        }

    def _get_blender_version(self) -> str:
        """Get formatted Blender version string."""
        version = bpy.app.version
        return f"{version[0]}.{version[1]}.{version[2]}"

    def _get_addon_info(self) -> Dict[str, Any]:
        """Get addon-specific information."""
        try:
            addon_module = sys.modules.get('blender_usd_multiexport')
            if addon_module and hasattr(addon_module, 'bl_info'):
                return dict(addon_module.bl_info)
        except:
            pass
        return {"error": "Could not retrieve addon info"}

    def _get_scene_info(self) -> Dict[str, Any]:
        """Get current scene information."""
        try:
            scene = bpy.context.scene
            return {
                "name": scene.name,
                "filepath": bpy.data.filepath or "unsaved",
                "frame_current": scene.frame_current,
                "frame_start": scene.frame_start,
                "frame_end": scene.frame_end,
                "objects_count": len(scene.objects),
                "collections_count": len(bpy.data.collections),
                "materials_count": len(bpy.data.materials),
                "usdme_endpoints_count": len(scene.usdme_settings.endpoints) if hasattr(scene, 'usdme_settings') else 0
            }
        except:
            return {"error": "Could not retrieve scene info"}

    def _log_system_info(self):
        """Log comprehensive system information in verbose mode."""
        if not self.verbose:
            return

        sys_info = self._get_system_info()
        bpy_info = self._get_blender_info()
        scene_info = self._get_scene_info()

        self._log("INFO", "System Information:", sys_info)
        self._log("INFO", "Blender Information:", bpy_info)
        self._log("INFO", "Scene Information:", scene_info)

    def _log_context_info(self, context: Dict[str, Any]):
        """Log operation context information."""
        self._log("INFO", "Operation Context:", context)


# Global logger instance
logger = USDME_Logger()


def get_logger() -> USDME_Logger:
    """Get the global logger instance."""
    return logger


def set_verbose_logging(verbose: bool):
    """Enable or disable verbose logging globally."""
    logger.set_verbose(verbose)


def log_bug_report():
    """Generate and save a bug report log file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = str(Path(bpy.app.tempdir) / f"usdme_bug_report_{timestamp}.json")

    if logger.export_log_to_file(filepath):
        print(f"[USDME INFO] Bug report saved to: {filepath}")
        return filepath
    else:
        print("[USDME ERROR] Failed to save bug report log file")
        return None


def validate_usd_export_params():
    """
    Validate USD export operator parameters for the current Blender version.

    Returns:
        dict: Information about parameter validation
    """
    try:
        # Try to get the operator's RNA properties
        rna_props = bpy.ops.wm.usd_export.get_rna_type().properties
        param_names = [prop.identifier for prop in rna_props]

        # Check for our commonly used parameters
        expected_params = [
            'filepath', 'collection', 'export_materials', 'export_uvmaps',
            'export_normals', 'export_animation', 'root_prim_path'
        ]

        found_params = [param for param in expected_params if param in param_names]
        missing_params = [param for param in expected_params if param not in param_names]

        return {
            "validation_successful": True,
            "total_params_found": len(param_names),
            "expected_params_found": found_params,
            "expected_params_missing": missing_params,
            "all_expected_found": len(missing_params) == 0
        }
    except Exception as e:
        return {
            "validation_successful": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


__all__ = ["USDME_Logger", "get_logger", "set_verbose_logging", "log_bug_report", "validate_usd_export_params"]
