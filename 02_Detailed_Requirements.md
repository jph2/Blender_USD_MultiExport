# Blender USD Stable Export - Detailed Requirements

**Status**: ✅ In Progress - Requirements being populated from confirmed questionnaire items  
**Date Created**: 25.11.2025  
**Version**: v1.2.0  
**Last Updated**: 25.11.2025 - Added ASWF USD Guidelines compliance requirements  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)

---

## 📋 Requirements Status

This document contains detailed requirements derived from confirmed questionnaire responses and ASWF USD Working Group guidelines.

**Important**: All requirements must be compatible with **Blender 5.0+ only**. Blender 4.x versions are not supported.

**ASWF Compliance**: Requirements marked with ASWF references align with [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md) to ensure compatibility with VFX pipelines and Omniverse workflows. See `USD_ASSET_STRUCTURE_ANALYSIS.md` for detailed analysis.

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

### Export Functionality Requirements

#### REQ-EXP-001: Export Options Defaults
**Priority**: High  
**Status**: Confirmed Requirement

**Requirement**: All USD export options MUST be available per endpoint, with all options enabled by default.

**Functional Requirements**:
- Export animation (default: enabled)
- Export materials (default: enabled)
- Export textures (default: enabled)
- Export cameras (default: enabled)
- Export lights (default: enabled)
- Export armatures (default: enabled)
- Export shape keys (default: enabled)
- Export hair/curves (default: enabled)
- Export UV maps (default: enabled)
- Export normals (default: enabled)
- Export mesh colors (default: enabled)
- Export custom properties (default: enabled)
- Use instancing (default: enabled)
- Export subdivision (default: enabled, method: BEST_MATCH)
- Evaluation mode (default: RENDER)

**Acceptance Criteria**:
- [ ] All export options are available per endpoint
- [ ] All options are enabled by default
- [ ] Users can disable options per endpoint

#### REQ-EXP-002: Export Presets
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: The addon MUST support export presets (predefined and user-defined).

**Functional Requirements**:
- Predefined presets (e.g., "Full Export", "Geometry Only", "Materials Only")
- User-defined presets
- Presets can be applied to endpoints

**Acceptance Criteria**:
- [ ] Predefined presets are available
- [ ] Users can create custom presets
- [ ] Presets can be applied to endpoints

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
- Check endpoint collection/objects exist
- Check filepath is valid
- Check disk space available
- Check write permissions
- Validate exported USD file
- Check material/texture references
- All validation done automatically before export

**Acceptance Criteria**:
- [ ] All validation checks are performed automatically
- [ ] Validation happens before export starts
- [ ] Validation errors are reported appropriately

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

#### REQ-UI-003: Endpoint List Information
**Priority**: Medium  
**Status**: Confirmed Requirement

**Requirement**: Endpoint list MUST display all relevant information.

**Functional Requirements**:
- Endpoint name
- Collection/object name
- Export filepath
- Status (enabled/disabled)
- Last export time
- Export options summary

**Acceptance Criteria**:
- [ ] All information is visible in endpoint list
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

**Status**: ⏳ Awaiting Requirements Questionnaire completion  
**Last Updated**: 25.11.2025

