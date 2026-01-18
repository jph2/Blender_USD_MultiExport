# Blender USD Stable Export - Module Design

**Status**: ✅ Updated - Incorporating ASWF USD Guidelines compliance  
**Date Created**: 25.11.2025  
**Version**: v1.1.0  
**Last Updated**: 25.11.2025 - Added ASWF USD structure compliance requirements  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)

---

## ✅ Module Architecture Document

This document describes the actual module architecture and design as implemented in v0.1.0 MVP.

**Important**: All module design targets **Blender 5.0+ only**. Blender 4.x versions are not supported.

**Status**: Updated to reflect actual v0.1.0 MVP implementation (December 2025)

---

## Document Structure (To Be Populated)

### 1. Architecture Overview
- High-level architecture
- Design principles
- Module organization

### 2. Module Breakdown (v0.1.0 MVP Implementation)

**Actual Module Structure:**

**Core modules:**
- `state_manager.py` - **IMPLEMENTED**: Handles scene state backup/restore for safe isolation
  - `ScopedIsolation` class - Context manager for endpoint isolation
  - `StateManager` class - Scene state management for batch operations
- `props.py` - **IMPLEMENTED**: Data model definitions
  - `USDME_EndpointPropertyGroup` - Endpoint property definitions
  - `USDME_SceneProperties` - Scene-level container
- `ops_export.py` - **IMPLEMENTED**: Export operations
  - `USDME_OT_export_endpoints` - Main export operator
  - Pre-flight validation logic
  - Subdivision export with duplicate preservation
  - Origin metadata injection

**UI modules:**
- `ui.py` - **IMPLEMENTED**: User interface
  - `USDME_PT_main_panel` - Main panel in Scene Properties
  - `USDME_OT_add_endpoint` - Add endpoint operator
  - `USDME_OT_remove_endpoint` - Remove endpoint operator (removes last only)
  - `USDME_OT_select_endpoint_target` - Selection tracking operator
  - `USDME_OT_generate_bug_report` - Bug report generation

**Utility modules:**
- `path_resolver.py` - **IMPLEMENTED**: Path handling
  - `PathResolver` class - Cross-platform path resolution
  - `resolve_export_path()` - Convenience function
- `logging_utils.py` - **IMPLEMENTED**: Logging system
  - `USDME_Logger` class - Comprehensive logging with file rotation
  - Bug report generation
  - Performance timers and context tracking

**Addon Registration:**
- `__init__.py` - **IMPLEMENTED**: Addon registration and preferences
  - `USDMultiExportPreferences` - Addon preferences (log level, default settings)
  - Module registration and class registration

### 3. Class Design

#### Critical Classes (Must Implement)

**`ScopedIsolation` (Context Manager)** - ✅ **IMPLEMENTED**
- **Location**: `state_manager.py` (lines 15-169)
- **Purpose**: Temporarily isolates a specific collection or object for export
- **Responsibilities**:
  - Cache current selection/visibility state
  - Deselect all, hide all (efficiently)
  - Unhide/select ONLY target endpoint
  - Guarantee state restoration in `__exit__` (even on errors)
- **Implementation**: Uses `try...finally` pattern, caches exact state
- **Features**:
  - Supports Collection and Object types
  - Recursive collection inclusion option (`include_subcollections`)
  - Object hierarchy traversal for parent-child relationships
  - Safe state restoration even on exceptions

**`StateManager`** - ✅ **IMPLEMENTED**
- **Location**: `state_manager.py` (lines 171-313)
- **Purpose**: Manages scene state for batch exports
- **Responsibilities**:
  - Backup scene state (selection, visibility, active object)
  - Restore scene state safely
  - Handle state corruption recovery
- **Critical**: Works even if export crashes mid-loop
- **Features**:
  - `safe_batch_operation()` context manager
  - Multiple backup support (stack-based)
  - Scene integrity validation
  - Automatic rollback on exceptions

**`PathResolver`** - ✅ **IMPLEMENTED**
- **Location**: `path_resolver.py` (lines 19-397)
- **Purpose**: Handle file path resolution (cross-platform compatible)
- **Responsibilities**:
  - Store paths relative to blend file (`//export/prop_a.usd`)
  - Resolve to absolute paths before export: `bpy.path.abspath()` (platform-agnostic)
  - Auto-create directories if they don't exist
  - **Cross-platform**: Uses `bpy.path` utilities which handle Windows/Mac/Linux path differences automatically
  - Never use hardcoded path separators (`/` or `\`) - always use `bpy.path` or `pathlib.Path`
- **Features**:
  - `resolve_export_path()` - Main resolution function
  - `validate_export_path()` - Path validation with detailed feedback
  - `get_relative_path()` - Convert absolute to relative paths
  - `ensure_directory_exists()` - Directory creation
  - `get_safe_filename()` - Filename sanitization
  - Handles `./` paths by converting to `//` format

**`RootPrimPathGenerator`** - ⚠️ **PARTIALLY IMPLEMENTED**
- **Location**: `ops_export.py` (lines 330-336) - Inline implementation
- **Purpose**: Generate consistent root prim paths following ASWF USD Working Group guidelines
- **Current Implementation**:
  - ✅ Root prim path generated from endpoint name (sanitized)
  - ✅ Name sanitization (removes invalid characters, replaces with underscores)
  - ✅ Fallback to "RootPrim" if name becomes empty
  - ❌ **NOT IMPLEMENTED**: Dedicated class/module (inline code only)
  - ❌ **NOT IMPLEMENTED**: `kind` metadata setting (not set in v0.1.0)
  - ❌ **NOT IMPLEMENTED**: `defaultPrim` setting (relies on Blender default)
  - ❌ **NOT IMPLEMENTED**: Name collision prevention validation
- **ASWF Compliance**: Basic path generation exists, full compliance deferred to v0.2.0+

**`PreFlightValidator`** - ✅ **IMPLEMENTED** (inline in export operator)
- **Location**: `ops_export.py` (lines 77-136)
- **Purpose**: Validate endpoints before export
- **Current Implementation**:
  - ✅ Type-specific validation (Collection vs Object)
  - ✅ Collection/object existence checks
  - ✅ Filepath validation (not empty)
  - ✅ Invalid endpoint detection and reporting
  - ✅ Pre-flight validation before batch export starts
  - ⚠️ **PARTIAL**: Empty collection check (not explicitly checked, but would fail during export)
  - ❌ **NOT IMPLEMENTED**: Dedicated validator class (inline code)
  - ❌ **NOT IMPLEMENTED**: Root prim path naming convention validation
  - ❌ **NOT IMPLEMENTED**: Reserved name conflict checking

**`USDStructureValidator`** - ❌ **NOT IMPLEMENTED**
- **Status**: Planned for v0.2.0+
- **Purpose**: Validate exported USD structure against ASWF guidelines
- **Responsibilities** (Future):
  - Verify root prim is Xform (not Scope)
  - Verify `kind` metadata is set to `component` on root prim
  - Verify `defaultPrim` is set correctly
  - Verify Purpose metadata is set appropriately
  - Verify materials are under root prim hierarchy
  - Compare structure against intent-vfx examples (optional, for testing)
- **ASWF Compliance**: Full validation deferred to v0.2.0+
- **Current State**: Basic root prim path generation exists, but no post-export validation

- Class diagrams
- Class relationships

### 4. Data Models

**Endpoint Data Structure** - ✅ **IMPLEMENTED** (`props.py` lines 16-124):
- ✅ `name` (StringProperty) - Used for default `root_prim_path`
- ✅ `endpoint_type` (EnumProperty) - 'COLLECTION' or 'OBJECT'
- ✅ `collection_name` (StringProperty) - Collection reference
- ✅ `object_name` (StringProperty) - Object reference
- ✅ `filepath` (StringProperty) - Stored as relative: `//export/prop_a.usd`
- ✅ `include_subcollections` (BoolProperty) - Sub-collection inclusion toggle
- ✅ `create_subfolder` (BoolProperty) - Auto-create USD_Endpoint subfolder
- ✅ `include_origin_metadata` (BoolProperty) - Add origin metadata to USD
- ✅ `export_subdivision` (BoolProperty) - Bake subdivision modifiers
- ✅ `enabled` (BoolProperty) - Enable/disable endpoint
- ⚠️ **PARTIAL**: Root prim path (auto-generated from name, sanitized inline in export operator)
- ❌ **NOT IMPLEMENTED**: Root prim kind (not set in v0.1.0)
- ❌ **NOT IMPLEMENTED**: Per-endpoint export configuration (hardcoded defaults)

**State Snapshot:**
- Selection state (list of selected objects)
- Visibility state (dict: object -> visibility)
- Active object reference
- View layer settings

**Export Configuration:**
- Must respect Blender 5.0 USD export limitations
- Coordinate system settings (Z-Up vs Y-Up)
- Unit scale (Meters vs Centimeters)
- Material export mode (USD Preview Surface - Phase 1, MDL - Phase 2)
- **USD Structure Settings** (ASWF compliance):
  - Root prim kind: `component` (default)
  - Root prim type: Xform (required)
  - Set `defaultPrim`: Yes (required)
  - Purpose metadata: Set on Scope primitives (recommended)
  - File extension: `.usd` (required for ascii/binary switching)

### 5. API Design
- Public APIs
- Internal APIs
- Extension points

### 6. Component Interactions
- Sequence diagrams
- Data flow
- Event handling

### 7. File Structure
- Directory layout
- File organization
- Naming conventions

---

### 8. ASWF USD Guidelines Compliance

**Reference**: [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

**Key Requirements**:
- Exported endpoints are **Component models** (self-contained assets)
- Root prim MUST be Xform with `kind` metadata set to `component`
- Root prim MUST be set as `defaultPrim`
- Structure MUST follow ASWF naming conventions
- Materials MUST be encapsulated within root prim hierarchy
- File extension MUST be `.usd` (allows ascii/binary switching)

**Implementation Notes**:
- `RootPrimPathGenerator` enforces naming conventions
- `USDStructureValidator` validates compliance post-export
- Blender 5.0 limitations documented (payloads, inherits, multi-layer composition)
- Future enhancements (v2.0+): Payload support, Class inheritance, multi-layer structure

**Validation Targets**:
- Compare exports against [USD-WG Assets - Intent-VFX Examples](https://github.com/usd-wg/assets/tree/main/intent-vfx)
- Ensure compatibility with VFX pipelines and Omniverse workflows

**See**: `USD_ASSET_STRUCTURE_ANALYSIS.md` for detailed analysis

---

**Status**: ✅ Updated to reflect actual v0.1.0 MVP implementation  
**Last Updated**: 13.01.2026  
**Implementation Review**: Completed - Documents actual code structure vs planned architecture

