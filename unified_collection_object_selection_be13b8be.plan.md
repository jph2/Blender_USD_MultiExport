---
name: Bug Fixes and Feature Enhancements
overview: Fix critical TypeError bug in object isolation, improve UI with labels and spacing, add filepath subfolder feature, and implement origin metadata tracking in USD files.
todos:
  - id: fix_typeerror_bug
    content: Fix TypeError in state_manager.py line 95 - use obj.name instead of obj for view_layer.objects membership check
    status: pending
  - id: ui_labels_spacing
    content: Add visible labels to all fields and increase horizontal space for long collection/object names using scale_x
    status: pending
  - id: filepath_subfolder
    content: Add create_subfolder checkbox property and implement subfolder creation logic (USD_Endpoint_[name])
    status: pending
  - id: origin_metadata
    content: Add include_origin_metadata checkbox and implement USD custom attributes for origin tracking
    status: pending
  - id: data_model
    content: "Update props.py: Add endpoint_type enum, object_name property, include_subcollections flag"
    status: pending
  - id: ui_type_selector
    content: Add type selector dropdown in UI with Collection/Object options
    status: pending
    dependencies:
      - data_model
  - id: ui_conditional_selectors
    content: Implement conditional collection/object selectors that show/hide based on type
    status: pending
    dependencies:
      - data_model
      - ui_type_selector
  - id: ui_subcollection_toggle
    content: Add include_subcollections checkbox (visible only for Collection type)
    status: pending
    dependencies:
      - data_model
      - ui_type_selector
  - id: update_autodetection
    content: Update add_endpoint operator to detect object vs collection and set type accordingly
    status: pending
    dependencies:
      - data_model
  - id: update_validation
    content: Update pre-flight and per-endpoint validation to handle both collection and object types
    status: pending
    dependencies:
      - data_model
  - id: update_export_logic
    content: Update export loop to get target based on endpoint_type and pass to ScopedIsolation
    status: pending
    dependencies:
      - data_model
      - update_validation
  - id: update_state_manager
    content: Update _get_collection_objects_recursive to support include_subcollections flag
    status: pending
    dependencies:
      - data_model
  - id: research_usd_export
    content: Research Blender 5.0 USD export operator to confirm object-level export support
    status: pending
  - id: remove_autocreation
    content: Remove or disable automatic collection creation button/functionality
    status: pending
---

# Bug Fixes and Feature Enhancements - Implementation Plan

## Overview

This plan addresses:
1. **Critical Bug Fix**: TypeError in object isolation (state_manager.py)
2. **UI Improvements**: Labels and spacing for long names (REQ-UI-009)
3. **Filepath Subfolder Feature**: Auto-create USD_Endpoint subfolder (REQ-EXP-008)
4. **Origin Metadata Feature**: Track origin file information in USD (REQ-EXP-009)

## Current State Analysis

### What's Implemented

- **Data Model**: `USDME_EndpointPropertyGroup` only has `collection_name` (StringProperty)
- **UI**: Collection selector using `prop_search` (flat list, no hierarchy indication)
- **Export Logic**: Only handles collections via `bpy.data.collections.get()`
- **Isolation**: `ScopedIsolation` already supports both Collection and Object types (lines 103-108 in `state_manager.py`)
- **Sub-collection Handling**: Currently recursively includes all child collections (no option to exclude)

### What's Missing

- Endpoint type indication (collection vs object)
- Object selection support in data model and UI
- Type-aware export logic
- Visual indication of selected type
- Sub-collection include/exclude option

## Requirements Summary

### From Conversation

1. **Unified Selector**: Single selector that can pick collections OR objects
2. **Type Indication**: Clear visual indication of what's selected (collection vs object)
3. **Three Selection Types**:

- Entire collection (with sub-collections)
- Sub-collection (with option to include/exclude parent)
- Single object

4. **Remove Auto-Creation**: Remove or make optional the automatic collection creation feature

### From Requirements Document

- **REQ-UI-002**: Tree view option for hierarchical structures (future enhancement)
- **REQ-EXP-001**: Export options per endpoint (already planned)

## Implementation Plan

### Phase 1: Data Model Updates

**File**: `blender_usd_multiexport_addon/props.py`

1. **Add Endpoint Type Enum**:
   ```python
         endpoint_type: EnumProperty(
             name="Endpoint Type",
             description="Type of export target",
             items=[
                 ('COLLECTION', "Collection", "Export entire collection"),
                 ('OBJECT', "Object", "Export single object"),
             ],
             default='COLLECTION'
         )
   ```




2. **Add Object Name Property**:
   ```python
         object_name: StringProperty(
             name="Object",
             description="Name of the object used as export target",
             default="",
         )
   ```




3. **Keep Collection Name** (existing, but make conditional):

- Keep `collection_name` property
- Validation will check which property to use based on `endpoint_type`

4. **Add Sub-Collection Option** (for collection type):
   ```python
         include_subcollections: BoolProperty(
             name="Include Sub-collections",
             description="Include objects from child collections",
             default=True,
         )
   ```




### Phase 2: UI Updates

**File**: `blender_usd_multiexport_addon/ui.py`

1. **Add Type Selector** (before collection/object selector):

- Enum dropdown for `endpoint_type` (Collection/Object)
- Clear labels with icons

2. **Conditional Selectors**:

- **If Collection**: Show collection `prop_search` (existing)
- **If Object**: Show object `prop_search` using `bpy.data.objects`
- Hide the non-active selector

3. **Sub-Collection Toggle** (only for Collection type):

- Checkbox: "Include Sub-collections"
- Only visible when `endpoint_type == 'COLLECTION'`
- Default: `True` (current behavior)

4. **Visual Type Indicator**:

- Icon next to endpoint name showing type (collection icon vs object icon)
- Update validation indicators to show type-specific warnings

5. **Remove Auto-Creation Button**:

- Remove or disable `USDME_OT_create_collection_from_selected` button
- Or make it optional via preferences

### Phase 3: Export Logic Updates

**File**: `blender_usd_multiexport_addon/ops_export.py`

1. **Update Pre-flight Validation**:

- Check `endpoint_type`
- Validate `collection_name` if type is COLLECTION
- Validate `object_name` if type is OBJECT
- Check collection/object exists in scene

2. **Update Export Loop**:

- Get target based on `endpoint_type`:
    - COLLECTION: `bpy.data.collections.get(endpoint.collection_name)`
    - OBJECT: `bpy.data.objects.get(endpoint.object_name)`
- Pass correct target to `ScopedIsolation`

3. **Update ScopedIsolation Call**:

- Pass Collection object or Object object (not string)
- `ScopedIsolation` already handles both types

4. **Update USD Export Parameters**:

- For collections: Keep `collection` parameter
- For objects: May need different parameter or approach
- Research Blender 5.0 USD export operator for object export

5. **Update Logging Context**:

- Include `endpoint_type` in context
- Log which type is being exported

### Phase 4: State Manager Updates

**File**: `blender_usd_multiexport_addon/state_manager.py`

1. **Update `_get_collection_objects_recursive`**:

- Add parameter: `include_children: bool = True`
- If `include_children=False`, only return direct collection objects
- Used when `include_subcollections=False`

2. **Update `_get_target_objects`**:

- Handle `include_subcollections` flag for collections
- Pass flag to `_get_collection_objects_recursive`

### Phase 5: Auto-Detection Updates

**File**: `blender_usd_multiexport_addon/ui.py` (USDME_OT_add_endpoint)

1. **Update Auto-Detection Logic**:

- Check if single object is selected → set type to OBJECT, set `object_name`
- Check if collection is active → set type to COLLECTION, set `collection_name`
- Check if multiple objects selected → default to COLLECTION (or ask user?)

2. **Remove Auto-Creation**:

- Remove `_create_collection_from_selected` call
- Or make it optional/conditional

### Phase 6: Validation Updates

**File**: `blender_usd_multiexport_addon/ops_export.py`

1. **Type-Specific Validation**:

- COLLECTION: Check `collection_name` not empty, collection exists
- OBJECT: Check `object_name` not empty, object exists

2. **Update Error Messages**:

- Type-specific error messages
- Clear indication of what's missing (collection vs object)

3. **Update UI Validation Indicators**:

- Show different warnings for collection vs object
- Update completeness check to consider type

## Data Flow

```javascript
User selects endpoint type (Collection/Object)
    ↓
UI shows appropriate selector (collection prop_search OR object prop_search)
    ↓
User selects collection/object
    ↓
Validation checks type-specific property
    ↓
Export gets target (Collection or Object)
    ↓
ScopedIsolation receives Collection or Object
    ↓
Isolation handles both types (already implemented)
    ↓
USD export with appropriate parameters
```



## Files to Modify

1. **`blender_usd_multiexport_addon/props.py`**:

- Add `endpoint_type` EnumProperty
- Add `object_name` StringProperty
- Add `include_subcollections` BoolProperty

2. **`blender_usd_multiexport_addon/ui.py`**:

- Add type selector dropdown
- Add conditional collection/object selectors
- Add sub-collection toggle (conditional)
- Update auto-detection logic
- Remove/disable auto-creation button
- Update validation indicators

3. **`blender_usd_multiexport_addon/ops_export.py`**:

- Update pre-flight validation
- Update export loop to handle both types
- Update logging context

4. **`blender_usd_multiexport_addon/state_manager.py`**:

- Update `_get_collection_objects_recursive` to support `include_subcollections`
- Update `_get_target_objects` to pass flag

## Testing Considerations

1. **Collection Endpoint**:

- Select collection → exports correctly
- Select sub-collection → exports sub-collection only (if include_subcollections=False)
- Select sub-collection → exports sub-collection + children (if include_subcollections=True)

2. **Object Endpoint**:

- Select object → exports correctly
- Object with children → exports object hierarchy

3. **Validation**:

- Empty collection name (collection type) → shows error
- Empty object name (object type) → shows error
- Invalid collection/object name → shows error

4. **UI**:

- Type selector changes → appropriate selector appears
- Sub-collection toggle only visible for collections
- Visual indicators show correct type

## Open Questions

1. **Blender USD Export Operator**: Does `bpy.ops.wm.usd_export()` support object-level export, or only collection-level? (Needs research)
2. **Multiple Objects Selected**: When adding endpoint with multiple objects selected, should we:

- Default to creating a collection?
- Default to OBJECT type and use first selected?
- Ask user?

3. **Auto-Creation**: Should we remove entirely or make optional via preferences?

## Migration Considerations

- Existing endpoints will have `endpoint_type` defaulting to 'COLLECTION' (backward compatible)

---

## Phase 7: Critical Bug Fix

**File**: `blender_usd_multiexport_addon/state_manager.py`

**Issue**: TypeError at line 95 when checking object membership in view_layer.objects
- Error: `bpy_prop_collection.__contains__: expected a string or a tuple of strings`
- Cause: `view_layer.objects` expects string names, not object references
- Impact: Object-type endpoints fail to export

**Fix**:
```python
# Line 95 - Change from:
if obj in view_layer.objects:  # Safety check

# To:
if obj.name in view_layer.objects:  # Safety check
```

**Also check for similar issues**:
- Line 149: `if obj in view_layer.objects:` → `if obj.name in view_layer.objects:`
- Line 155: `if obj in view_layer.objects:` → `if obj.name in view_layer.objects:`
- Any other `obj in view_layer.objects` checks

## Phase 8: UI Improvements (REQ-UI-009)

**File**: `blender_usd_multiexport_addon/ui.py`

1. **Add Visible Labels**:
   - Ensure all fields have clear labels (Type, Collection, Object, Filepath)
   - Labels should be visible and associated with their fields

2. **Increase Field Width for Long Names**:
   ```python
   # For collection/object name fields:
   row_collection.prop_search(...)
   row_collection.scale_x = 2.0  # Give more horizontal space
   
   # For filepath field:
   row_filepath.prop(endpoint, "filepath", text="")
   row_filepath.scale_x = 2.0  # Give more horizontal space
   ```

3. **Improve Layout**:
   - Use split layouts if needed
   - Ensure names up to 100+ characters are visible

## Phase 9: Filepath Subfolder Feature (REQ-EXP-008)

**Files**: `blender_usd_multiexport_addon/props.py`, `blender_usd_multiexport_addon/ops_export.py`, `blender_usd_multiexport_addon/ui.py`

1. **Add Property** (`props.py`):
   ```python
   create_subfolder: BoolProperty(
       name="Create Subfolder",
       description="Create a subfolder named 'USD_Endpoint' with object/collection name in the file location",
       default=True,
   )
   ```

2. **Add UI Checkbox** (`ui.py`):
   ```python
   # After filepath field:
   row_subfolder = box.row(align=True)
   row_subfolder.prop(endpoint, "create_subfolder", text="Create Subfolder (USD_Endpoint/[name])")
   ```

3. **Implement Subfolder Logic** (`ops_export.py`):
   ```python
   # After filepath resolution, before export:
   if endpoint.create_subfolder:
       import os
       from pathlib import Path
       
       # Get target name
       target_name = endpoint.collection_name if endpoint.endpoint_type == 'COLLECTION' else endpoint.object_name
       
       # Create subfolder path
       file_dir = Path(filepath).parent
       subfolder_name = f"USD_Endpoint_{target_name}"
       subfolder_path = file_dir / subfolder_name
       subfolder_path.mkdir(parents=True, exist_ok=True)
       
       # Update filepath
       filename = Path(filepath).name
       filepath = str(subfolder_path / filename)
   ```

## Phase 10: Origin Metadata Feature (REQ-EXP-009)

**Files**: `blender_usd_multiexport_addon/props.py`, `blender_usd_multiexport_addon/ops_export.py`, `blender_usd_multiexport_addon/ui.py`

1. **Add Property** (`props.py`):
   ```python
   include_origin_metadata: BoolProperty(
       name="Include Origin Metadata",
       description="Add origin file information as custom attributes to root prim",
       default=True,
   )
   ```

2. **Add UI Checkbox** (`ui.py`):
   ```python
   # After filepath or in export options section:
   row_metadata = box.row(align=True)
   row_metadata.prop(endpoint, "include_origin_metadata", text="Include Origin Metadata")
   ```

3. **Implement Metadata Addition** (`ops_export.py`):
   ```python
   # After successful USD export:
   if endpoint.include_origin_metadata:
       try:
           from pxr import Usd, Sdf
           import getpass
           import socket
           from datetime import datetime
           import os
           
           stage = Usd.Stage.Open(filepath)
           root_prim = stage.GetPrimAtPath(f"/{endpoint.name}")
           
           if not root_prim.IsValid():
               root_prim = stage.GetDefaultPrim()
           
           if root_prim.IsValid():
               blend_filepath = bpy.data.filepath
               
               # Add custom attributes
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
               
               stage.Save()
       except ImportError:
           logger.log_warning("USD Python API (pxr) not available. Origin metadata not added.")
       except Exception as e:
           logger.log_error(f"Failed to add origin metadata: {e}")
   ```

## Updated Files to Modify

1. **`blender_usd_multiexport_addon/state_manager.py`**:
   - Fix TypeError: Use `obj.name` instead of `obj` for view_layer.objects checks

2. **`blender_usd_multiexport_addon/ui.py`**:
   - Add visible labels to all fields
   - Increase field width using `scale_x = 2.0`
   - Add create_subfolder checkbox
   - Add include_origin_metadata checkbox

3. **`blender_usd_multiexport_addon/props.py`**:
   - Add `create_subfolder` BoolProperty
   - Add `include_origin_metadata` BoolProperty

4. **`blender_usd_multiexport_addon/ops_export.py`**:
   - Implement subfolder creation logic
   - Implement origin metadata addition after export

## Testing Considerations

1. **Bug Fix**:
   - Object-type endpoints export successfully
   - No TypeError when checking object membership
   - Collection-type endpoints still work

2. **UI Improvements**:
   - All fields have visible labels
   - Long names (100+ chars) are fully visible
   - Layout is clean and readable

3. **Filepath Subfolder**:
   - Subfolder created when checkbox enabled
   - Subfolder name uses correct format: `USD_Endpoint_[name]`
   - File placed correctly (in subfolder or at filepath)
   - Works for both collection and object types

4. **Origin Metadata**:
   - All attributes added to root prim
   - Metadata preserved in binary USD
   - Graceful handling if pxr API unavailable
   - All origin information correctly captured