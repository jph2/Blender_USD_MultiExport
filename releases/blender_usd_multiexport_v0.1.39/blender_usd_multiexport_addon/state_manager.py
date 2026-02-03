# Blender USD Multi Export - State Management
"""
State management utilities for safe scene isolation during USD export operations.

This module provides:
- ScopedIsolation: Context manager for temporarily isolating collections/objects for export
- StateManager: Scene state management for batch export operations
"""

import bpy
from typing import Optional, Dict, List, Set, Any
from contextlib import contextmanager


class ScopedIsolation:
    """
    Context manager for temporarily isolating a specific collection or object for export.

    Safely caches current selection/visibility state, isolates the target start point,
    and guarantees state restoration even if an exception occurs during export.

    Usage:
        with ScopedIsolation(context, target_collection_or_object) as isolation:
            # Do export operations here
            # State will be restored automatically
            pass
    """

    def __init__(self, context: bpy.types.Context, target_start_point: Any, include_subcollections: bool = True):
        """
        Initialize the isolation context.

        Args:
            context: Blender context
            target_start_point: Collection or object to isolate for export
            include_subcollections: For collections, whether to include child collections (default: True)
        """
        self.context = context
        self.target_start_point = target_start_point
        self.include_subcollections = include_subcollections

        # State snapshots for restoration
        self._original_selection: Set[bpy.types.Object] = set()
        self._original_visibility: Dict[bpy.types.Object, bool] = {}
        self._original_active_object: Optional[bpy.types.Object] = None
        self._original_view_layer_objects: List[bpy.types.Object] = []

    def __enter__(self):
        """Enter the isolation context: cache state and isolate target."""
        self._cache_current_state()
        self._isolate_target()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the isolation context: restore original state."""
        self._restore_state()
        return False  # Don't suppress exceptions

    def _cache_current_state(self):
        """Cache the current scene state for later restoration."""
        scene = self.context.scene
        view_layer = self.context.view_layer

        # Cache active object
        self._original_active_object = view_layer.objects.active

        # Cache selection state
        self._original_selection = set(obj for obj in view_layer.objects if obj.select_get())

        # Cache visibility state (only for objects that exist in current view layer)
        self._original_visibility = {}
        for obj in view_layer.objects:
            self._original_visibility[obj] = obj.hide_viewport

        # Cache view layer objects list (in case it changes)
        self._original_view_layer_objects = list(view_layer.objects)

    def _isolate_target(self):
        """Isolate the target start point by hiding everything else and selecting only the target."""
        scene = self.context.scene
        view_layer = self.context.view_layer

        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')

        # Hide all objects in viewport (but preserve their original state for restoration)
        for obj in view_layer.objects:
            obj.hide_viewport = True

        # Determine what objects belong to the target start point
        target_objects = self._get_target_objects()

        # Unhide and select only the target objects
        for obj in target_objects:
            if obj.name in view_layer.objects:  # Safety check - use obj.name for bpy_prop_collection
                obj.hide_viewport = False
                obj.select_set(True)

        # Set the first target object as active (if any)
        if target_objects:
            view_layer.objects.active = target_objects[0]

    def _get_target_objects(self) -> List[bpy.types.Object]:
        """Get all objects that belong to the target start point."""
        if isinstance(self.target_start_point, bpy.types.Collection):
            # Return objects in the collection (with or without children based on flag)
            return self._get_collection_objects_recursive(self.target_start_point, self.include_subcollections)
        elif isinstance(self.target_start_point, bpy.types.Object):
            # Return the object and its children in the hierarchy
            return self._get_object_hierarchy(self.target_start_point)
        elif isinstance(self.target_start_point, str):
            # Treat as collection name
            collection = bpy.data.collections.get(self.target_start_point)
            if collection:
                return self._get_collection_objects_recursive(collection, self.include_subcollections)
        else:
            # Fallback: assume it's an object
            return []

    def _get_collection_objects_recursive(self, collection: bpy.types.Collection, include_children: bool = True) -> List[bpy.types.Object]:
        """Get all objects in a collection and optionally its child collections.
        
        Args:
            collection: The collection to get objects from
            include_children: If True, recursively include objects from child collections (default: True)
        """
        objects = []

        # Add objects directly in this collection
        objects.extend(collection.objects)

        # Recursively add objects from child collections if flag is set
        if include_children:
            for child_collection in collection.children:
                objects.extend(self._get_collection_objects_recursive(child_collection, include_children))

        return objects

    def _get_object_hierarchy(self, root_object: bpy.types.Object) -> List[bpy.types.Object]:
        """Get an object and all its children in the hierarchy."""
        objects = [root_object]

        def add_children(obj):
            for child in obj.children:
                objects.append(child)
                add_children(child)

        add_children(root_object)
        return objects

    def _restore_state(self):
        """Restore the original scene state."""
        view_layer = self.context.view_layer

        # Restore visibility state
        for obj, was_visible in self._original_visibility.items():
            try:
                # Check if object still exists and is valid before accessing its name
                if obj and obj.name in view_layer.objects:  # Safety check - use obj.name for bpy_prop_collection
                    obj.hide_viewport = was_visible
            except (ReferenceError, AttributeError):
                # Object was deleted, skip it
                continue

        # Clear selection and restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self._original_selection:
            try:
                # Check if object still exists and is valid before accessing its name
                if obj and obj.name in view_layer.objects:  # Safety check - use obj.name for bpy_prop_collection
                    obj.select_set(True)
            except (ReferenceError, AttributeError):
                # Object was deleted, skip it
                continue

        # Restore active object
        try:
            if self._original_active_object and self._original_active_object.name in view_layer.objects:
                view_layer.objects.active = self._original_active_object
        except (ReferenceError, AttributeError):
            # Active object was deleted, skip it
            pass


class StateManager:
    """
    Manages scene state for batch export operations.

    Handles backup/restore of scene state, state corruption recovery,
    and provides safe batch export workflow management.
    """

    def __init__(self, context: bpy.types.Context):
        """
        Initialize the state manager.

        Args:
            context: Blender context
        """
        self.context = context
        self._backup_states: List[Dict[str, Any]] = []
        self._corruption_recovery_enabled = True

    def create_backup(self) -> Dict[str, Any]:
        """
        Create a backup of the current scene state.

        Returns:
            Dict containing scene state snapshot
        """
        scene = self.context.scene
        view_layer = self.context.view_layer

        backup = {
            'active_object': view_layer.objects.active,
            'selected_objects': set(obj for obj in view_layer.objects if obj.select_get()),
            'visibility_states': {obj: obj.hide_viewport for obj in view_layer.objects},
            'view_layer_objects': list(view_layer.objects),
            'scene_render_engine': scene.render.engine,
            'scene_frame_current': scene.frame_current,
        }

        self._backup_states.append(backup)
        return backup

    def restore_backup(self, backup: Optional[Dict[str, Any]] = None) -> bool:
        """
        Restore scene state from backup.

        Args:
            backup: Specific backup to restore, or None for most recent

        Returns:
            True if restoration succeeded, False otherwise
        """
        if not self._backup_states and backup is None:
            return False

        if backup is None:
            backup = self._backup_states.pop()

        try:
            view_layer = self.context.view_layer

            # Restore visibility
            for obj, was_visible in backup['visibility_states'].items():
                if obj.name in view_layer.objects:  # Safety check - use obj.name for bpy_prop_collection
                    obj.hide_viewport = was_visible

            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in backup['selected_objects']:
                if obj.name in view_layer.objects:  # Safety check - use obj.name for bpy_prop_collection
                    obj.select_set(True)

            # Restore active object
            if backup['active_object'] and backup['active_object'].name in view_layer.objects:
                view_layer.objects.active = backup['active_object']

            # Restore other scene state
            self.context.scene.render.engine = backup['scene_render_engine']
            self.context.scene.frame_current = backup['scene_frame_current']

            return True

        except Exception as e:
            print(f"StateManager: Failed to restore backup: {e}")
            return False

    def clear_backups(self):
        """Clear all stored backup states."""
        self._backup_states.clear()

    def get_backup_count(self) -> int:
        """Get the number of stored backup states."""
        return len(self._backup_states)

    @contextmanager
    def safe_batch_operation(self):
        """
        Context manager for safe batch operations.

        Automatically creates backup on enter, restores on exit,
        and handles corruption recovery.
        """
        backup = None
        try:
            backup = self.create_backup()
            yield self
        except Exception as e:
            print(f"StateManager: Batch operation failed: {e}")
            if self._corruption_recovery_enabled and backup:
                print("StateManager: Attempting recovery...")
                self.restore_backup(backup)
            raise
        finally:
            if backup:
                self.restore_backup(backup)

    def validate_scene_integrity(self) -> bool:
        """
        Validate that the current scene state is consistent.

        Returns:
            True if scene state appears valid, False otherwise
        """
        try:
            scene = self.context.scene
            view_layer = self.context.view_layer

            # Basic checks
            if not scene:
                return False

            if not view_layer:
                return False

            # Check that all objects in view layer still exist
            for obj in view_layer.objects:
                if obj is None:
                    return False

            return True

        except Exception as e:
            print(f"StateManager: Scene integrity check failed: {e}")
            return False
