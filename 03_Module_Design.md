# Blender USD Stable Export - Module Design

**Status**: ✅ Updated - Incorporating ASWF USD Guidelines compliance  
**Date Created**: 25.11.2025  
**Version**: v1.1.0  
**Last Updated**: 25.11.2025 - Added ASWF USD structure compliance requirements  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)

---

## ⚠️ This document is a placeholder

This document will contain the module architecture and design derived from the Detailed Requirements (`02_Detailed_Requirements.md`).

**Important**: All module design must target **Blender 5.0+ only**. Blender 4.x versions are not supported.

**Next Step**: Complete the requirements document first, then populate this document with:
- Module structure
- Class diagrams
- Component interactions
- Data models
- API design

---

## Document Structure (To Be Populated)

### 1. Architecture Overview
- High-level architecture
- Design principles
- Module organization

### 2. Module Breakdown
- **Core modules:**
  - State Manager (`state_manager.py`) - **CRITICAL**: Handles scene state backup/restore for safe isolation
  - Isolation Context (`isolation.py`) - Context manager for endpoint isolation
- **UI modules:**
  - Panel UI
  - Endpoint management UI
- **Export modules:**
  - Export operators
  - Pre-flight validation
- **Utility modules:**
  - Path handling (relative path resolution)
  - Root prim path generation (with ASWF compliance)
  - Coordinate system handling
  - USD structure validation (ASWF guidelines compliance)

### 3. Class Design

#### Critical Classes (Must Implement)

**`ScopedIsolation` (Context Manager)**
- **Purpose**: Temporarily isolates a specific collection or object for export
- **Responsibilities**:
  - Cache current selection/visibility state
  - Deselect all, hide all (efficiently)
  - Unhide/select ONLY target endpoint
  - Guarantee state restoration in `__exit__` (even on errors)
- **Implementation**: Use `try...finally` pattern, cache exact state

**`StateManager`**
- **Purpose**: Manages scene state for batch exports
- **Responsibilities**:
  - Backup scene state (selection, visibility, active object)
  - Restore scene state safely
  - Handle state corruption recovery
- **Critical**: Must work even if export crashes mid-loop

**`PathResolver`**
- **Purpose**: Handle file path resolution
- **Responsibilities**:
  - Store paths relative to blend file (`//export/prop_a.usd`)
  - Resolve to absolute paths before export: `bpy.path.abspath()`
  - Auto-create directories if they don't exist

**`RootPrimPathGenerator`**
- **Purpose**: Generate consistent root prim paths following ASWF USD Working Group guidelines
- **Responsibilities**:
  - Default `root_prim_path` from endpoint name (e.g., "MyChair" -> `/MyChair`)
  - Prevent name collisions when merging USDs (avoid `/World`, `/environment`, `/Mesh`, `/root`)
  - Validate prim path format
  - Ensure root prim will be Xform (not Scope) - validated before export
  - **NEW**: Set `kind` metadata to `component` on root prim (via post-export processing or export parameters)
  - **NEW**: Ensure `defaultPrim` is set to root prim path
- **ASWF Compliance**: Follows [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

**`PreFlightValidator`**
- **Purpose**: Validate endpoints before export
- **Responsibilities**:
  - Check if target collections are empty
  - Verify file paths and directories exist
  - Check render/viewport visibility settings
  - Warn about hidden objects/collections
  - **NEW**: Validate root prim path follows naming convention
  - **NEW**: Validate root prim path doesn't conflict with reserved names (`/World`, `/environment`)

**`USDStructureValidator`** (NEW)
- **Purpose**: Validate exported USD structure against ASWF guidelines
- **Responsibilities**:
  - Verify root prim is Xform (not Scope)
  - Verify `kind` metadata is set to `component` on root prim
  - Verify `defaultPrim` is set correctly
  - Verify Purpose metadata is set appropriately
  - Verify materials are under root prim hierarchy
  - Compare structure against intent-vfx examples (optional, for testing)
- **ASWF Compliance**: Validates against [USD-WG Asset Structure Guidelines](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

- Class diagrams
- Class relationships

### 4. Data Models

**Endpoint Data Structure:**
- Name (used for default `root_prim_path`)
- Collection/Object reference
- Filepath (stored as relative: `//export/prop_a.usd`)
- Export configuration
- **Root prim path** (auto-generated from name if not set, follows ASWF naming conventions)
- **Root prim kind** (default: `component`, per ASWF guidelines)
- **Root prim type** (must be Xform, not Scope, per ASWF guidelines)

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

**Status**: ✅ Updated with ASWF USD Guidelines compliance requirements  
**Last Updated**: 25.11.2025

