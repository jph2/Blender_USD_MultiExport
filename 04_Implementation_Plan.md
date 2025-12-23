# Blender USD Stable Export - Implementation Plan

**Status**: ✅ MVP Complete - v0.1.0 Released
**Date Created**: 25.11.2025
**Version**: v1.1.0 (Updated for MVP completion)
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)
**MVP Release**: v0.1.0 - December 23, 2025

---

## ⚠️ This document is a placeholder

This document will contain the detailed step-by-step implementation plan derived from the Module Design (`03_Module_Design.md`).

**Important**: All implementation must target **Blender 5.0+ only**. Blender 4.x versions are not supported.

**Next Step**: Complete the module design first, then populate this document with:
- Implementation phases
- Task breakdown
- Timeline estimates
- Dependencies
- Testing strategy
- Milestones

---

## Document Structure (To Be Populated)

### 1. Implementation Overview
- Approach
- Phases
- Timeline

### 2. Phase Breakdown

#### Phase 0: Setup & Environment (Blender 5.0+ installation and verification)
**Critical Tasks:**
- Install Blender 5.0+ (released November 18, 2025)
- Verify Python 3.11+ (bundled with Blender 5.0)
- Test `bpy.ops.wm.usd_export` operator availability and parameters
- Verify USD export capabilities with test scenes
- Document Blender 5.0 USD export operator signature
- Query operator defaults: `bpy.ops.wm.usd_export.get_rna_type().properties`

**Deliverables:**
- Working Blender 5.0 installation
- Verified USD export operator parameters
- Test scene with various data types (meshes, cameras, curves, lights, etc.)
- Documentation of operator signature

#### Phase 1: MVP Core Functionality ✅ **COMPLETED** (v0.1.0)
**Completed Tasks:**
- ✅ **Implement `ScopedIsolation` context manager** (MUST HAVE)
  - Cache selection/visibility state
  - Isolate target endpoint
  - Guarantee state restoration
- ✅ **Implement `StateManager` class** (MUST HAVE)
  - Backup/restore scene state
  - Handle batch export state management
  - Error recovery mechanisms
- ✅ **Implement `PathResolver` utility**
  - Relative path storage (`//export/prop_a.usd`)
  - Absolute path resolution before export
  - Directory auto-creation
- ✅ Implement visibility checking before export
- ✅ Add warnings for hidden objects/collections
- ✅ Support all Blender 5.0 supported data types
- ✅ Handle experimental instancing with appropriate warnings
- ✅ Implement proper error handling for Blender 5.0 limitations

**Deliverables (v0.1.0 MVP):**
- ✅ `ScopedIsolation` context manager (working)
- ✅ `StateManager` class (working)
- ✅ `PathResolver` utility (working)
- ✅ Endpoint definition system with visibility validation
- ✅ Warning system for hidden objects/collections
- ✅ Support for all Blender 5.0 data types
- ✅ Error handling for known limitations
- ✅ Comprehensive logging and bug reporting
- ✅ Functional UI with export controls

**MVP Decision**: Core functionality complete and tested. Advanced features deferred to ensure MVP quality and gather user feedback before investing in complex USD manipulation features.

#### Phase 1.5: Advanced Features (Post-MVP) 🔄 **PLANNED**
**Deferred Tasks (v0.2.0+):**
- ⏳ **Implement `RootPrimPathGenerator`**
  - Auto-generate from endpoint name
  - Prevent name collisions
- ⏳ **Implement `PreFlightValidator`**
  - Check empty collections
  - Verify paths/directories
  - Check visibility settings
  - Warn about hidden objects

#### Phase 2: UI Implementation (with warnings for hidden objects/experimental features)
**Critical Tasks:**
- Add visibility status indicators for endpoints
- Warn users about hidden objects/collections
- Label experimental features clearly (instancing)
- Document limitations in UI tooltips/help
- Add color management warnings (HDR/wide-gamut material appearance)
- **UI for coordinate system selection** (Z-Up vs Y-Up)
- **UI for unit scale** (Meters vs Centimeters)
- **Display relative paths** in UI, resolve on export

**Deliverables:**
- UI with visibility indicators
- Warning messages for hidden objects
- Clear labeling of experimental features
- Helpful tooltips documenting limitations
- Coordinate system/unit selection UI

#### Phase 3: Export Logic (using Blender 5.0 USD export operator with proper parameters)
**Critical Tasks:**
- Use Blender 5.0 USD export operator with verified parameters
- **Wrap export in `ScopedIsolation` context manager** (MUST HAVE)
- Respect visibility rules (only export visible objects)
- Handle all supported data types correctly
- Implement proper material export (USD Preview Surface: color, metallic, roughness)
- Support export options: root prim path, selection-only, animation range, custom properties, UV maps, normals, merge transforms, triangulation, texture paths
- **Apply coordinate system/unit transformations** correctly
- **Use auto-generated `root_prim_path`** if not explicitly set

**Deliverables:**
- Working export logic using Blender 5.0 operator
- Proper material handling
- Support for all export options
- Correct handling of visibility rules
- Coordinate system/unit handling

#### Phase 4: Testing & Polish (test against Blender 5.0 USD export limitations)
**Critical Tasks:**
- Test state manager with batch exports (5+ endpoints)
- Test state restoration after crashes/interruptions
- Test relative path handling (move project, share via version control)
- Test root prim path generation and collision prevention
- Test pre-flight validation
- Test against Blender 5.0 USD export limitations:
  - Verify no invisible objects are exported
  - Verify no composition arcs are attempted
  - Test experimental instancing features
- Verify all supported data types export correctly
- Test visibility scenarios (hidden objects, collections)
- Validate material appearance with HDR/wide-gamut color management
- Test edge cases: absolute shape keys (should fail gracefully), bendy bones (should warn)
- **Test coordinate system/unit handling** (verify objects appear correctly in Omniverse)

**Deliverables:**
- Comprehensive test suite
- Test results documentation
- Known limitations documentation
- User guide with Blender 5.0 specifics
- State management validation results

### 3. Task Details
- For each phase:
  - Tasks
  - Subtasks
  - Dependencies
  - Estimates
  - Assignments

### 4. Timeline & Milestones
- Gantt chart or timeline
- Key milestones
- Deliverables

### 5. Testing Strategy
- Unit testing
- Integration testing
- User acceptance testing
- Test cases

### 6. Risk Management
- Identified risks
- Mitigation strategies
- Contingency plans

### 7. Resource Requirements
- Development resources
- Testing resources
- Documentation resources

---

**Status**: ✅ MVP v0.1.0 Complete - Ready for Testing
**MVP Release**: December 23, 2025
**Next Phase**: v0.2.0 Advanced Features (Post-MVP validation)
**Last Updated**: 23.12.2025

**MVP Summary**:
- Core endpoint-based export workflow functional
- Safe scene state management implemented
- Comprehensive error handling and logging
- Cross-platform path resolution working
- Automated bug report generation ready
- Testing framework documented and ready

**Why MVP Approach**:
- Validate core concept before adding complexity
- Get real-world testing feedback to guide priorities
- Ensure solid foundation before advanced USD features
- Risk mitigation through incremental development

