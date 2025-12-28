# Blender USD Multi Export - Path Resolution Utilities
"""
Cross-platform path handling for USD export operations.

Provides:
- Relative path storage and absolute path resolution
- Directory auto-creation
- Cross-platform compatibility using bpy.path utilities
- Path validation and error handling
"""

import os
import bpy
from pathlib import Path
from typing import Optional, Dict, Any, List
from . import logging_utils


class PathResolver:
    """
    Handles path resolution for USD export operations.

    Stores paths relative to blend files and resolves them to absolute paths
    using Blender's cross-platform path utilities.
    """

    def __init__(self):
        self.logger = logging_utils.get_logger()

    def resolve_export_path(self, relative_path: str, create_directories: bool = True) -> Optional[str]:
        """
        Resolve a relative path to an absolute path for USD export.

        Args:
            relative_path: Path relative to blend file (e.g., "//export/asset.usd" or "./export/asset.usd")
            create_directories: Whether to create parent directories if they don't exist

        Returns:
            Absolute path string, or None if resolution fails
        """
        try:
            self.logger.log_step("path_resolution_start", {
                "input_path": relative_path,
                "create_directories": create_directories
            })

            # Validate input
            if not relative_path or not isinstance(relative_path, str):
                self.logger.log_error(
                    "Invalid path provided to PathResolver",
                    context={"path": relative_path, "type": type(relative_path).__name__}
                )
                return None

            # Convert ./ paths to // paths (relative to blend file)
            # bpy.path.abspath() doesn't handle ./ correctly - it uses current working directory
            # So we convert ./ to // which means "relative to blend file"
            if relative_path.startswith("./"):
                # Remove ./ prefix and convert to Blender's // format
                converted_path = "//" + relative_path[2:]
                self.logger.log_step("path_converted", {
                    "original": relative_path,
                    "converted": converted_path
                })
                relative_path = converted_path

            # Use Blender's cross-platform path resolution
            absolute_path = bpy.path.abspath(relative_path)

            # Clean up the path (remove redundant separators, resolve . and ..)
            absolute_path = os.path.normpath(absolute_path)

            # Ensure the path uses forward slashes for consistency
            absolute_path = absolute_path.replace('\\', '/')

            self.logger.log_step("path_resolved", {
                "input_path": relative_path,
                "resolved_path": absolute_path,
                "exists": os.path.exists(absolute_path)
            })

            # Create parent directories if requested
            if create_directories:
                parent_dir = os.path.dirname(absolute_path)
                if parent_dir and not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                        self.logger.log_step("directory_created", {"path": parent_dir})
                    except (OSError, PermissionError) as e:
                        self.logger.log_error(
                            f"Failed to create directory: {parent_dir}",
                            exception=e,
                            context={"directory": parent_dir}
                        )
                        return None

            # Validate final path
            if not self._validate_path(absolute_path):
                return None

            return absolute_path

        except Exception as e:
            self.logger.log_error(
                "Path resolution failed",
                exception=e,
                context={"input_path": relative_path}
            )
            return None

    def validate_export_path(self, path: str) -> Dict[str, Any]:
        """
        Validate an export path and return detailed information.

        Args:
            path: The path to validate (relative or absolute)

        Returns:
            Dict with validation results and recommendations
        """
        result = {
            "is_valid": False,
            "path_type": "unknown",
            "exists": False,
            "parent_exists": False,
            "is_writable": False,
            "recommendations": [],
            "warnings": [],
            "errors": []
        }

        try:
            # Determine path type
            if path.startswith("//"):
                result["path_type"] = "blender_relative"
            elif os.path.isabs(path):
                result["path_type"] = "absolute"
            else:
                result["path_type"] = "relative"

            # Resolve to absolute path
            absolute_path = self.resolve_export_path(path, create_directories=False)
            if not absolute_path:
                result["errors"].append("Path resolution failed")
                return result

            result["resolved_path"] = absolute_path

            # Check existence
            result["exists"] = os.path.exists(absolute_path)
            result["parent_exists"] = os.path.exists(os.path.dirname(absolute_path))

            # Check writability
            parent_dir = os.path.dirname(absolute_path)
            if parent_dir:
                result["is_writable"] = os.access(parent_dir, os.W_OK)
            else:
                result["is_writable"] = os.access(os.getcwd(), os.W_OK)

            # Validate based on file extension
            if not path.lower().endswith(('.usd', '.usda', '.usdc', '.usdz')):
                result["warnings"].append("File extension should be .usd, .usda, .usdc, or .usdz")

            # Generate recommendations
            if not result["parent_exists"]:
                result["recommendations"].append("Parent directory will be created automatically")
            if not result["is_writable"]:
                result["errors"].append("Parent directory is not writable")
            if result["exists"]:
                result["warnings"].append("File already exists and will be overwritten")

            # Overall validity
            result["is_valid"] = (
                bool(absolute_path) and
                result["is_writable"] and
                len(result["errors"]) == 0
            )

        except Exception as e:
            result["errors"].append(f"Validation failed: {str(e)}")

        return result

    def get_relative_path(self, absolute_path: str, relative_to_blend: bool = True) -> Optional[str]:
        """
        Convert an absolute path to a relative path.

        Args:
            absolute_path: Absolute path to convert
            relative_to_blend: If True, make relative to blend file; if False, make relative to current working directory

        Returns:
            Relative path string, or None if conversion fails
        """
        try:
            if relative_to_blend:
                # Use Blender's relative path function
                return bpy.path.relpath(absolute_path)
            else:
                # Make relative to current working directory
                return os.path.relpath(absolute_path, os.getcwd())

        except Exception as e:
            self.logger.log_error(
                "Failed to create relative path",
                exception=e,
                context={"absolute_path": absolute_path, "relative_to_blend": relative_to_blend}
            )
            return None

    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory

        Returns:
            True if directory exists or was created successfully
        """
        try:
            if not directory_path:
                return False

            # Resolve relative paths if needed
            if not os.path.isabs(directory_path):
                directory_path = self.resolve_export_path(directory_path, create_directories=False)
                if not directory_path:
                    return False

            # Get directory path (in case a file path was provided)
            dir_path = os.path.dirname(directory_path) if os.path.isfile(directory_path) else directory_path

            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                self.logger.log_step("directory_created", {"path": dir_path})

            return os.path.exists(dir_path)

        except Exception as e:
            self.logger.log_error(
                "Failed to create directory",
                exception=e,
                context={"directory_path": directory_path}
            )
            return False

    def get_safe_filename(self, filename: str, directory: str = "") -> str:
        """
        Generate a safe filename by cleaning invalid characters and avoiding conflicts.

        Args:
            filename: Desired filename
            directory: Directory to check for conflicts

        Returns:
            Safe filename string
        """
        try:
            # Remove or replace invalid characters
            safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
            safe_name = safe_name.strip()

            # Ensure it has a valid extension
            if not safe_name.lower().endswith(('.usd', '.usda', '.usdc', '.usdz')):
                safe_name += '.usd'

            # Avoid conflicts by adding number if file exists
            if directory:
                full_path = os.path.join(directory, safe_name)
                if os.path.exists(full_path):
                    base, ext = os.path.splitext(safe_name)
                    counter = 1
                    while os.path.exists(os.path.join(directory, f"{base}_{counter}{ext}")):
                        counter += 1
                    safe_name = f"{base}_{counter}{ext}"

            return safe_name

        except Exception as e:
            self.logger.log_error(
                "Failed to generate safe filename",
                exception=e,
                context={"filename": filename, "directory": directory}
            )
            return f"export.usd"  # Fallback

    def _validate_path(self, path: str) -> bool:
        """
        Validate a resolved path for basic correctness.

        Args:
            path: The path to validate

        Returns:
            True if path is valid for USD export
        """
        if not path:
            return False

        # Check for invalid characters in path
        invalid_chars = ['<', '>', '|', '"', '*', '?']
        if any(char in path for char in invalid_chars):
            self.logger.log_warning(
                f"Path contains invalid characters: {path}",
                suggestion="Avoid using < > | \" * ? in file paths"
            )
            return False

        # Check path length (some systems have limits)
        if len(path) > 260:  # Common Windows limit
            self.logger.log_warning(
                f"Path is very long ({len(path)} chars): {path}",
                suggestion="Consider using shorter directory names"
            )

        # Ensure parent directory is accessible
        parent_dir = os.path.dirname(path)
        if parent_dir and os.path.exists(parent_dir):
            if not os.access(parent_dir, os.W_OK):
                self.logger.log_error(
                    f"Parent directory is not writable: {parent_dir}",
                    context={"path": path}
                )
                return False

        return True

    def get_project_export_directory(self, blend_file_path: Optional[str] = None) -> str:
        """
        Get the recommended export directory for the current project.

        Args:
            blend_file_path: Path to blend file (uses current if None)

        Returns:
            Recommended export directory path
        """
        try:
            if blend_file_path is None:
                blend_file_path = bpy.data.filepath

            if blend_file_path:
                # Use blend file directory + "export" subdirectory
                blend_dir = os.path.dirname(blend_file_path)
                export_dir = os.path.join(blend_dir, "export")
                return self.get_relative_path(export_dir, relative_to_blend=True)
            else:
                # No blend file saved, use relative path
                return "//export"

        except Exception as e:
            self.logger.log_error(
                "Failed to determine project export directory",
                exception=e
            )
            return "//export"  # Fallback


# Global path resolver instance
path_resolver = PathResolver()


def get_path_resolver() -> PathResolver:
    """Get the global path resolver instance."""
    return path_resolver


def resolve_export_path(relative_path: str, create_directories: bool = True) -> Optional[str]:
    """
    Convenience function to resolve an export path.

    Args:
        relative_path: Path relative to blend file
        create_directories: Whether to create parent directories

    Returns:
        Absolute path string, or None if resolution fails
    """
    return path_resolver.resolve_export_path(relative_path, create_directories)


def validate_export_path(path: str) -> Dict[str, Any]:
    """
    Convenience function to validate an export path.

    Args:
        path: The path to validate

    Returns:
        Dict with validation results
    """
    return path_resolver.validate_export_path(path)


__all__ = ["PathResolver", "get_path_resolver", "resolve_export_path", "validate_export_path"]
