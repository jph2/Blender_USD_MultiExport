# Blender USD Stable Export - Detailed Requirements

**Status**: ✅ In Progress - Requirements being populated from confirmed questionnaire items  
**Date Created**: 25.11.2025  
**Version**: v2.5.1  
**Last Updated**: 02.02.2026 14:01 - v0.1.52 bake rotation fix documented  
**GlobalID**: 20260202_1401_Blender_USD_MultiExport_02  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)  
**Cross-Platform Pattern Reference**: `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`

---

## 📋 Requirements Status

This document contains detailed requirements derived from confirmed questionnaire responses and ASWF USD Working Group guidelines.

**Important**: All requirements must be compatible with **Blender 5.0+ only**. Blender 4.x versions are not supported.

**ASWF Compliance**: Requirements marked with ASWF references align with [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md) to ensure compatibility with VFX pipelines and Omniverse workflows. See `USD_ASSET_STRUCTURE_ANALYSIS.md` for detailed analysis.

**Perspective: Start Point (Pipeline Origin)**

The addon defines **start points** in the DCC—not "start points." A start point is the **stable origin in the DCC** for the downstream USD pipeline and composition arcs. Exported USD files are the **beginning** of further pipelining (references, layers, variants), not the terminus. Naming (start point, USD_StartPoint folder, etc.) reflects this pipeline-origin perspective.

**System Architecture: Push vs Pull Workflows**

**MVP Architecture: One-Way Push Model**

The MVP focuses on a **one-way push model** for ComfyUI integration:

**Push Phase (Blender Side)**:
- **Blender** exports USD files to predefined destinations via **start point** definitions (pipeline origins)
- Export happens independently in Blender (user-initiated or scripted)
- USD files are written to specified file paths
- **No ComfyUI involvement** in the export process

**Pull Phase (ComfyUI Side)**:
- **ComfyUI** reads the export path from **start point** definitions stored in .blend file
- ComfyUI nodes (e.g., BlenderToUSD) load pre-generated USD files from specified locations
- **Passive file loading** - ComfyUI does not trigger Blender exports
- USD files are consumed downstream in ComfyUI workflows

**Key Clarification**:
- ❌ **NOT MVP**: Bidirectional execution (ComfyUI driving Blender exports)
- ✅ **MVP**: One-way push (Blender exports → ComfyUI reads paths → ComfyUI loads files)
- 🔮 **Future**: Bidirectional execution could be added as enhancement

**Benefits of Push Model**:
- Simple, focused architecture
- No complex API integration required
- Clear separation of concerns
- Reliable file-based communication
- Easy to debug and validate

---

## Document Structure

### 1. Overview
- Project scope
- Objectives
- Success criteria

### 2. Functional Requirements
- Start point definition and management (pipeline origins)
- Export functionality
- User interface requirements
- Error handling

### 3. Non-Functional Requirements
- Performance requirements
- Compatibility requirements: **Blender 5.0+ only** (released November 18, 2025)
- Usability requirements
- Reliability requirements
- **Blender 5.0 USD Export Limitations**:
  - Only visible objects can be exported (no invisible object export)
  - No USD composition arcs authoring (layers, variants, references)
  - Experimental instancing support (use with caution)
  - No absolute shape keys in animation export
  - No bendy bones support in armatures

### 4. User Stories
- As a [user type], I want [feature] so that [benefit]

### 5. Acceptance Criteria
- For each requirement/user story

### 6. Priority Matrix
- Critical, High, Medium, Low priorities

### 7. Dependencies
- External dependencies
- Internal dependencies

---

## ✅ Confirmed Requirements (Pre-Questionnaire)

These requirements have been confirmed and do not require questionnaire validation:

### Start point Management Requirements

#### REQ-SP-001: Start points Saved with Blend File
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Start points MUST be saved with the .blend file as scene-specific data.

**Functional Requirements**:
- Start points are stored per-scene
- Start points persist when .blend file is saved and reopened
- Each scene can have its own set of start points

**Acceptance Criteria**:
- [ ] Start points are saved with .blend file
- [ ] Start points are restored when .blend file is reopened
- [ ] Different scenes can have different start point configurations

#### REQ-SP-002: Enable/Disable Toggle
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Start points MUST support enable/disable toggle to allow disabling start points without deleting them.

**Functional Requirements**:
- Each start point has an enabled/disabled state
- Disabled start points are skipped during export
- Start points can be toggled on/off without deletion

**Acceptance Criteria**:
- [ ] Start points have enable/disable toggle
- [ ] Disabled start points are skipped during export
- [ ] Start point state persists with .blend file

#### REQ-SP-007: Remove Start point with Selection
**Priority**: Medium  
**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Basic remove exists, dropdown selection NOT implemented  
**Date Added**: 28.12.2025  
**Implementation Status**: v0.1.0 MVP

**Requirement**: Users MUST be able to remove specific start points using a remove button with a dropdown list to select which start point to remove.

**Current Implementation (v0.1.0)**:
- ✅ Remove button exists in UI
- ✅ Removes last start point from list
- ✅ Operation supports UNDO
- ✅ Remove button works when start points exist
- ❌ **NOT IMPLEMENTED**: Dropdown list to select which start point to remove
- ❌ **NOT IMPLEMENTED**: Visual selection of start point before removal

**Functional Requirements**:
- Remove button with dropdown list showing all start points
- Dropdown displays start point names (and optionally type/collection/object for clarity)
- User can select which start point to remove from the dropdown
- Selected start point is removed from the scene
- Operation can be undone (UNDO support)
- If no start points exist, remove button is disabled or hidden

**Acceptance Criteria**:
- [x] Remove button exists (basic implementation)
- [x] Remove operation supports UNDO
- [x] Remove button works when start points exist
- [ ] Remove button has a dropdown list of start points
- [ ] Dropdown shows start point names clearly
- [ ] User can select and remove a specific start point (currently only removes last)
- [ ] Removed start point is properly cleaned up from scene data

**Implementation Notes**:
- Current code: `USDME_OT_remove_start point` in `ui.py` (lines 313-326)
- Currently removes: `settings.start points.remove(len(settings.start points) - 1)` (last start point only)
- **TODO for v0.2.0+**: Implement dropdown selection UI for start point removal

#### REQ-SP-003: Unified Collection/Object Selection
**Priority**: High  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Start points MUST support selecting either a collection (with sub-collections) or a single object as the export target, with clear visual indication of the selected type.

**Functional Requirements**:
- Each start point has a type selector (Collection or Object)
- Collection type: Select entire collection or sub-collection
- Object type: Select single object
- Clear visual indication of selected type (icon, label, or both)
- Type-specific selectors (collection dropdown for Collection type, object dropdown for Object type)
- Only the relevant selector is visible based on start point type
- Sub-collection inclusion option for Collection type (include/exclude child collections)

**Acceptance Criteria**:
- [ ] Start point type selector is available (Collection/Object)
- [ ] Collection selector appears when Collection type is selected
- [ ] Object selector appears when Object type is selected
- [ ] Visual indicator shows selected type (icon and/or label)
- [ ] Sub-collection toggle is available for Collection type
- [ ] Start point type persists with .blend file
- [ ] Auto-detection sets type based on selection (collection active → Collection type, object selected → Object type)

#### REQ-SP-005: Auto-Naming Start points
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Start point names MUST be automatically set to match the selected collection or object name.

**Functional Requirements**:
- When a collection is selected, start point name is automatically set to the collection name
- When an object is selected, start point name is automatically set to the object name
- Auto-naming occurs when collection_name or object_name property changes
- User can manually override the start point name if needed
- Auto-naming updates if the selected collection/object changes

**Acceptance Criteria**:
- [ ] Start point name automatically updates when collection is selected
- [ ] Start point name automatically updates when object is selected
- [ ] Auto-naming works for both Collection and Object type start points
- [ ] User can manually edit start point name to override auto-naming
- [ ] Start point name updates if collection/object selection changes

#### REQ-SP-006: Selection Tracking Button
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Each start point MUST have a "Select" button that allows users to track which start point belongs to which collection/object by selecting it in the viewport.

**Functional Requirements**:
- "Select" button available for each start point
- Button selects the collection/object in the viewport when clicked
- For Collection type: Selects all objects in the collection (and sub-collections if enabled)
- For Object type: Selects the object in the viewport
- Button provides visual feedback (icon, tooltip)
- Selection works even if start point is disabled

**Acceptance Criteria**:
- [ ] "Select" button is visible for each start point
- [ ] Clicking "Select" button selects the collection/object in viewport
- [ ] Collection selection includes all objects in collection (respects sub-collection setting)
- [ ] Object selection selects the specific object
- [ ] Button works for both enabled and disabled start points
- [ ] Visual feedback is provided (icon, tooltip)

#### REQ-SP-004: Sub-Collection Handling
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: When a collection start point is selected, users MUST be able to control whether sub-collections (child collections) are included in the export.

**Functional Requirements**:
- Toggle option: "Include Sub-collections" (default: enabled)
- When enabled: Export includes objects from selected collection AND all child collections recursively
- When disabled: Export includes only objects directly in the selected collection (excludes child collections)
- Option only visible/applicable for Collection type start points
- Option persists with start point configuration

**Acceptance Criteria**:
- [ ] "Include Sub-collections" toggle is available for Collection type start points
- [ ] Toggle defaults to enabled (current behavior)
- [ ] When enabled, child collections are included recursively
- [ ] When disabled, only direct collection objects are exported
- [ ] Toggle state persists with .blend file

### Export Functionality Requirements

#### REQ-EXP-001: Export Options Defaults
**Priority**: High  
**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Hardcoded defaults exist, per-start point options NOT implemented  
**Version**: v0.2.0+ (Planned)  
**Reference**: `09_Roadmap.md` - Comprehensive export options roadmap

**Requirement**: All USD export options MUST be available per start point, with sensible defaults based on common workflows.

**Current Implementation (v0.1.0)**:
- ✅ Hardcoded export defaults exist in `ops_export.py` (lines 338-346)
- ✅ Defaults include: `export_materials=True`, `export_uvmaps=True`, `export_normals=True`, `export_animation=False`, `export_lights=False`
- ✅ Root prim path generation (sanitized from start point name)
- ❌ **NOT IMPLEMENTED**: Per-start point export option overrides
- ❌ **NOT IMPLEMENTED**: UI for configuring export options per start point
- ❌ **NOT IMPLEMENTED**: Export options stored in start point properties

**Functional Requirements**:

**General Export Settings**:
- Forward Axis (default: Y)
- Up Axis (default: Z)
- Selection Only (default: False)
- Visible Only (default: True)
- Convert Orientation (default: True)
- Unit System (default: Use Scene Units) - See REQ-EXP-012 for details
- Create ARKit Asset (default: False)
- Relative Paths (default: True)
- Export As Overs (default: False)
- Merge Transform and Shape (default: True)
- Xform Ops order (default: Scale, Rotate, Translate)

**Stage Configuration**:
- Default Prim Path (default: `/root`)
- Root Prim Path (default: `/root`)
- Material Prim Path (default: `/root/materials`)
- Default Prim Kind (default: None)

**Export Type Selection**:
- Export Transforms (default: True)
- Export Meshes (default: True)
- Export Materials (default: True)
- Export Lights (default: False)
- Export Cameras (default: False)
- Export Curves (default: False)

**Geometry Options**:
- Subdivision Scheme (default: Best Match)
- Export Color Attributes (default: True)
- Export Mesh Attributes (default: True)
- Export Normals (default: True)
- Export UV Maps (default: True)
- Convert UV to ST (default: True)
- Triangulate Meshes (default: False)
- Quad Method (default: Shortest Diagonal)
- N-gon Method (default: Beauty)

**Material Export Options**:
- Generate Preview Surface (default: True)
- Export Cycles Shaders (default: False)
- Convert to MDL (default: False)
- Export Textures (default: True)
- Overwrite Textures (default: False)
- Use Original Texture Paths (default: False)
- USDZ Texture Downscale (default: Keep)
- USDZ Custom Downscale (default: 128)

**Light Export Options**:
- Light Intensity Scale (default: 1.0)
- Convert Light Units to Nits (default: True)
- Scale Light Radius (default: True)
- Convert World Material (default: True)

**Rigging Export Options**:
- Export Armatures (default: True)
- Only Deform Bones (default: False)
- Export Shape Keys (default: True)

**Animation Export Options**:
- Export Animation (default: False)
- Start Frame (default: 1)
- End Frame (default: 250)
- Frame Step (default: 1.0)

**Particles & Instancing**:
- Export Particles (default: True)
- Export Hair (default: True)
- Export Child Particles (default: False)

**Current Implementation (v0.1.0 MVP)**:
- Hardcoded export parameters in `ops_export.py` (lines 338-346):
  ```python
  export_params = {
      "filepath": filepath,
      "export_materials": True,      # Hardcoded
      "export_uvmaps": True,          # Hardcoded
      "export_normals": True,         # Hardcoded
      "export_animation": False,      # Hardcoded
      "export_lights": False,         # Hardcoded
      "root_prim_path": f"/{sanitized_name}",  # Generated from start point name
  }
  ```
- Additional per-start point options implemented:
  - `export_subdivision` (BoolProperty in `props.py` line 103)
  - `include_origin_metadata` (BoolProperty in `props.py` line 97)
- **NOT IMPLEMENTED**: All other export options are hardcoded and cannot be changed per start point

**Note**: Current v0.1.0 MVP has hardcoded defaults. Per-start point export options will be implemented in v0.2.0+ as per roadmap phases.

**Acceptance Criteria**:
- [ ] All export options are available per start point (v0.2.0+)
- [ ] Default values match common workflow needs
- [ ] Users can override defaults per start point
- [ ] Options are organized in logical UI sections
- [ ] Version-aware compatibility wrapper handles Blender 5.0 API changes

#### REQ-EXP-002: Export Presets
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Version**: v0.5.0+ (Planned)  
**Reference**: `09_Roadmap.md` Section 10 - Export Presets System

**Requirement**: The addon MUST support export presets (predefined and user-defined) to simplify common workflows.

**Functional Requirements**:
- Predefined presets:
  - **Default**: Balanced settings for general use
  - **Omniverse**: Optimized for NVIDIA Omniverse
  - **ARKit/USDZ**: Optimized for ARKit/USDZ export
  - **VFX Pipeline**: ASWF-compliant settings
  - **Game Engine**: Optimized for game engines
- User-defined presets (save/load from JSON or YAML)
- Presets can be applied to start points
- Preset inheritance: Start points can override preset values
- Preset management UI (create, edit, delete, import/export)

**Acceptance Criteria**:
- [ ] Predefined presets are available (v0.5.0+)
- [ ] Users can create custom presets
- [ ] Presets can be applied to start points
- [ ] Preset values can be overridden per start point
- [ ] Presets can be imported/exported as files
- [ ] Preset management UI is functional

#### REQ-EXP-003: Export Options Scope
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export options MUST support both global defaults and per-start point overrides.

**Functional Requirements**:
- Global default export settings
- Per-start point override capability
- Start points inherit global defaults unless overridden

**Acceptance Criteria**:
- [ ] Global default export settings exist
- [ ] Start points can override global defaults
- [ ] Override system works correctly

#### REQ-EXP-004: Batch Export Operations
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export MUST support batch operations with progress indication and cancellation.

**Functional Requirements**:
- Export multiple start points sequentially
- Progress indicator during batch export
- Ability to cancel batch export
- Export log/results display

**Acceptance Criteria**:
- [ ] Multiple start points can be exported in batch
- [ ] Progress indicator shows export progress
- [ ] Batch export can be cancelled
- [ ] Export results are logged

#### REQ-EXP-005: Export Validation
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export validation MUST be performed automatically in the background.

**Functional Requirements**:
- Check start point type is valid (Collection or Object)
- Check start point collection/object exists (type-specific validation)
- Check filepath is valid
- Check disk space available
- Check write permissions
- Validate exported USD file
- Check material/texture references
- All validation done automatically before export
- Type-specific error messages (collection not found vs object not found)

**Acceptance Criteria**:
- [ ] Start point type validation is performed
- [ ] Collection validation for Collection type start points
- [ ] Object validation for Object type start points
- [ ] All validation checks are performed automatically
- [ ] Validation happens before export starts
- [ ] Validation errors are reported appropriately with type-specific messages

#### REQ-EXP-006: Validation Error Handling
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Validation errors MUST be logged and displayed as warnings.

**Functional Requirements**:
- Validation errors logged to file
- Warnings displayed in UI
- Export continues for valid start points, skips invalid ones

**Acceptance Criteria**:
- [ ] Validation errors are logged
- [ ] Warnings are displayed in UI
- [ ] Invalid start points are skipped, valid ones continue

#### REQ-EXP-007: USD Asset Structure Compliance
**Priority**: Critical  
**Status**: Confirmed Requirement  
**Reference**: [ASWF USD Working Group Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

**Requirement**: Exported USD files MUST follow ASWF USD Working Group guidelines for Component model structure to ensure compatibility with VFX pipelines and Omniverse workflows.

**Functional Requirements**:
- Root prim MUST be an Xform (Xformable) primitive, not a Scope
- Root prim MUST have `kind` metadata set to `component`
- Root prim MUST be set as `defaultPrim` in the USD file
- Root prim path MUST follow naming convention: start point name → root prim path (e.g., "MyChair" → `/MyChair`)
- Geometry SHOULD be organized under Scope primitives (e.g., `geo`, `mtl` scopes)
- Purpose metadata SHOULD be set appropriately on Scope primitives (render, proxy, guide)
- File extension MUST be `.usd` (allows ascii/binary switching without breaking references)
- Materials MUST be encapsulated within the asset's root primitive hierarchy
- Structure MUST be self-contained and portable

**ASWF Guidelines Alignment**:
- Each exported start point represents a **Component model** (self-contained asset)
- Components keep geometry behind payloads (future consideration for v2.0+)
- Components should inherit from Class primitives (future consideration for v2.0+)
- Reference: [USD-WG Assets - Intent-VFX Examples](https://github.com/usd-wg/assets/tree/main/intent-vfx) for validation targets

**Blender 5.0 Limitations** (Documented):
- Multi-layer composition not supported natively
- Payload authoring has limited control
- Inherits authoring not easily supported
- Variants authoring not supported

**Acceptance Criteria**:
- [ ] Root prim is Xform primitive (not Scope)
- [ ] `kind` metadata is set to `component` on root prim
- [ ] `defaultPrim` is set to root prim path
- [ ] Root prim path follows naming convention (start point name → `/Start pointName`)
- [ ] Geometry is organized under Scope primitives (when possible)
- [ ] Purpose metadata is set on Scope primitives
- [ ] File extension is `.usd`
- [ ] Materials are under root prim hierarchy
- [ ] Exported structure is validated against ASWF guidelines
- [ ] Structure is compatible with intent-vfx examples

**Related Requirements**:
- REQ-EXP-001: Export Options Defaults
- REQ-COMP-001: Blender Version Support
- See `USD_ASSET_STRUCTURE_ANALYSIS.md` for detailed analysis

#### REQ-EXP-008: Auto-Create Export Subfolder
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Users MUST be able to automatically create a subfolder named 'USD_Start point' with the object/collection name in the file location.

**Functional Requirements**:
- Checkbox option: "Create Subfolder" (default: checked)
- Subfolder naming: `USD_Start point_[object_or_collection_name]`
- Subfolder created in the directory specified by the filepath
- USD file placed inside the created subfolder
- If checkbox is unchecked, file is placed directly at the specified filepath
- Option persists with start point configuration

**Additional Functional Requirements**:
- When create_subfolder is enabled and filepath is empty, auto-populate filepath with suggested path
- Suggested filepath format: `{blend_file_directory}/{target_name}.usd` or `//{target_name}.usd` if blend file is unsaved
- When filepath is a directory (no filename), automatically generate filename using target name: `{target_name}.usd`
- Subfolder creation logic must handle both file paths and directory paths correctly

**Acceptance Criteria**:
- [ ] "Create Subfolder" checkbox is available for each start point
- [ ] Checkbox defaults to checked
- [ ] Subfolder is created with correct naming convention
- [ ] USD file is placed inside subfolder when enabled
- [ ] USD file is placed at filepath when disabled
- [ ] Option persists with .blend file
- [ ] Filepath is auto-populated when create_subfolder is checked and filepath is empty
- [ ] Filename is generated when filepath is a directory (no filename specified)
- [ ] Generated filename uses target name (collection or object name)
- [ ] Subfolder creation works correctly with both file paths and directory paths

#### REQ-EXP-009: Origin Metadata in USD Files
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Exported USD files MUST optionally include origin metadata as custom attributes on the root prim to track where the file originated.

**Functional Requirements**:
- Checkbox option: "Include Origin Metadata" (default: enabled)
- Custom attributes added to root prim with namespace `usdme:`
- Attributes include:
  - `usdme:origin_file` - Full path to source .blend file
  - `usdme:origin_filename` - Name of source .blend file
  - `usdme:origin_username` - Username who exported the file
  - `usdme:origin_computer` - Computer/hostname where export occurred
  - `usdme:export_timestamp` - ISO timestamp of export
- Metadata preserved in both ASCII and binary USD formats
- Option persists with start point configuration
- Graceful handling if USD Python API (pxr) is unavailable

**Technical Implementation**:
- Use `pxr.Usd` Python API to add custom attributes after export
- Attributes use `Sdf.ValueTypeNames.String` type
- Metadata added to root prim (start point name path)
- Fallback to default prim if root prim not found

**Acceptance Criteria**:
- [ ] "Include Origin Metadata" checkbox is available
- [ ] Checkbox defaults to enabled
- [ ] All origin attributes are added to root prim
- [ ] Metadata is preserved in binary USD files
- [ ] Metadata is readable in both ASCII and binary formats
- [ ] Option persists with .blend file
- [ ] Graceful error handling if pxr API unavailable

#### REQ-EXP-010: Overwrite Confirmation Dialog
**Priority**: High  
**Status**: ⚠️ **NOT IMPLEMENTED** - Files are overwritten without confirmation  
**Date Added**: 28.12.2025  
**Implementation Status**: v0.1.0 MVP

**Requirement**: When exporting to an existing USD file, users MUST be prompted to confirm overwrite before the file is replaced.

**Current Implementation (v0.1.0)**:
- ❌ **NOT IMPLEMENTED**: No file existence check before export
- ❌ **NOT IMPLEMENTED**: No confirmation dialog
- ⚠️ **CURRENT BEHAVIOR**: Files are overwritten silently without user confirmation

**Functional Requirements**:
- Check if target USD file exists before export
- Show confirmation dialog if file exists
- Dialog must clearly indicate:
  - File path that will be overwritten
  - Warning message about data loss
- User can choose to:
  - Confirm overwrite (proceed with export)
  - Cancel export (abort operation)
- Confirmation dialog uses Blender's standard UI patterns
- Option to remember choice (future enhancement)

**Acceptance Criteria**:
- [ ] File existence check is performed before export
- [ ] Confirmation dialog appears when file exists
- [ ] Dialog shows file path clearly
- [ ] User can confirm or cancel overwrite
- [ ] Export proceeds only after confirmation
- [ ] Export is cancelled if user chooses not to overwrite

**Implementation Notes**:
- Current code: `USDME_OT_export_start points` in `ops_export.py` (line 547)
- Export proceeds directly: `bpy.ops.wm.usd_export(**export_params)` without file existence check
- **TODO for v0.2.0+**: Add file existence check and confirmation dialog before export

#### REQ-EXP-011: Version-Aware API Compatibility
**Priority**: Critical  
**Status**: Confirmed Requirement  
**Version**: v0.2.0 (Required for all export options)  
**Date Added**: 2025-12-28  
**Reference**: `09_Roadmap.md` Section 12.1 - Blender API Compatibility

**Requirement**: The addon MUST implement a version-aware compatibility wrapper to handle Blender 5.0 API changes and ensure safe USD export parameter handling.

**Functional Requirements**:
- Query Blender 5.0 USD exporter RNA properties to get valid parameter names
- Filter out unsupported parameters before passing to `bpy.ops.wm.usd_export()`
- Map old parameter names to new ones via lookup table (as discovered)
- Log warnings for ignored parameters instead of crashing
- Use `bpy.app.version` to detect Blender version
- Provide safe fallbacks for unsupported parameters
- Optionally use USDHook extension points for stable features

**Technical Implementation**:
- Implement `_get_usd_export_properties()` to query valid RNA properties
- Implement `_get_parameter_rename_map()` for parameter name mapping
- Implement `build_usd_export_params()` to filter and validate parameters
- Implement `export_usd_safe()` wrapper function
- Enable verbose logging to catch unsupported parameters during development

**Acceptance Criteria**:
- [ ] Version-aware wrapper is implemented (v0.2.0)
- [ ] All export parameters are validated against Blender 5.0 API
- [ ] Unsupported parameters are filtered out with warnings
- [ ] Parameter rename mapping is functional
- [ ] No `TypeError: keyword not recognized` errors occur
- [ ] Warnings are logged for ignored parameters
- [ ] Exported USD files are valid and open correctly

#### REQ-EXP-012: Unit System Control
**Priority**: High  
**Status**: Confirmed Requirement  
**Version**: v0.2.0 (Planned)  
**Date Added**: 2025-12-28  
**Reference**: `09_Roadmap.md` Section 1.4 - External Items Options

**Requirement**: Users MUST be able to control the unit system used during USD export, with options to use scene units, force specific units, or use preset-based unit settings.

**Functional Requirements**:
- Per-start point unit system selection with the following options:
  - **Use Scene Units** (default): Export using Blender scene's current unit system
  - **Force Centimeters**: Convert all measurements to centimeters regardless of scene units
  - **Force Meters**: Convert all measurements to meters regardless of scene units
- Unit system setting persists with start point configuration
- Unit conversion applies to:
  - Object transforms (position, scale)
  - Geometry dimensions
  - Light intensity (if applicable)
  - Camera settings (if applicable)
- Global default unit system option in addon preferences (optional)
- Preset-based unit selection (e.g., "Omniverse" preset uses centimeters, "VFX Pipeline" uses meters)

**Technical Implementation**:
- Add `unit_system` EnumProperty to `USDME_Start point` (props.py) with options:
  - `SCENE_UNITS` - Use Blender scene units (default)
  - `FORCE_CENTIMETERS` - Force centimeters
  - `FORCE_METERS` - Force meters
- Add UI dropdown in start point settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_to_centimeters` (when forcing centimeters)
- For scene units: Query `bpy.context.scene.unit_settings.system` and `bpy.context.scene.unit_settings.scale_length`
- For forced units: Apply appropriate conversion factor
- Integration with export presets (v0.5.0+) for preset-based unit selection

**Blender API**:
```python
export_params = {
    "convert_to_centimeters": True,  # When unit_system == FORCE_CENTIMETERS
    # Note: Blender may not have direct "force meters" option
    # May require post-processing or scale factor application
}
```

**Use Cases**:
- **Omniverse Workflows**: Typically require centimeters (FORCE_CENTIMETERS)
- **VFX Pipelines**: Often use meters (FORCE_METERS)
- **General Use**: Use scene units for flexibility (SCENE_UNITS)
- **Preset-Based**: Apply unit system based on selected export preset

**Acceptance Criteria**:
- [ ] Unit system selector is available per start point (v0.2.0)
- [ ] "Use Scene Units" option respects Blender scene unit settings
- [ ] "Force Centimeters" option converts all measurements to centimeters
- [ ] "Force Meters" option converts all measurements to meters
- [ ] Unit conversion applies to all relevant export data
- [ ] Unit system setting persists with .blend file
- [ ] Export presets can specify unit system (v0.5.0+)
- [ ] Global default unit system can be set in preferences (optional)
- [ ] Exported USD files have correct unit metadata

#### REQ-EXP-013: USD Post-Processing and Python/pxr Module Detection
**Priority**: High  
**Status**: Confirmed Requirement  
**Date Added**: 2025-01-20  
**Reference**: Learnings from Rhino_USD_MultiExport implementation

**Requirement**: The addon MUST support post-processing of exported USD files to ensure USD compliance (defaultPrim, prim naming) using Python with the `pxr` module, with comprehensive detection of Python installations containing USD Python bindings.

**Functional Requirements**:

**Post-Processing Capabilities**:
- Post-process exported USD files to set `defaultPrim` metadata if missing
- Rename root prim to match start point/filename (sanitized for USD naming rules)
- Set `defaultPrim` in layer metadata for proper referencing
- Preserve file format (binary `.usd`/`.usdc` or ASCII `.usda`) during post-processing
- Use `Export()` method instead of `Save()` to preserve binary format based on file extension

**Python/pxr Module Detection**:
- Comprehensive detection of Python installations with `pxr` module (USD Python bindings)
- Detection priority order:
  1. Python executables in PATH (`python`, `python3`)
  2. `VIRTUAL_ENV` environment variable (virtual environments)
  3. `PYTHON_HOME` environment variable
  4. Common virtual environment locations in user profile (e.g., `USD_PY311env`, `venv`, `.venv`)
  5. NVIDIA Omniverse installation paths (`%LOCALAPPDATA%\ov\pkg\`, `%PROGRAMDATA%\NVIDIA Corporation\Omniverse\`)
  6. Standard Python installation locations (`C:\Python39\`, `C:\Python310\`, etc.)
  7. Program Files Python installations
  8. AppData Local Python installations
- Test each Python executable for `pxr` module availability before use
- Log detection attempts and results for debugging
- Provide clear error messages with installation guidance when `pxr` module is unavailable

**Post-Processing Workflow**:
- For ASCII `.usda` files: Use embedded text-based processing (most reliable, no dependencies)
- For binary `.usd`/`.usdc` files: Use external CPython process with `pxr` module
- Fall back to embedded text processing for ASCII files if `pxr` module unavailable
- Graceful degradation: Export succeeds even if post-processing fails (with warning)

**Error Handling**:
- Clear error messages when `pxr` module is unavailable
- Installation guidance provided in error messages:
  - Option A: Install NVIDIA Omniverse (includes USD Python)
  - Option B: `pip install usd-core` (in Python 3.9-3.13 environment)
  - Instructions to verify: `python -c "from pxr import Usd, Sdf; print('OK')"`
- Workaround suggestion: Export as `.usda` format for reliable post-processing without `pxr`

**Distribution Considerations**:
- Document Python/pxr requirement clearly in user guide
- Provide installation instructions for USD Python bindings
- Consider adding configuration option for custom Python path (future enhancement)
- Do NOT bundle Python runtime (complex licensing, size, conflicts)
- Rely on comprehensive auto-detection for most users

**Technical Implementation**:
- Use `importlib.util` pattern for dynamic module loading
- Create temporary Python script files to avoid command-line escaping issues
- Execute via external CPython process (not Blender's embedded Python)
- Capture and log Python output and errors
- Clean up temporary script files in `finally` blocks
- Use `root_layer.Export(stage_path)` to preserve binary format

**Acceptance Criteria**:
- [ ] Post-processing sets `defaultPrim` correctly for exported USD files
- [ ] Root prim is renamed to match start point/filename (sanitized)
- [ ] Binary USD format is preserved during post-processing
- [ ] Python installations with `pxr` module are detected automatically
- [ ] Detection checks multiple common installation locations
- [ ] Clear error messages guide users when `pxr` module is unavailable
- [ ] Post-processing works for both ASCII and binary USD files
- [ ] Export succeeds even if post-processing fails (with warning)
- [ ] Installation instructions are documented in user guide
- [ ] Detection attempts are logged for debugging

**Related Requirements**:
- REQ-EXP-007: USD Asset Structure Compliance (defaultPrim requirement)
- REQ-EXP-009: Origin Metadata in USD Files (also uses pxr module)

**Implementation Notes**:
- Post-processing is critical for USD compliance (defaultPrim, prim naming)
- Binary USD files require `pxr` module for post-processing
- ASCII USD files can be post-processed without `pxr` (text-based)
- Comprehensive Python detection ensures compatibility across different user setups
- Future enhancement: Add UI option to configure custom Python path

#### REQ-EXP-014: Complete Modifier Export Support
**Priority**: Critical  
**Status**: ✅ **IMPLEMENTED** - v0.1.11  
**Date Added**: 25.01.2026  
**Reference**: Discovery session with SHAKTI_Decals production scene

**Requirement**: The addon MUST support exporting ALL modifier types with applied (baked) geometry, using a non-destructive duplicate-and-apply workflow.

**Functional Requirements**:
- Apply SUBSURF modifiers when `export_subdivision` is enabled
- Apply ALL other modifiers (Shrinkwrap, Array, Mirror, Boolean, etc.) when `export_modifiers` is enabled
- Handle modifiers with target objects (e.g., Shrinkwrap target) by ensuring targets are visible during application
- Apply modifiers in correct modifier stack order
- Preserve original objects and modifiers (non-destructive workflow via duplication)
- Clean up temporary duplicates after export

**Technical Implementation**:
- Duplicate object before applying modifiers
- For Shrinkwrap: Temporarily unhide target object, apply modifier, restore visibility
- Apply modifiers to duplicate in stack order
- Export duplicate (has baked geometry)
- Delete duplicate and restore original names after export

**Acceptance Criteria**:
- [x] SUBSURF modifiers are applied when export_subdivision enabled
- [x] All other modifiers are applied when export_modifiers enabled
- [x] Shrinkwrap target visibility is handled correctly
- [x] Modifiers applied in correct stack order
- [x] Original objects preserved (no permanent modifications)
- [x] Duplicates cleaned up after export
- [x] Works for both OBJECT and COLLECTION start point types

#### REQ-EXP-015: Consistent USD Namespace (Prim Naming)
**Priority**: Critical  
**Status**: ✅ **IMPLEMENTED** - v0.1.11  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - USD referencing requires stable prim paths

**Requirement**: Exported USD prims MUST have names that match the original Blender object names (sanitized for USD naming rules), enabling reliable USD referencing and composition.

**Functional Requirements**:
- USD prim names must match Blender object names (with sanitization)
- No temporary suffixes in USD (`_dup`, `.001`, etc.)
- Name sanitization: Replace spaces and special characters with underscores
- Consistent names enable USD referencing, variant switching, and layer composition
- Name consistency across multiple export sessions

**Technical Implementation - Name-Swap Strategy**:
1. Before duplication: Rename original object to `__USDME_ORIG_{name}` (hidden name)
2. Duplicate the object (Blender assigns original name since it's now free)
3. Apply modifiers to duplicate
4. Export duplicate (has clean original name)
5. After export: Delete duplicate, rename original back from hidden name

**Acceptance Criteria**:
- [x] USD prims have same names as Blender objects (sanitized)
- [x] No `_dup` or `.001` suffixes in exported USD
- [x] Names remain consistent across export sessions
- [x] Original object names restored after export
- [x] Name sanitization works for USD-invalid characters

#### REQ-EXP-016: Export All Collection Objects
**Priority**: Critical  
**Status**: ✅ **IMPLEMENTED** - v0.1.12  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - 4 of 6 objects were missing from USD export

**Requirement**: ALL mesh objects in a collection start point MUST be exported, regardless of whether they have modifiers that need to be applied.

**Functional Requirements**:
- Objects WITH modifiers: Duplicate, apply modifiers, export duplicate
- Objects WITHOUT modifiers: Export original directly (no duplication needed)
- No objects should be silently skipped
- Logging must clearly show which objects are processed and how
- Selection for export includes both duplicated and non-duplicated objects

**Technical Implementation**:
- Build `objects_to_export` list containing:
  - All duplicates (for objects that needed modifier baking)
  - All originals that weren't duplicated (no modifiers to apply)
- Hide all objects except those in `objects_to_export`
- Select all objects in `objects_to_export`
- Export with `selected_objects_only=True`

**Acceptance Criteria**:
- [x] All mesh objects in collection are exported
- [x] Objects with modifiers are exported with baked geometry
- [x] Objects without modifiers are exported as-is
- [x] No silent skipping of objects
- [x] Log shows all processed objects

#### REQ-EXP-017: Robust Cleanup and State Restoration
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.11  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - duplicates were left behind in Blender

**Requirement**: After export completes (success or failure), the Blender scene MUST be in exactly the same state as before export.

**Functional Requirements**:
- No duplicate objects left behind
- All object names restored to originals (from `__USDME_ORIG_*` back to original)
- Object visibility restored to pre-export state
- Object selection restored to pre-export state
- Cleanup runs even if export fails mid-way (rollback on error)
- Emergency name restoration on exceptions

**Technical Implementation**:
- Track all created duplicates in `duplicated_objects` list
- Track all name swaps in `name_swaps` dictionary
- Cleanup runs AFTER `ScopedIsolation` exits (not inside it)
- Use try/finally blocks to ensure cleanup runs on errors
- Emergency name restoration in exception handlers

**Acceptance Criteria**:
- [x] No duplicates remain after export
- [x] All names restored to originals
- [x] Visibility restored
- [x] Selection restored
- [x] Cleanup runs on success
- [x] Cleanup runs on failure (rollback)
- [x] Emergency restoration on exceptions

#### REQ-EXP-018: Consistent Mesh Data Names in USD
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.14  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - mesh prim names incrementing on each export

**Requirement**: Mesh data block names MUST remain consistent across exports to ensure stable USD prim paths.

**Functional Requirements**:
- Mesh prim names in USD must match the original Blender mesh data block names
- No auto-incrementing suffixes (`.011`, `.012`, etc.) on mesh prims
- Consistent mesh names enable reliable USD referencing and variant switching
- Name-swap strategy applied to mesh data blocks, not just objects

**Technical Implementation**:
- Save original mesh data name before duplication (e.g., `Plane.005`)
- After duplication: rename original mesh to hidden name (`__USDME_MESH_Plane.005`)
- Rename duplicate's mesh data to original name (`Plane.005`)
- Track mesh swaps in `mesh_swaps` dictionary
- Use `mesh_swaps_for_cleanup` to persist swaps through isolation context
- Restore original mesh data names during cleanup phase

**Acceptance Criteria**:
- [x] Mesh prim names remain consistent across multiple exports
- [x] No incrementing suffixes on mesh prims
- [x] Original mesh data names preserved in Blender after export
- [x] Cleanup restores mesh data names correctly
- [x] Works with all modifier types

---

#### REQ-MOD-003: Skip Intentionally Disabled Modifiers
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.15  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - disabled modifiers being exported despite all visibility toggles off

**Requirement**: Modifiers that are intentionally disabled (both `show_render` and `show_viewport` are False) MUST be skipped during export to respect user intent.

**Functional Requirements**:
- Modifiers with all visibility toggles off should not be applied during export
- User intent must be respected - disabled modifiers should not affect export
- Modifiers with at least one visibility mode enabled (viewport OR render) should be applied
- Skipped modifiers should be logged for user visibility

**Technical Implementation**:
- Add `should_apply_modifier(mod, logger, start point_context)` helper function
- Check if both `show_render` and `show_viewport` are False
- If both are False, skip the modifier and log the skip
- If either is True, proceed with modifier application (existing v0.1.13 logic)
- Apply check at the beginning of all 4 modifier application loops:
  - OBJECT type SUBSURF modifiers
  - OBJECT type other modifiers
  - COLLECTION type SUBSURF modifiers
  - COLLECTION type other modifiers

**Acceptance Criteria**:
- [x] Modifiers with both `show_render=False` and `show_viewport=False` are skipped
- [x] Modifiers with only `show_viewport=True` are applied
- [x] Modifiers with only `show_render=True` are applied
- [x] Modifiers with both enabled are applied
- [x] Skipped modifiers are logged with reason
- [x] Works for all modifier types (SUBSURF, SHRINKWRAP, ARRAY, etc.)

---

#### REQ-MOD-004: Unified Modifier Export
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.16  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - logical inconsistency between export_subdivision and export_modifiers checkboxes

**Requirement**: Subdivision modifiers MUST be included when "Export Modifiers" is enabled. The legacy "Export Subdivision" checkbox MUST be removed to avoid confusion and ensure consistent behavior.

**Functional Requirements**:
- Single "Export Modifiers" checkbox controls ALL modifiers (Subdivision, Shrinkwrap, Array, etc.)
- When "Export Modifiers" is checked, subdivisions are automatically included
- No separate checkbox for subdivision (it's just another modifier type)
- Cleaner, more intuitive UI with single modifier export control

**Technical Implementation**:
- Remove `export_subdivision` property from `USDME_Start pointPropertyGroup`
- Remove "Export Subdivision" UI checkbox from start point panel
- Replace all `start point.export_subdivision` checks with `start point.export_modifiers`
- Treat SUBSURF modifiers as part of unified modifier export logic
- Apply SUBSURF modifiers first (as they're usually at bottom of stack), then other modifiers
- Remove `subdivision_modifiers_applied` tracking (use unified `modifiers_applied`)

**Acceptance Criteria**:
- [x] "Export Subdivision" checkbox removed from UI
- [x] `export_subdivision` property removed from props
- [x] When "Export Modifiers" is checked, subdivisions are exported
- [x] All modifier types (including SUBSURF) handled by single checkbox
- [x] No confusion about which modifiers are exported
- [x] Backward compatibility: existing start points with `export_subdivision=True` gracefully handled (property ignored)

---

#### REQ-MOD-005: Unified OBJECT/COLLECTION Duplication Strategy
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.17  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - leftover duplicate objects with `_dup1` suffixes after failed exports

**Requirement**: OBJECT and COLLECTION type start points MUST use the same name-swap duplication strategy to ensure consistent behavior and prevent leftover duplicates.

**Functional Requirements**:
- OBJECT type start points use name-swap strategy (same as COLLECTION)
- Duplicates always have original names (not `_dup1` suffixes)
- Automatic cleanup of leftover objects from previous failed exports
- Consistent duplication and cleanup logic across both start point types

**Technical Implementation**:
- OBJECT type: Rename original to `__USDME_ORIG_*` before duplication
- Duplicate gets original name automatically (name is free)
- Track name swaps for cleanup: `name_swaps_for_cleanup`
- Cleanup leftover `__USDME_ORIG_*` objects at export start
- Cleanup leftover `_dup*` objects from old versions

**Acceptance Criteria**:
- [x] OBJECT type uses name-swap strategy (same as COLLECTION)
- [x] Duplicates have original names (not `_dup1` suffixes)
- [x] Leftover objects from failed exports are cleaned up automatically
- [x] Both OBJECT and COLLECTION types use consistent duplication logic
- [x] No leftover `_dup*` objects remain after export

---

#### REQ-MOD-006: Modifier Stack Order Preservation
**Priority**: Critical  
**Status**: ✅ **IMPLEMENTED** - v0.1.18  
**Date Added**: 25.01.2026  
**Reference**: Discovery session - modifiers applied in wrong order causing incorrect geometry (Mirror applied after Subdivision)

**Requirement**: Modifiers MUST be applied in the order they appear in the modifier stack (top to bottom). Stack order determines the final geometry result and MUST be preserved.

**Functional Requirements**:
- Modifiers applied in stack order (top to bottom)
- No type-based reordering (e.g., SUBSURF first, then others)
- Stack order matches Blender viewport behavior
- Geometry results match what user sees in viewport

**Technical Implementation**:
- Iterate through `dup_obj.modifiers` directly (gives modifiers in stack order)
- Apply modifiers in the order they appear: `for mod in list(dup_obj.modifiers):`
- Remove type-based separation logic (`subsurf_modifiers` vs `other_modifiers`)
- Apply to both OBJECT and COLLECTION type start points

**Acceptance Criteria**:
- [x] Modifiers applied in stack order (top to bottom)
- [x] No type-based reordering
- [x] Mirror modifier (top) applies before Subdivision (below)
- [x] Geometry results match Blender viewport
- [x] Works for both OBJECT and COLLECTION types

**Known Issues**:
- ⚠️ **Selection and Mask Issues**: During testing, there were issues with selections and masks of selections that may affect modifier application. This issue is unresolved and should be investigated if similar problems occur in the future.

---

#### REQ-EXP-019: Unit Conversion System
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.19-v0.1.20  
**Date Added**: 26.01.2026  
**Reference**: Discovery session - Omniverse compatibility requirements

**Requirement**: The addon MUST support per-start point unit conversion between metric units (mm, cm, m, km) during export.

**Functional Requirements**:
- Source unit selection (what units the Blender scene uses)
- Target unit selection (what units the USD output should use)
- Auto-detection of source unit from Blender scene settings
- Scale factor calculation: `source_factor / target_factor`
- Scale factor applied to object locations ONLY (not object scale)
- Metric units only: millimeters, centimeters, meters, kilometers

**Technical Implementation**:
- `source_unit` EnumProperty in `USDME_Start pointPropertyGroup`
- `target_unit` EnumProperty in `USDME_Start pointPropertyGroup`
- `detect_source_unit(context)` method for auto-detection
- `get_scale_factor()` method for conversion calculation
- UI "Detect" button to refresh source unit from scene settings

**Acceptance Criteria**:
- [x] Source and target unit selectors available per start point
- [x] Auto-detection from Blender scene unit settings works
- [x] Scale factor correctly calculated
- [x] Scale applied to object.location only (not object.scale)
- [x] `xformOp:scale` remains `(1,1,1)` in USD output

---

#### REQ-EXP-020: Y-Up Axis Conversion
**Priority**: High  
**Status**: ✅ **IMPLEMENTED** - v0.1.19-v0.1.20  
**Date Added**: 26.01.2026  
**Reference**: Omniverse compatibility (Y-up vs Z-up coordinate systems)

**Requirement**: The addon MUST support per-start point axis conversion from Blender's Z-up to Y-up coordinate system for Omniverse compatibility.

**Functional Requirements**:
- Y-up toggle checkbox per start point
- When enabled: Convert from Z-up (Blender/Rhino) to Y-up (Omniverse)
- Location transformation: `(x, y, z) → (x, z, -y)`
- Rotation: Apply -90° rotation around X axis
- Works with unit conversion when both are enabled

**Technical Implementation**:
- `y_is_up` BoolProperty in `USDME_Start pointPropertyGroup`
- Location transform in export logic: `(x, z, -y)`
- Rotation matrix: `-90°` around X axis combined with existing rotation

**Acceptance Criteria**:
- [x] Y-up checkbox available per start point
- [x] Location correctly transformed when enabled
- [x] Rotation correctly applied when enabled
- [x] Works correctly combined with unit conversion
- [x] Omniverse compatibility verified

---

#### REQ-EXP-021: Object Selection for Export
**Priority**: Critical  
**Status**: ✅ **IMPLEMENTED** - v0.1.27  
**Date Added**: 26.01.2026  
**Reference**: Discovery session - OBJECT type export selection bug

**Requirement**: The export logic MUST correctly select objects for export, ensuring that Blender's USD exporter sees the selected objects regardless of previous visibility state.

**Functional Requirements**:
- Objects must be visible to be selected in Blender
- Selection must occur BEFORE hiding non-target objects
- Object references must be refreshed after view layer updates
- Selection verification logging for debugging

**Technical Implementation** - Correct Order:
1. Deselect all objects (while they are still visible)
2. Unhide target objects and select them
3. Set first target as active object
4. Force `context.view_layer.update()`
5. THEN hide all non-target objects

**Critical Pattern**:
```python
# Step 1: Deselect all (while visible)
for obj in context.view_layer.objects:
    obj.select_set(False)

# Step 2: Ensure targets visible and selected
for obj_name in object_names_to_export:
    obj = context.view_layer.objects[obj_name]
    obj.hide_viewport = False
    obj.hide_set(False)
    if not first_obj_set:
        context.view_layer.objects.active = obj
        first_obj_set = True
    obj.select_set(True)

# Step 3: Update
context.view_layer.update()

# Step 4: THEN hide others
for obj in context.view_layer.objects:
    if obj.name not in object_names_to_export:
        obj.hide_viewport = True
```

**Acceptance Criteria**:
- [x] OBJECT type start points export geometry correctly
- [x] COLLECTION type start points export geometry correctly
- [x] Selection works regardless of initial object visibility
- [x] `selected_objects_count > 0` in export logs
- [x] Selection verification logging implemented

---

#### REQ-EXP-022: Collection Normalization Controls
**Priority**: High  
**Status**: Planned  
**Date Added**: 2026-02-02  
**Reference**: Discovery session - "Collection Normalization & Pivot Strategy"

**Requirement**: Collection start points MUST support optional normalization of position, scale, and rotation before export to ensure consistent USD bake results.

**Functional Requirements**:
- Per-collection toggles:
  - Normalize Position (bake translation into geometry)
  - Normalize Scale (apply scale to 1.0)
  - Normalize Rotation (apply rotation to 0; bake into geometry)
- Normalization is applied in a temporary export context (non-destructive)
- State is fully restored after export
- Works with modifiers and duplication workflow

**Acceptance Criteria**:
- [ ] Normalize Position applies translation to geometry without changing world-space placement
- [ ] Normalize Scale results in unit scale (1,1,1) on exported prims
- [ ] Normalize Rotation bakes rotation into geometry (optional toggle)
- [ ] Scene is restored to pre-export state after completion or failure

---

#### REQ-EXP-023: Collection Pivot Source
**Priority**: High  
**Status**: Planned  
**Date Added**: 2026-02-02  
**Reference**: Discovery session - "Collection Normalization & Pivot Strategy"

**Requirement**: Collection start points MUST support configurable pivot sources to stabilize export alignment and decal placement.

**Functional Requirements**:
- Pivot source options:
  - World Origin (0,0,0)
  - Custom XYZ
  - 3D Cursor
  - Object Pivot (Fake Parent reference)
- Fake Parent uses another object's pivot as a reference (does not parent)
- Pivot is applied to collection export root, not to source objects
- Works with normalization toggles (position/scale/rotation)
- Optional pivot-only mode: define pivot without normalizing transforms (keep transforms relative to pivot)

**Acceptance Criteria**:
- [ ] Pivot source selection is available for Collection start points
- [ ] Fake Parent pivot uses selected object origin consistently
- [ ] World Origin and Custom XYZ behave deterministically
- [ ] 3D Cursor pivot can be selected and used
- [ ] Exported USD preserves alignment relative to chosen pivot
- [ ] Pivot-only mode keeps transforms intact while re-basing to pivot

---

#### REQ-EXP-024: Object Pivot Normalization
**Priority**: Medium  
**Status**: Planned  
**Date Added**: 2026-02-02  

**Requirement**: Object start points MUST support an optional pivot normalization to origin (off by default).

**Functional Requirements**:
- Optional toggle to normalize object pivot to (0,0,0)
- Toggle is off by default to preserve existing authoring workflows
- Normalization is non-destructive and restored after export

**Acceptance Criteria**:
- [ ] Object pivot normalization toggle is available for Object start points
- [ ] When enabled, exported object has pivot normalized without changing world-space placement
- [ ] Scene state is restored after export

---

#### REQ-EXP-025: Correct Z-up → Y-up Bake Rotation
**Priority**: Critical  
**Status**: Implemented  
**Date Added**: 2026-02-02  

**Requirement**: The USD bake step MUST convert Blender Z-up geometry to Y-up using a **-90° rotation around X**, and normals MUST reflect the same transform.

**Functional Requirements**:
- Bake rotation uses -90° around X for Z-up → Y-up conversion
- Baked normals match the rotated geometry (no inverted lighting artifacts)
- Stage metadata (`upAxis`) matches the baked geometry orientation

**Acceptance Criteria**:
- [ ] Exported USD opens in Omniverse with correct forward direction (no 180° flip)
- [ ] Normals display correctly without inversion
- [ ] No Omniverse Resolve transform required for axis correction

---

### User Interface Requirements

**Cross-Platform Pattern Reference**: `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`

#### REQ-UI-PATTERN-001: Cross-Platform UI Pattern Alignment (v0.1.19)
**Priority**: High  
**Status**: NEW - Pending Implementation  
**Date Added**: 26.01.2026

**Requirement**: The UI MUST align with the cross-platform USD Multi-Export UI/UX Pattern to ensure consistent user experience across Blender, Rhino, and future host applications.

**Cross-Platform Pattern Requirements**:
Per `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`, the following features are required:

| Feature | Current Status | Priority | Target Version |
|---------|---------------|----------|----------------|
| Single Enable Checkbox | ✅ Implemented | - | v0.1.0 |
| Type Icon | ✅ Implemented | - | v0.1.0 |
| Status Icon | ✅ Implemented | - | v0.1.0 |
| Context-Aware Add | ✅ Implemented | - | v0.1.0 |
| Select Target Button | ✅ Implemented | - | v0.1.0 |
| Export All Enabled | ✅ Implemented | - | v0.1.0 |
| Selective Export | ✅ Implemented | - | v0.1.0 |
| **Unit Conversion** | ✅ Implemented | - | **v0.1.20** |
| **Y-Up Axis** | ✅ Implemented | - | **v0.1.20** |
| **OBJECT Export** | ✅ Implemented | - | **v0.1.27** |
| **Progress Bar** | ❌ Missing | HIGH | **v0.2.0** |
| **Remove Selection-Based** | ⚠️ Last only | MEDIUM | **v0.2.0** |
| **Export Results Summary** | ❌ Missing | MEDIUM | **v0.2.0** |
| Keyboard Shortcuts | ❌ Missing | LOW | v0.2.1+ |

**Note**: Selective export is implemented via the enable/disable checkbox per start point. Users enable the start points they want to export and click "Export Start points" - this IS the selective export mechanism.

**Functional Requirements (v0.2.0)**:
1. **Progress Bar**: Show progress during batch export using `wm.progress_*` API
2. **Selection-Based Remove**: Change Remove to remove selected start point (not just last)
3. **Export Results Summary**: Show popup with export results after batch completion

**Acceptance Criteria**:
- [ ] Progress bar visible during export
- [ ] Remove operates on selected start point in list
- [ ] Export results summary popup shown after completion
- [ ] UI aligns with cross-platform pattern specification

---

#### REQ-UI-001: UI Layout
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: UI MUST use collapsible sections, collapsed by default, with presets.

**Functional Requirements**:
- Collapsible sections for different UI areas
- Sections collapsed by default
- Presets section available

**Acceptance Criteria**:
- [ ] UI uses collapsible sections
- [ ] Sections are collapsed by default
- [ ] Presets section is accessible

#### REQ-UI-002: Start point Display
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Start points MUST be displayed as a simple list with add/remove buttons, with tree view option for hierarchical structures.

**Functional Requirements**:
- Simple list view with add/remove buttons
- Tree view option for hierarchical collections
- Both views available

**Acceptance Criteria**:
- [ ] Simple list view is available
- [ ] Tree view is available for hierarchical structures
- [ ] Users can switch between views

#### REQ-UI-008: Unified Type Selector with Visual Indication
**Priority**: High  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: The UI MUST provide a unified selector that can select either collections or objects, with clear visual indication of what type is selected.

**Functional Requirements**:
- Type selector dropdown (Collection/Object) for each start point
- Visual type indicator (icon and/or label) showing current selection type
- Conditional selectors:
  - Collection type → Show collection searchable dropdown (`prop_search` with `bpy.data.collections`)
  - Object type → Show object searchable dropdown (`prop_search` with `bpy.data.objects`)
- Only the relevant selector is visible based on selected type
- Type indicator updates when type changes
- Sub-collection toggle only visible for Collection type

**Acceptance Criteria**:
- [ ] Type selector dropdown is visible for each start point
- [ ] Collection selector appears when Collection type is selected
- [ ] Object selector appears when Object type is selected
- [ ] Visual indicator (icon/label) shows selected type clearly
- [ ] Non-active selector is hidden
- [ ] Type changes update UI appropriately
- [ ] Sub-collection toggle only appears for Collection type

#### REQ-UI-009: UI Field Labels and Spacing
**Priority**: High  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: The UI MUST provide clear labels for all fields and adequate space for long object/collection names.

**Functional Requirements**:
- All input fields must have visible labels (Type, Collection, Object, Filepath)
- Labels must NOT have leading spaces (e.g., "Type:" not "  Type:")
- Input fields for collection/object names must have sufficient horizontal space
- Use `scale_x` or split layouts to accommodate long names
- Labels should be clear and descriptive with appropriate icons

**Acceptance Criteria**:
- [ ] All fields have visible labels without leading spaces
- [ ] Labels are clearly visible and associated with their input fields
- [ ] Long collection/object names are fully visible without truncation
- [ ] UI layout accommodates names up to 100+ characters

#### REQ-UI-010: Collection Normalization & Pivot UI
**Priority**: High  
**Status**: Planned  
**Date Added**: 2026-02-02

**Requirement**: The Collection export UI MUST expose normalization controls and pivot source selection.

**Functional Requirements**:
- Checkboxes for:
  - Normalize Position
  - Normalize Scale
  - Normalize Rotation
- Pivot source selector:
  - World Origin
  - Custom XYZ (with XYZ inputs)
  - 3D Cursor
  - Object Pivot (Fake Parent)
- Object picker shown when Object Pivot is selected
- XYZ fields shown only when Custom XYZ is selected
- Clear tooltips explaining non-destructive behavior

**Acceptance Criteria**:
- [ ] Normalization controls appear only for Collection start points
- [ ] Pivot source selector is visible and updates dependent fields
- [ ] UI tooltips clarify fake parent and non-destructive behavior

#### REQ-UI-011: Collection vs Object Usage Guidance
**Priority**: Medium  
**Status**: Planned  
**Date Added**: 2026-02-02

**Requirement**: The UI MUST provide guidance on when to use Collection vs Object start points.

**Functional Requirements**:
- Tooltip text on type selector explaining:
  - Collection: bulk export of multiple objects; requires defined pivot
  - Object: single asset export with explicit target object
- Guidance in documentation explaining:
  - Collection pivot selection and normalization tradeoffs
  - Object start points for precise single-object export

**Acceptance Criteria**:
- [ ] Hover tooltips clearly explain Collection vs Object usage
- [ ] Documentation includes a "When to use Collections vs Objects" section

#### REQ-UI-003: Start point List Information
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Start point list MUST display all relevant information.

**Functional Requirements**:
- Start point name
- Start point type (Collection/Object) with visual indicator
- Collection/object name (based on type)
- Export filepath
- Status (enabled/disabled)
- Last export time
- Export options summary

**Acceptance Criteria**:
- [ ] All information is visible in start point list
- [ ] Start point type is clearly indicated
- [ ] Information is clearly displayed
- [ ] List is easy to read and navigate

#### REQ-UI-004: Export Controls
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: All export controls MUST be visible in the UI.

**Functional Requirements**:
- Export All button
- Export Selected button
- Export Active button
- Export Defined Start points button
- Export progress indicator
- Export log/results
- Export settings/preferences

**Acceptance Criteria**:
- [ ] All export buttons are visible
- [ ] Progress indicator is shown during export
- [ ] Export log/results are displayed

#### REQ-UI-005: Support & Feedback UI
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Support and feedback buttons MUST be available in an extra tab or expandable section.

**Functional Requirements**:
- Bug Report button
- Feature Request button
- Documentation link
- Help/Support link
- Located in separate tab or expandable section

**Acceptance Criteria**:
- [ ] Support buttons are accessible
- [ ] Buttons are in separate tab or expandable section
- [ ] All support options are available

#### REQ-UI-006: Bug Report Functionality
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Bug report functionality MUST follow common best practices.

**Functional Requirements**:
- Open GitHub Issues page with bug report template pre-filled
- Auto-collect all relevant information:
  - Blender version
  - Addon version
  - Operating system
  - Current scene information (object count, collection count, start point count)
  - Current start point configuration
  - Recent error messages/logs
  - Export settings
- Use common best practices for bug reporting

**Acceptance Criteria**:
- [ ] Bug report button opens GitHub Issues
- [ ] Template is pre-filled with all information
- [ ] Follows common best practices

#### REQ-UI-007: Support Button Location
**Priority**: Low  
**Status**: Confirmed Requirement

**Requirement**: Support buttons location MUST follow common best practices.

**Functional Requirements**:
- Use standard Blender addon patterns for support button placement
- Follow common UI/UX best practices

**Acceptance Criteria**:
- [ ] Support buttons follow best practices
- [ ] Location is intuitive for users

### Error Handling & Feedback Requirements

#### REQ-ERR-001: Error Reporting
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Error reporting MUST follow common best practices with both simple and detailed messages.

**Functional Requirements**:
- Popup dialog for critical errors
- Status message in UI panel
- Blender's info area
- Log file
- Console output
- Both simple (user-friendly) and detailed (technical) messages available

**Acceptance Criteria**:
- [ ] Errors are reported using best practices
- [ ] Both simple and detailed messages are available
- [ ] Errors are logged appropriately

#### REQ-ERR-002: Success Feedback
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Successful exports MUST be indicated using all available feedback methods.

**Functional Requirements**:
- Status message
- Notification popup
- Visual indicator (checkmark, color change)
- Export log with results

**Acceptance Criteria**:
- [ ] All success feedback methods are used
- [ ] Users can clearly see export success
- [ ] Export log shows results

#### REQ-ERR-003: Logging
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Export operations MUST be logged with time tags in log file names.

**Functional Requirements**:
- Log to file (next to exported files)
- Time tag in log file name
- Log export start/end times
- Log start points exported
- Log file paths
- Log errors/warnings
- Log export options used

**Acceptance Criteria**:
- [ ] Logs are created next to exported files
- [ ] Log file names include time tags
- [ ] All relevant information is logged

### Performance Requirements

#### REQ-PERF-001: UI During Export
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: UI MUST show progress and allow cancellation during export.

**Functional Requirements**:
- Show progress indicator
- Allow cancellation
- UI remains responsive

**Acceptance Criteria**:
- [ ] Progress is shown during export
- [ ] Export can be cancelled
- [ ] UI remains responsive

#### REQ-PERF-002: Large Scene Handling
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Large scenes MUST be handled efficiently with selective export support.

**Functional Requirements**:
- Support selective export (toggle start points on/off)
- Optimize visibility operations
- Add progress indicators
- Allow cancellation
- Efficient state management
- Batch export optimization

**Acceptance Criteria**:
- [ ] Start points can be toggled on/off for selective export
- [ ] Large scenes export efficiently
- [ ] Progress indicators work for large scenes

### Compatibility Requirements

#### REQ-COMP-001: Blender Version Support
**Priority**: Critical  
**Status**: Confirmed Requirement

**Requirement**: Addon MUST support Blender 5.0+ and future versions with version checks.

**Functional Requirements**:
- Target Blender 5.0+ (released November 18, 2025)
- Version checks for future Blender versions
- No support for Blender 4.x

**Acceptance Criteria**:
- [ ] Addon works with Blender 5.0+
- [ ] Version checks are implemented
- [ ] Future versions are supported with version checks

#### REQ-COMP-002: Non-Intrusive Design
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Addon MUST follow non-intrusive design principles.

**Functional Requirements**:
- Use Blender's standard addon patterns
- Avoid modifying global Blender settings
- Use isolated namespaces for custom properties
- Document known conflicts if discovered

**Acceptance Criteria**:
- [ ] Addon follows Blender standards
- [ ] No global settings are modified
- [ ] Custom properties use isolated namespaces

#### REQ-COMP-003: ASWF USD Guidelines Compliance
**Priority**: Critical  
**Status**: Confirmed Requirement  
**Reference**: [ASWF USD Working Group Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

**Requirement**: Exported USD files MUST comply with ASWF USD Working Group guidelines to ensure compatibility with VFX pipelines, Omniverse workflows, and industry standards.

**Functional Requirements**:
- Follow Component model structure guidelines
- Align with USD-WG Assets intent-vfx examples
- Ensure compatibility with VFX Reference Platform requirements
- Document alignment with ASWF standards

**Acceptance Criteria**:
- [ ] Exported USD structure follows ASWF guidelines (see REQ-EXP-007)
- [ ] Structure is validated against intent-vfx examples
- [ ] Documentation references ASWF guidelines
- [ ] Compatibility with VFX pipelines is maintained

**Related Documents**:
- `USD_ASSET_STRUCTURE_ANALYSIS.md` - Detailed analysis of ASWF guidelines relevance
- REQ-EXP-007: USD Asset Structure Compliance

### Future Requirements (Version 2.0)

#### REQ-FUT-001: Command-Line/Batch Export
**Priority**: Medium  
**Status**: Planned for v2.0

**Requirement**: Command-line/batch export support (deferred to v2.0).

**Functional Requirements**:
- Support headless Blender execution
- Support batch script execution
- Support command-line arguments

#### REQ-FUT-002: Python API for Scripting
**Priority**: Medium  
**Status**: Planned for v2.0

**Requirement**: Comprehensive Python API for scripting (deferred to v2.0).

**Functional Requirements**:
- Programmatic start point creation
- Programmatic export execution
- Access to export results/status

#### REQ-FUT-003: External Tool Integration
**Priority**: Low  
**Status**: Planned for v2.0

**Requirement**: Integration with external tools (deferred to v2.0).

**Functional Requirements**:
- Asset management systems
- Version control systems
- CI/CD pipelines

#### REQ-FUT-004: Custom Property Reading/Writing
**Priority**: Low  
**Status**: Planned for v2.0

**Requirement**: Custom property reading/writing (deferred to v2.0).

**Functional Requirements**:
- Read custom properties from objects
- Write custom properties to USD
- Custom metadata handling

### Out-of-Scope for v1.0

#### REQ-OOS-001: USD Composition
**Status**: Out-of-Scope for v1.0

**Requirement**: USD composition features are out-of-scope. Focus on simple export only.

#### REQ-OOS-002: Custom Metadata
**Status**: Out-of-Scope for v1.0

**Requirement**: Custom metadata beyond standard properties is out-of-scope for v1.0.

#### REQ-OOS-003: Custom Export Hooks
**Status**: Out-of-Scope for v1.0

**Requirement**: Custom export hooks (USDHook) are out-of-scope for v1.0. Standard export only.

#### REQ-OOS-004: Asset Management Integration
**Status**: Out-of-Scope for v1.0

**Requirement**: Asset management integration is out-of-scope for v1.0.

### Roadmap Items

#### REQ-ROAD-001: Documentation
**Status**: Roadmap

**Requirement**: Comprehensive documentation (user manual, quick start, video tutorials) - planned for later.

#### REQ-ROAD-002: Help & Support
**Status**: Roadmap

**Requirement**: Enhanced help & support features (built-in tooltips, help button, example scenes, support forum) - planned for later.

#### REQ-COMP-004: Cross-Platform Compatibility
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: The addon MUST work on Windows, macOS, and Linux using the same ZIP file. No platform-specific builds are required.

**Functional Requirements**:
- Same ZIP file works on Windows, macOS, and Linux
- Use `bpy.path` utilities for all file path operations (platform-agnostic)
- Never use hardcoded path separators (`/` or `\`)
- Use `bpy.path.abspath()` and `bpy.path.relpath()` for path resolution
- Use `pathlib.Path` or `os.path.join()` for path construction if needed
- Test on multiple platforms during development

**Why it works**:
- Blender addons are pure Python code (platform-independent)
- Blender's Python API (`bpy`) is consistent across platforms
- `bpy.path` utilities handle platform differences automatically
- No platform-specific binaries required

**Acceptance Criteria**:
- [ ] Same ZIP file installs and works on Windows
- [ ] Same ZIP file installs and works on macOS
- [ ] Same ZIP file installs and works on Linux
- [ ] File paths work correctly on all platforms
- [ ] No hardcoded path separators in code
- [ ] All path operations use `bpy.path` utilities

---

## Implementation Status

### Recently Added Requirements (v2.4.0 - 26.01.2026)

- **REQ-EXP-019**: Unit Conversion System - Per-start point metric unit conversion (mm, cm, m, km) with auto-detection
- **REQ-EXP-020**: Y-Up Axis Conversion - Per-start point Z-up to Y-up conversion for Omniverse compatibility
- **REQ-EXP-021**: Object Selection for Export - Correct selection order to ensure objects are selected before export

### Previously Added Requirements (v1.7.0 - 25.01.2026)

- **REQ-EXP-014**: Complete Modifier Export Support - Apply ALL modifier types with baked geometry, non-destructive workflow
- **REQ-EXP-015**: Consistent USD Namespace (Prim Naming) - Name-swap strategy for clean prim names matching Blender objects
- **REQ-EXP-016**: Export All Collection Objects - Export all mesh objects, not just those with modifiers
- **REQ-EXP-017**: Robust Cleanup and State Restoration - No leftover duplicates, complete state restoration

### Previously Added Requirements (v1.6.0 - 20.01.2025)

- **REQ-EXP-013**: USD Post-Processing and Python/pxr Module Detection - Post-process exported USD files for compliance, comprehensive Python detection

### Previously Added Requirements (v1.5.0 - 28.12.2025)

- **REQ-SP-007**: Remove Start point with Selection - Remove button with dropdown to select which start point to remove

### Previously Added Requirements (v1.4.0 - 28.12.2025)

- **REQ-SP-003**: Unified Collection/Object Selection - Start points can select collections or objects
- **REQ-SP-004**: Sub-Collection Handling - Control over sub-collection inclusion
- **REQ-SP-005**: Auto-Naming Start points - Start point names automatically match selected collection/object
- **REQ-SP-006**: Selection Tracking Button - Select button to track which start point belongs to what
- **REQ-UI-008**: Unified Type Selector with Visual Indication - UI for type selection
- **REQ-UI-009**: UI Field Labels and Spacing - Clear labels and adequate space for long names
- **REQ-EXP-008**: Auto-Create Export Subfolder - Create USD_Start point subfolder with object/collection name
- **REQ-EXP-009**: Origin Metadata in USD Files - Track origin file, username, computer, timestamp

### Current Implementation Status

**v0.1.27 MVP (Complete)**:
- ✅ MVP Complete: Basic start point-based export functionality
- ✅ Collection selection implemented
- ✅ Object selection implemented (fixed in v0.1.27)
- ✅ Sub-collection recursive inclusion implemented
- ✅ Type selector UI implemented
- ✅ Sub-collection toggle implemented
- ✅ Filepath subfolder creation implemented
- ✅ Origin metadata tracking implemented
- ✅ Subdivision export (with duplicate preservation fix)
- ✅ Light exclusion implemented
- ✅ State management and scene isolation
- ✅ Comprehensive logging system
- ✅ Auto-naming start points (matches collection/object name)
- ✅ Selection tracking button (Select button per start point)
- ✅ Pre-flight validation (checks start point completeness before export)
- ✅ Bug report generation
- ✅ Add start point with auto-detection (collection/object from context)
- ✅ **Unit conversion system** (mm, cm, m, km) with auto-detection (v0.1.20)
- ✅ **Y-up axis conversion** for Omniverse compatibility (v0.1.20)
- ✅ **xformOp:scale = (1,1,1)** ensured in USD output (v0.1.22)
- ✅ **OBJECT type export** works correctly (fixed in v0.1.27)
- ⚠️ Basic remove start point (removes last only, no dropdown selection)
- ❌ Overwrite confirmation dialog (NOT implemented - files overwritten silently)
- ❌ Per-start point export options (hardcoded defaults only)

**v0.2.0+ (Planned - See Roadmap)**:
- ⏳ Per-start point export options (General, Stage, Geometry, Materials, etc.)
- ⏳ Version-aware compatibility wrapper for Blender 5.0 API
- ⏳ Export presets system
- ⏳ Animation export support
- ⏳ Rigging export support
- ⏳ Particles export support
- ⏳ Enhanced validation and pre-flight checks

**Reference**: See `09_Roadmap.md` for detailed feature breakdown and implementation phases.

---

**Status**: ✅ MVP Complete (v0.1.27) - Requirements for v0.2.0+ defined in Roadmap  
**Last Updated**: 2026-01-26  
**Roadmap Reference**: See `09_Roadmap.md` for comprehensive v0.2.0+ feature requirements and implementation plan

