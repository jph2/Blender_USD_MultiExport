# Blender USD Multi Export - Logging Utilities
"""
Comprehensive logging utilities for debugging and bug reporting.

Provides:
- Verbose mode toggle
- Detailed operation logging with timestamps
- System/environment info collection
- Export operation step tracking
- Error context and actionable advice
- File rotation for persistent logging
- Context tracking for nested operations
- Performance timers for operation profiling
"""

import bpy
import datetime
import logging
import logging.handlers
import platform
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List


class USDME_Logger:
    """Centralized logging utility for USD Multi Export operations."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.log_entries: List[Dict[str, Any]] = []
        self.operation_start_time: Optional[datetime.datetime] = None
        self.current_operation: Optional[str] = None
        self.context_stack: List[str] = []  # Context tracking for nested operations
        self.timers: Dict[str, float] = {}  # Performance timers
        
        # Setup Python logging with file rotation
        self._setup_python_logging()

    def _setup_python_logging(self):
        """Setup Python logging with file rotation and console handler."""
        self.python_logger = logging.getLogger('blender_usd_multiexport')
        self.python_logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.python_logger.handlers:
            return
        
        # Create formatters
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        self.console_formatter = logging.Formatter(
            '[blender_usd_multiexport:%(levelname)s] %(message)s'
        )
        
        # Setup file handler with rotation
        self.file_handler = self._setup_file_handler()
        self.python_logger.addHandler(self.file_handler)
        
        # Setup console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)  # Default console level
        self.console_handler.setFormatter(self.console_formatter)
        self.python_logger.addHandler(self.console_handler)
    
    def _setup_file_handler(self) -> logging.Handler:
        """Setup rotating file handler for persistent logging."""
        try:
            # Get Blender's temp directory (guaranteed in Blender 5.0+)
            temp_dir = Path(bpy.app.tempdir)
            log_dir = temp_dir / "blender_usd_logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / "blender_usd_multiexport.log"
            
            # Rotating file handler (max 5MB, keep 3 backups)
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
            )
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(self.file_formatter)
            
            return handler
        except Exception as e:
            # Fallback if file logging fails
            print(f"Warning: Failed to setup file logging: {e}")
            return logging.NullHandler()
    
    def set_console_level(self, level: str) -> None:
        """Set console logging level. Options: DEBUG, INFO, WARNING, ERROR"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.console_handler.setLevel(level_map[level.upper()])
            self.python_logger.debug(f"Console log level set to: {level.upper()}")
        else:
            self.python_logger.warning(f"Invalid log level: {level}. Using INFO.")
            self.console_handler.setLevel(logging.INFO)
    
    def set_verbose(self, verbose: bool):
        """Enable or disable verbose logging."""
        self.verbose = verbose
        if verbose:
            self.set_console_level('DEBUG')
        else:
            self.set_console_level('INFO')
    
    def push_context(self, context: str) -> None:
        """Push a context onto the stack for nested logging."""
        self.context_stack.append(context)
        self.debug(f"Entering context: {context}")
    
    def pop_context(self) -> Optional[str]:
        """Pop a context from the stack."""
        if self.context_stack:
            context = self.context_stack.pop()
            self.debug(f"Exiting context: {context}")
            return context
        return None
    
    def start_timer(self, name: str) -> None:
        """Start a performance timer."""
        self.timers[name] = time.time()
        self.debug(f"Started timer: {name}")
    
    def end_timer(self, name: str) -> float:
        """End a performance timer and return elapsed time."""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            self.debug(f"Timer {name}: {elapsed:.3f}s")
            del self.timers[name]
            return elapsed
        else:
            self.warning(f"Timer '{name}' was not started")
            return 0.0
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message with optional extra context."""
        self._log_with_context(logging.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with optional extra context."""
        self._log_with_context(logging.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with optional extra context."""
        self._log_with_context(logging.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message with optional extra context."""
        self._log_with_context(logging.ERROR, message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log critical message with optional extra context."""
        self._log_with_context(logging.CRITICAL, message, extra)
    
    def _log_with_context(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log message with current context information."""
        # Add context to message if available
        context_prefix = ""
        if self.context_stack:
            context_prefix = f"[{self.context_stack[-1]}] "
        
        full_message = f"{context_prefix}{message}"
        
        # Add extra context if provided
        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            full_message = f"{full_message} ({extra_str})"
        
        # Log to Python logger
        self.python_logger.log(level, full_message)
        
        # Also log to internal log_entries for bug reports
        self._log_internal(level, full_message, extra)

    def start_operation(self, operation_name: str, context_info: Optional[Dict[str, Any]] = None):
        """Start tracking a major operation."""
        self.operation_start_time = datetime.datetime.now()
        self.current_operation = operation_name
        self.log_entries = []  # Reset for new operation
        
        # Push context for nested logging
        self.push_context(operation_name)

        self.info(f"Started operation: {operation_name}", context_info)
        
        # Start performance timer
        self.start_timer(operation_name)

        if self.verbose:
            self._log_system_info()
            if context_info:
                self._log_context_info(context_info)

    def end_operation(self, success: bool = True, result_info: Optional[Dict[str, Any]] = None):
        """End tracking of the current operation."""
        if not self.operation_start_time or not self.current_operation:
            return

        # End performance timer
        elapsed = self.end_timer(self.current_operation)
        
        duration = datetime.datetime.now() - self.operation_start_time
        status = "SUCCESS" if success else "FAILED"
        
        # Add timer info to result
        if result_info is None:
            result_info = {}
        result_info["timer_elapsed_seconds"] = elapsed

        self.info(f"Completed operation: {self.current_operation} ({status}) - Duration: {duration} ({elapsed:.3f}s)", result_info)
        
        # Pop context
        self.pop_context()

        # Reset
        self.operation_start_time = None
        self.current_operation = None

    def log_step(self, step_name: str, details: Optional[Dict[str, Any]] = None, level: str = "INFO"):
        """Log a specific step in the current operation."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        log_level = level_map.get(level.upper(), logging.INFO)
        
        if not self.current_operation:
            self._log_with_context(log_level, f"Step: {step_name}", details)
            return

        context = {"operation": self.current_operation, "step": step_name}
        if details:
            context.update(details)

        self._log_with_context(log_level, f"[{self.current_operation}] {step_name}", context)

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
            import traceback
            error_context["traceback"] = traceback.format_exc()
            error_context["exception_details"] = {
                "message": str(exception),
                "type": type(exception).__name__,
                "module": getattr(exception, '__module__', 'builtins')
            }

        self.error(error_msg, error_context)

    def log_warning(self, warning_msg: str, suggestion: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None):
        """Log a warning with optional suggestion."""
        warning_context = {}
        if suggestion:
            warning_context["suggestion"] = suggestion
        if context:
            warning_context.update(context)

        self.warning(warning_msg, warning_context)

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

    def _log_internal(self, level: int, message: str, context: Optional[Dict[str, Any]] = None):
        """Internal logging method for bug report data."""
        level_name = logging.getLevelName(level)
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": level_name,
            "message": message,
            "context": context or {}
        }

        self.log_entries.append(entry)
    
    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Legacy logging method - redirects to new logging system."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        log_level = level_map.get(level.upper(), logging.INFO)
        self._log_with_context(log_level, message, context)

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


def setup_logging(console_level: str = "INFO") -> USDME_Logger:
    """Initialize the logging system with specified console level."""
    logger_instance = get_logger()
    logger_instance.set_console_level(console_level)
    logger_instance.info("USD Multi Export logging system initialized")
    return logger_instance


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
