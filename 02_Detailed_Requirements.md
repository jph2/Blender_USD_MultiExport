# Blender USD Stable Export - Detailed Requirements

**Status**: ✅ In Progress - Requirements being populated from confirmed questionnaire items  
**Date Created**: 25.11.2025  
**Version**: v1.5.0  
**Last Updated**: 28.12.2025 - Added remove endpoint with selection dropdown requirement  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)

---

## 📋 Requirements Status

This document contains detailed requirements derived from confirmed questionnaire responses and ASWF USD Working Group guidelines.

**Important**: All requirements must be compatible with **Blender 5.0+ only**. Blender 4.x versions are not supported.

**ASWF Compliance**: Requirements marked with ASWF references align with [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md) to ensure compatibility with VFX pipelines and Omniverse workflows. See `USD_ASSET_STRUCTURE_ANALYSIS.md` for detailed analysis.

**System Architecture: Push vs Pull Workflows**

**MVP Architecture: One-Way Push Model**

The MVP focuses on a **one-way push model** for ComfyUI integration:

**Push Phase (Blender Side)**:
- **Blender** exports USD files to predefined destinations via export endpoints
- Export happens independently in Blender (user-initiated or scripted)
- USD files are written to specified file paths
- **No ComfyUI involvement** in the export process

**Pull Phase (ComfyUI Side)**:
- **ComfyUI** reads the export path from endpoint definitions stored in .blend file
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
- Endpoint definition and management
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

### Endpoint Management Requirements

#### REQ-EP-001: Endpoints Saved with Blend File
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Endpoints MUST be saved with the .blend file as scene-specific data.

**Functional Requirements**:
- Endpoints are stored per-scene
- Endpoints persist when .blend file is saved and reopened
- Each scene can have its own set of endpoints

**Acceptance Criteria**:
- [ ] Endpoints are saved with .blend file
- [ ] Endpoints are restored when .blend file is reopened
- [ ] Different scenes can have different endpoint configurations

#### REQ-EP-002: Enable/Disable Toggle
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Endpoints MUST support enable/disable toggle to allow disabling endpoints without deleting them.

**Functional Requirements**:
- Each endpoint has an enabled/disabled state
- Disabled endpoints are skipped during export
- Endpoints can be toggled on/off without deletion

**Acceptance Criteria**:
- [ ] Endpoints have enable/disable toggle
- [ ] Disabled endpoints are skipped during export
- [ ] Endpoint state persists with .blend file

#### REQ-EP-007: Remove Endpoint with Selection
**Priority**: Medium  
**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Basic remove exists, dropdown selection NOT implemented  
**Date Added**: 28.12.2025  
**Implementation Status**: v0.1.0 MVP

**Requirement**: Users MUST be able to remove specific endpoints using a remove button with a dropdown list to select which endpoint to remove.

**Current Implementation (v0.1.0)**:
- ✅ Remove button exists in UI
- ✅ Removes last endpoint from list
- ✅ Operation supports UNDO
- ✅ Remove button works when endpoints exist
- ❌ **NOT IMPLEMENTED**: Dropdown list to select which endpoint to remove
- ❌ **NOT IMPLEMENTED**: Visual selection of endpoint before removal

**Functional Requirements**:
- Remove button with dropdown list showing all endpoints
- Dropdown displays endpoint names (and optionally type/collection/object for clarity)
- User can select which endpoint to remove from the dropdown
- Selected endpoint is removed from the scene
- Operation can be undone (UNDO support)
- If no endpoints exist, remove button is disabled or hidden

**Acceptance Criteria**:
- [x] Remove button exists (basic implementation)
- [x] Remove operation supports UNDO
- [x] Remove button works when endpoints exist
- [ ] Remove button has a dropdown list of endpoints
- [ ] Dropdown shows endpoint names clearly
- [ ] User can select and remove a specific endpoint (currently only removes last)
- [ ] Removed endpoint is properly cleaned up from scene data

**Implementation Notes**:
- Current code: `USDME_OT_remove_endpoint` in `ui.py` (lines 313-326)
- Currently removes: `settings.endpoints.remove(len(settings.endpoints) - 1)` (last endpoint only)
- **TODO for v0.2.0+**: Implement dropdown selection UI for endpoint removal

#### REQ-EP-003: Unified Collection/Object Selection
**Priority**: High  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Endpoints MUST support selecting either a collection (with sub-collections) or a single object as the export target, with clear visual indication of the selected type.

**Functional Requirements**:
- Each endpoint has a type selector (Collection or Object)
- Collection type: Select entire collection or sub-collection
- Object type: Select single object
- Clear visual indication of selected type (icon, label, or both)
- Type-specific selectors (collection dropdown for Collection type, object dropdown for Object type)
- Only the relevant selector is visible based on endpoint type
- Sub-collection inclusion option for Collection type (include/exclude child collections)

**Acceptance Criteria**:
- [ ] Endpoint type selector is available (Collection/Object)
- [ ] Collection selector appears when Collection type is selected
- [ ] Object selector appears when Object type is selected
- [ ] Visual indicator shows selected type (icon and/or label)
- [ ] Sub-collection toggle is available for Collection type
- [ ] Endpoint type persists with .blend file
- [ ] Auto-detection sets type based on selection (collection active → Collection type, object selected → Object type)

#### REQ-EP-005: Auto-Naming Endpoints
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Endpoint names MUST be automatically set to match the selected collection or object name.

**Functional Requirements**:
- When a collection is selected, endpoint name is automatically set to the collection name
- When an object is selected, endpoint name is automatically set to the object name
- Auto-naming occurs when collection_name or object_name property changes
- User can manually override the endpoint name if needed
- Auto-naming updates if the selected collection/object changes

**Acceptance Criteria**:
- [ ] Endpoint name automatically updates when collection is selected
- [ ] Endpoint name automatically updates when object is selected
- [ ] Auto-naming works for both Collection and Object type endpoints
- [ ] User can manually edit endpoint name to override auto-naming
- [ ] Endpoint name updates if collection/object selection changes

#### REQ-EP-006: Selection Tracking Button
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: Each endpoint MUST have a "Select" button that allows users to track which endpoint belongs to which collection/object by selecting it in the viewport.

**Functional Requirements**:
- "Select" button available for each endpoint
- Button selects the collection/object in the viewport when clicked
- For Collection type: Selects all objects in the collection (and sub-collections if enabled)
- For Object type: Selects the object in the viewport
- Button provides visual feedback (icon, tooltip)
- Selection works even if endpoint is disabled

**Acceptance Criteria**:
- [ ] "Select" button is visible for each endpoint
- [ ] Clicking "Select" button selects the collection/object in viewport
- [ ] Collection selection includes all objects in collection (respects sub-collection setting)
- [ ] Object selection selects the specific object
- [ ] Button works for both enabled and disabled endpoints
- [ ] Visual feedback is provided (icon, tooltip)

#### REQ-EP-004: Sub-Collection Handling
**Priority**: Medium  
**Status**: Confirmed Requirement  
**Date Added**: 28.12.2025

**Requirement**: When a collection endpoint is selected, users MUST be able to control whether sub-collections (child collections) are included in the export.

**Functional Requirements**:
- Toggle option: "Include Sub-collections" (default: enabled)
- When enabled: Export includes objects from selected collection AND all child collections recursively
- When disabled: Export includes only objects directly in the selected collection (excludes child collections)
- Option only visible/applicable for Collection type endpoints
- Option persists with endpoint configuration

**Acceptance Criteria**:
- [ ] "Include Sub-collections" toggle is available for Collection type endpoints
- [ ] Toggle defaults to enabled (current behavior)
- [ ] When enabled, child collections are included recursively
- [ ] When disabled, only direct collection objects are exported
- [ ] Toggle state persists with .blend file

### Export Functionality Requirements

#### REQ-EXP-001: Export Options Defaults
**Priority**: High  
**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Hardcoded defaults exist, per-endpoint options NOT implemented  
**Version**: v0.2.0+ (Planned)  
**Reference**: `09_Roadmap.md` - Comprehensive export options roadmap

**Requirement**: All USD export options MUST be available per endpoint, with sensible defaults based on common workflows.

**Current Implementation (v0.1.0)**:
- ✅ Hardcoded export defaults exist in `ops_export.py` (lines 338-346)
- ✅ Defaults include: `export_materials=True`, `export_uvmaps=True`, `export_normals=True`, `export_animation=False`, `export_lights=False`
- ✅ Root prim path generation (sanitized from endpoint name)
- ❌ **NOT IMPLEMENTED**: Per-endpoint export option overrides
- ❌ **NOT IMPLEMENTED**: UI for configuring export options per endpoint
- ❌ **NOT IMPLEMENTED**: Export options stored in endpoint properties

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
      "root_prim_path": f"/{sanitized_name}",  # Generated from endpoint name
  }
  ```
- Additional per-endpoint options implemented:
  - `export_subdivision` (BoolProperty in `props.py` line 103)
  - `include_origin_metadata` (BoolProperty in `props.py` line 97)
- **NOT IMPLEMENTED**: All other export options are hardcoded and cannot be changed per endpoint

**Note**: Current v0.1.0 MVP has hardcoded defaults. Per-endpoint export options will be implemented in v0.2.0+ as per roadmap phases.

**Acceptance Criteria**:
- [ ] All export options are available per endpoint (v0.2.0+)
- [ ] Default values match common workflow needs
- [ ] Users can override defaults per endpoint
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
- Presets can be applied to endpoints
- Preset inheritance: Endpoints can override preset values
- Preset management UI (create, edit, delete, import/export)

**Acceptance Criteria**:
- [ ] Predefined presets are available (v0.5.0+)
- [ ] Users can create custom presets
- [ ] Presets can be applied to endpoints
- [ ] Preset values can be overridden per endpoint
- [ ] Presets can be imported/exported as files
- [ ] Preset management UI is functional

#### REQ-EXP-003: Export Options Scope
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export options MUST support both global defaults and per-endpoint overrides.

**Functional Requirements**:
- Global default export settings
- Per-endpoint override capability
- Endpoints inherit global defaults unless overridden

**Acceptance Criteria**:
- [ ] Global default export settings exist
- [ ] Endpoints can override global defaults
- [ ] Override system works correctly

#### REQ-EXP-004: Batch Export Operations
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export MUST support batch operations with progress indication and cancellation.

**Functional Requirements**:
- Export multiple endpoints sequentially
- Progress indicator during batch export
- Ability to cancel batch export
- Export log/results display

**Acceptance Criteria**:
- [ ] Multiple endpoints can be exported in batch
- [ ] Progress indicator shows export progress
- [ ] Batch export can be cancelled
- [ ] Export results are logged

#### REQ-EXP-005: Export Validation
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Export validation MUST be performed automatically in the background.

**Functional Requirements**:
- Check endpoint type is valid (Collection or Object)
- Check endpoint collection/object exists (type-specific validation)
- Check filepath is valid
- Check disk space available
- Check write permissions
- Validate exported USD file
- Check material/texture references
- All validation done automatically before export
- Type-specific error messages (collection not found vs object not found)

**Acceptance Criteria**:
- [ ] Endpoint type validation is performed
- [ ] Collection validation for Collection type endpoints
- [ ] Object validation for Object type endpoints
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
- Export continues for valid endpoints, skips invalid ones

**Acceptance Criteria**:
- [ ] Validation errors are logged
- [ ] Warnings are displayed in UI
- [ ] Invalid endpoints are skipped, valid ones continue

#### REQ-EXP-007: USD Asset Structure Compliance
**Priority**: Critical  
**Status**: Confirmed Requirement  
**Reference**: [ASWF USD Working Group Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

**Requirement**: Exported USD files MUST follow ASWF USD Working Group guidelines for Component model structure to ensure compatibility with VFX pipelines and Omniverse workflows.

**Functional Requirements**:
- Root prim MUST be an Xform (Xformable) primitive, not a Scope
- Root prim MUST have `kind` metadata set to `component`
- Root prim MUST be set as `defaultPrim` in the USD file
- Root prim path MUST follow naming convention: endpoint name → root prim path (e.g., "MyChair" → `/MyChair`)
- Geometry SHOULD be organized under Scope primitives (e.g., `geo`, `mtl` scopes)
- Purpose metadata SHOULD be set appropriately on Scope primitives (render, proxy, guide)
- File extension MUST be `.usd` (allows ascii/binary switching without breaking references)
- Materials MUST be encapsulated within the asset's root primitive hierarchy
- Structure MUST be self-contained and portable

**ASWF Guidelines Alignment**:
- Each exported endpoint represents a **Component model** (self-contained asset)
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
- [ ] Root prim path follows naming convention (endpoint name → `/EndpointName`)
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

**Requirement**: Users MUST be able to automatically create a subfolder named 'USD_Endpoint' with the object/collection name in the file location.

**Functional Requirements**:
- Checkbox option: "Create Subfolder" (default: checked)
- Subfolder naming: `USD_Endpoint_[object_or_collection_name]`
- Subfolder created in the directory specified by the filepath
- USD file placed inside the created subfolder
- If checkbox is unchecked, file is placed directly at the specified filepath
- Option persists with endpoint configuration

**Additional Functional Requirements**:
- When create_subfolder is enabled and filepath is empty, auto-populate filepath with suggested path
- Suggested filepath format: `{blend_file_directory}/{target_name}.usd` or `//{target_name}.usd` if blend file is unsaved
- When filepath is a directory (no filename), automatically generate filename using target name: `{target_name}.usd`
- Subfolder creation logic must handle both file paths and directory paths correctly

**Acceptance Criteria**:
- [ ] "Create Subfolder" checkbox is available for each endpoint
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
- Option persists with endpoint configuration
- Graceful handling if USD Python API (pxr) is unavailable

**Technical Implementation**:
- Use `pxr.Usd` Python API to add custom attributes after export
- Attributes use `Sdf.ValueTypeNames.String` type
- Metadata added to root prim (endpoint name path)
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
- Current code: `USDME_OT_export_endpoints` in `ops_export.py` (line 547)
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
- Per-endpoint unit system selection with the following options:
  - **Use Scene Units** (default): Export using Blender scene's current unit system
  - **Force Centimeters**: Convert all measurements to centimeters regardless of scene units
  - **Force Meters**: Convert all measurements to meters regardless of scene units
- Unit system setting persists with endpoint configuration
- Unit conversion applies to:
  - Object transforms (position, scale)
  - Geometry dimensions
  - Light intensity (if applicable)
  - Camera settings (if applicable)
- Global default unit system option in addon preferences (optional)
- Preset-based unit selection (e.g., "Omniverse" preset uses centimeters, "VFX Pipeline" uses meters)

**Technical Implementation**:
- Add `unit_system` EnumProperty to `USDME_Endpoint` (props.py) with options:
  - `SCENE_UNITS` - Use Blender scene units (default)
  - `FORCE_CENTIMETERS` - Force centimeters
  - `FORCE_METERS` - Force meters
- Add UI dropdown in endpoint settings panel (ui.py)
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
- [ ] Unit system selector is available per endpoint (v0.2.0)
- [ ] "Use Scene Units" option respects Blender scene unit settings
- [ ] "Force Centimeters" option converts all measurements to centimeters
- [ ] "Force Meters" option converts all measurements to meters
- [ ] Unit conversion applies to all relevant export data
- [ ] Unit system setting persists with .blend file
- [ ] Export presets can specify unit system (v0.5.0+)
- [ ] Global default unit system can be set in preferences (optional)
- [ ] Exported USD files have correct unit metadata

### User Interface Requirements

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

#### REQ-UI-002: Endpoint Display
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: Endpoints MUST be displayed as a simple list with add/remove buttons, with tree view option for hierarchical structures.

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
- Type selector dropdown (Collection/Object) for each endpoint
- Visual type indicator (icon and/or label) showing current selection type
- Conditional selectors:
  - Collection type → Show collection searchable dropdown (`prop_search` with `bpy.data.collections`)
  - Object type → Show object searchable dropdown (`prop_search` with `bpy.data.objects`)
- Only the relevant selector is visible based on selected type
- Type indicator updates when type changes
- Sub-collection toggle only visible for Collection type

**Acceptance Criteria**:
- [ ] Type selector dropdown is visible for each endpoint
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

#### REQ-UI-003: Endpoint List Information
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Endpoint list MUST display all relevant information.

**Functional Requirements**:
- Endpoint name
- Endpoint type (Collection/Object) with visual indicator
- Collection/object name (based on type)
- Export filepath
- Status (enabled/disabled)
- Last export time
- Export options summary

**Acceptance Criteria**:
- [ ] All information is visible in endpoint list
- [ ] Endpoint type is clearly indicated
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
- Export Defined Endpoints button
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
  - Current scene information (object count, collection count, endpoint count)
  - Current endpoint configuration
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
- Log endpoints exported
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
- Support selective export (toggle endpoints on/off)
- Optimize visibility operations
- Add progress indicators
- Allow cancellation
- Efficient state management
- Batch export optimization

**Acceptance Criteria**:
- [ ] Endpoints can be toggled on/off for selective export
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
- Programmatic endpoint creation
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

### Recently Added Requirements (v1.5.0 - 28.12.2025)

- **REQ-EP-007**: Remove Endpoint with Selection - Remove button with dropdown to select which endpoint to remove

### Previously Added Requirements (v1.4.0 - 28.12.2025)

- **REQ-EP-003**: Unified Collection/Object Selection - Endpoints can select collections or objects
- **REQ-EP-004**: Sub-Collection Handling - Control over sub-collection inclusion
- **REQ-EP-005**: Auto-Naming Endpoints - Endpoint names automatically match selected collection/object
- **REQ-EP-006**: Selection Tracking Button - Select button to track which endpoint belongs to what
- **REQ-UI-008**: Unified Type Selector with Visual Indication - UI for type selection
- **REQ-UI-009**: UI Field Labels and Spacing - Clear labels and adequate space for long names
- **REQ-EXP-008**: Auto-Create Export Subfolder - Create USD_Endpoint subfolder with object/collection name
- **REQ-EXP-009**: Origin Metadata in USD Files - Track origin file, username, computer, timestamp

### Current Implementation Status

**v0.1.0 MVP (Complete)**:
- ✅ MVP Complete: Basic endpoint-based export functionality
- ✅ Collection selection implemented
- ✅ Object selection implemented
- ✅ Sub-collection recursive inclusion implemented
- ✅ Type selector UI implemented
- ✅ Sub-collection toggle implemented
- ✅ Filepath subfolder creation implemented
- ✅ Origin metadata tracking implemented
- ✅ Subdivision export (with duplicate preservation fix)
- ✅ Light exclusion implemented
- ✅ State management and scene isolation
- ✅ Comprehensive logging system
- ✅ Auto-naming endpoints (matches collection/object name)
- ✅ Selection tracking button (Select button per endpoint)
- ✅ Pre-flight validation (checks endpoint completeness before export)
- ✅ Bug report generation
- ✅ Add endpoint with auto-detection (collection/object from context)
- ⚠️ Basic remove endpoint (removes last only, no dropdown selection)
- ❌ Overwrite confirmation dialog (NOT implemented - files overwritten silently)
- ❌ Per-endpoint export options (hardcoded defaults only)

**v0.2.0+ (Planned - See Roadmap)**:
- ⏳ Per-endpoint export options (General, Stage, Geometry, Materials, etc.)
- ⏳ Version-aware compatibility wrapper for Blender 5.0 API
- ⏳ Export presets system
- ⏳ Animation export support
- ⏳ Rigging export support
- ⏳ Particles export support
- ⏳ Enhanced validation and pre-flight checks

**Reference**: See `09_Roadmap.md` for detailed feature breakdown and implementation phases.

---

**Status**: ✅ MVP Complete (v0.1.0) - Requirements for v0.2.0+ defined in Roadmap  
**Last Updated**: 2025-12-28  
**Roadmap Reference**: See `09_Roadmap.md` for comprehensive v0.2.0+ feature requirements and implementation plan

