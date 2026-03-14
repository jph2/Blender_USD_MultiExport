---
arys_schema_version: '1.2'
id: 610ded4d-92e2-4f61-97dc-35166a1be758
title: Blender USD Multi Export - Testing Plan
type: TECHNICAL
status: active
trust_level: 2
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Blender USD Multi Export - Testing Plan

**Status**: ✅ Ready for Implementation
**Date Created**: 23.12.2025
**Version**: v0.1.3 (MVP Release)
**Last Updated**: 03.02.2026 23:27
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)
**Tag block:**
#blender #framework_integration #export #creative #conversion #validation #advanced #stage #openusd #usd_core #workflow_automation #ai_coding_agents #quality_assurance #deterministic_workflows #performance #optimization

---

## 📋 Overview

This testing plan provides comprehensive procedures for validating the Blender USD Multi Export addon. The plan is structured in phases to ensure thorough testing from basic functionality through advanced scenarios and error conditions.

### 🎯 Testing Objectives

- **Verify Core Functionality**: Ensure endpoints can be defined and exported successfully
- **Validate Safety**: Confirm scene state preservation and crash resistance
- **Test Error Handling**: Verify graceful failure handling with actionable error messages
- **Ensure Compatibility**: Confirm cross-platform compatibility and Blender 5.0+ support
- **Validate Logging**: Test verbose logging and bug report generation
- **Performance Validation**: Ensure efficient handling of large scenes

### 📊 Success Criteria

- **All basic export tests pass** (100% success rate)
- **Error scenarios handled gracefully** (appropriate warnings/errors)
- **Scene state preservation** (no permanent changes to user scenes)
- **Bug reports contain all required information** (system, scene, operation context)
- **Performance acceptable** (< 5 seconds per endpoint, < 30 seconds for large scenes)
- **Cross-platform compatibility** (same ZIP works on Windows/macOS/Linux)

---

## 🔧 Setup Requirements

### Prerequisites

- **Blender 5.0+** installed and functional
- **Test scene files** with various object types (meshes, materials, lights, cameras)
- **Multiple collections** with different content types
- **File system permissions** for export directories
- **External text editor** for reviewing JSON bug reports

### Test Environment Setup

1. **Create test scene** with organized collections:
   ```
   Test Scene Structure:
   ├── Characters (collection with rigged character)
   │   ├── Hero (mesh with armature, materials, textures)
   │   └── NPC (simpler character)
   ├── Props (collection with static objects)
   │   ├── Furniture (tables, chairs with materials)
   │   └── Decorations (plants, lights with complex materials)
   ├── Environment (collection with lighting and cameras)
   │   ├── Lighting (area lights, HDRI setup)
   │   └── Cameras (perspective cameras with animation)
   └── Vehicles (collection with animated objects)
       └── Car (mesh with animation, materials)
   ```

2. **Export directory structure**:
   ```
   //export/
   ├── characters/
   ├── props/
   ├── environment/
   └── vehicles/
   ```

3. **Enable addon** in Blender:
   - Install from ZIP or enable from development directory
   - Verify "USD Multi Export" panel appears in Scene Properties

---

## Automated testing (Z-up / Y-up)

Optional checks for the **Z to Y for Omniverse** option (no test suite in repo yet):

1. **Stage metadata:** After exporting with the option enabled, open the USDA with pxr (e.g. `Usd.Stage.Open(filepath)`), read stage metadata: `UsdGeom.GetStageUpAxis(stage)` should be `UsdGeom.Tokens.y`.
2. **Default prim rotation:** Get the default prim, read its `xformOp:rotateXYZ` (or equivalent); when Z-to-Y is on, the root Xform should have rotation equivalent to -90° about X (e.g. `(-90, 0, 0)` in degrees).
3. **With option off:** Export with the option disabled; `upAxis` should be Z and default prim rotation (0,0,0).

These can be implemented as a small Python script (run with Blender’s USD Python or standalone pxr) or as pytest/Blender test operators when you add a test harness.

---

## 🧪 Testing Phases

### Phase 1: Basic Functionality Testing

**Objective**: Verify core addon functionality works as expected.

#### 1.1 Addon Installation & UI
- [ ] Addon appears in Blender's addon list
- [ ] "USD Multi Export" panel visible in Scene Properties
- [ ] All UI elements functional (Add/Remove buttons, endpoint list, export button)
- [ ] Verbose logging toggle accessible
- [ ] Bug report button present

#### 1.2 Endpoint Management
- [ ] Add endpoint button creates new endpoint with default name
- [ ] Endpoint name field editable
- [ ] Collection name field editable
- [ ] Filepath field supports Blender relative paths (`//export/file.usd`)
- [ ] Enable/disable toggle works per endpoint
- [ ] Remove endpoint button deletes last endpoint
- [ ] Endpoints persist with .blend file save/load

#### 1.3 Basic Export Testing
- [ ] Single endpoint export completes successfully
- [ ] USD file created at specified location
- [ ] File contains expected content (meshes, materials)
- [ ] Progress messages appear in Blender Info area
- [ ] Export operation completes within 5 seconds

### Phase 2: Advanced Functionality Testing

**Objective**: Test complex scenarios and edge cases.

#### 2.1 Multiple Endpoint Batch Export
- [ ] 3+ endpoints export successfully in batch
- [ ] Each endpoint creates separate USD file
- [ ] Files contain only their respective collection content
- [ ] Batch operation completes within 30 seconds
- [ ] Progress indication shows current endpoint

#### 2.2 Content Type Validation
- [ ] **Meshes**: Complex geometry exports correctly
- [ ] **Materials**: USD Preview Surface materials preserved
- [ ] **Textures**: Image references maintained
- [ ] **UV Maps**: UV coordinates exported
- [ ] **Normals**: Surface normals preserved
- [ ] **Cameras**: Camera properties exported
- [ ] **Lights**: Light properties exported
- [ ] **Armatures**: Bone hierarchies preserved (no bendy bones)

#### 2.3 Scene State Preservation
- [ ] Object visibility unchanged after export
- [ ] Object selection unchanged after export
- [ ] Active object unchanged after export
- [ ] View layer settings preserved
- [ ] Render engine unchanged

#### 2.4 USD Bake Validation (Post-Process Pipeline)
- [ ] Baseline export: Blender USD file is meters, Z-up, no transforms baked
- [ ] Bake script runs without errors on a single-mesh USD file
- [ ] Baked file has correct `metersPerUnit` metadata (e.g., 0.01 for cm)
- [ ] Baked file has correct `upAxis` metadata (Y)
- [ ] Omniverse shows **no Resolve transforms** (ScaleunitsResolve/RotateunitsResolve = 0)
- [ ] Geometry size matches target unit (e.g., 2.7m → 270cm)
- [ ] Orientation is correct (Z-up → Y-up)
- [ ] Object position preserved (no world-space drift)
- [ ] Normals render correctly (no shading artifacts)
- [ ] xformOps cleared or not required on baked file

### Phase 3: Error Handling & Recovery Testing

**Objective**: Ensure robust error handling and recovery.

#### 3.1 Collection Errors
- [ ] Missing collection name → warning message
- [ ] Collection with no objects → appropriate handling
- [ ] Nested collection structures → recursive object inclusion
- [ ] Collection renamed after endpoint creation → error handling

#### 3.2 File Path Errors
- [ ] Empty filepath → validation error
- [ ] Invalid characters in path → clear error message
- [ ] Read-only directory → permission error
- [ ] Non-existent directory → auto-creation or error
- [ ] Relative vs absolute path handling

#### 3.3 Export Operation Errors
- [ ] USD export operator failure → detailed error context
- [ ] Insufficient disk space → clear error message
- [ ] Interrupted export → partial cleanup
- [ ] Memory issues with large scenes → graceful degradation

#### 3.4 Recovery Testing
- [ ] Export interruption → scene state restoration
- [ ] Multiple failures → partial success reporting
- [ ] Critical errors → safe failure without Blender crash

### Phase 4: Logging & Bug Report Testing

**Objective**: Validate logging system and bug report generation.

#### 4.1 Verbose Logging
- [ ] Verbose toggle enables detailed console output
- [ ] System information logged on operation start
- [ ] Step-by-step operation progress visible
- [ ] Timing information for performance analysis
- [ ] File size reporting on successful exports

#### 4.2 Bug Report Generation
- [ ] Bug report button creates JSON file
- [ ] File saved to Blender temp directory
- [ ] JSON contains system information
- [ ] Scene statistics included
- [ ] Recent operation logs captured
- [ ] Recent errors logged with context

#### 4.3 Error Context Logging
- [ ] Stack traces included for exceptions
- [ ] Operation context preserved
- [ ] Recovery suggestions provided
- [ ] Error classification (recoverable/critical)

### Phase 5: Performance & Scalability Testing

**Objective**: Ensure addon performs well under various loads.

#### 5.1 Performance Benchmarks
- [ ] Single endpoint: < 1 second export time
- [ ] 5 endpoints: < 5 seconds total
- [ ] 10 endpoints: < 15 seconds total
- [ ] Large scene (1000+ objects): < 30 seconds
- [ ] Memory usage remains reasonable

#### 5.2 Large Scene Handling
- [ ] Selective endpoint export (enable/disable toggles)
- [ ] Progress indication for long operations
- [ ] Cancellation support during export
- [ ] Efficient visibility operations

#### 5.3 Resource Usage
- [ ] CPU usage during export operations
- [ ] Memory consumption with large scenes
- [ ] Disk I/O patterns
- [ ] Temporary file cleanup

### Phase 6: Cross-Platform Compatibility Testing

**Objective**: Verify consistent behavior across platforms.

#### 6.1 Platform Testing
- [ ] **Windows**: Install from ZIP, full functionality
- [ ] **macOS**: Install from ZIP, full functionality
- [ ] **Linux**: Install from ZIP, full functionality
- [ ] Same ZIP file works on all platforms

#### 6.2 Path Handling
- [ ] Blender relative paths (`//export/file.usd`) resolve correctly
- [ ] Platform-specific path separators handled automatically
- [ ] UNC paths (Windows) work correctly
- [ ] Unix-style paths (macOS/Linux) work correctly

#### 6.3 File System Compatibility
- [ ] Unicode filenames supported
- [ ] Long path names handled
- [ ] Network drives accessible
- [ ] Case-sensitive filesystems (macOS/Linux) vs case-insensitive (Windows)

---

## 🐛 Bug Reporting Procedures

### During Testing: Immediate Actions

1. **Enable Verbose Logging**
   - Check the "Verbose Logging" toggle in the USD Multi Export panel

2. **Reproduce the Issue**
   - Perform the exact steps that caused the problem
   - Note any error messages in Blender's Info area
   - Copy console output if visible

3. **Generate Bug Report**
   - Click "Generate Bug Report" button immediately after error
   - Note the file path shown in the popup dialog
   - File will be saved as: `usdme_bug_report_YYYYMMDD_HHMMSS.json`

4. **Document Context**
   - Screenshot of the USD Multi Export panel
   - Screenshot of Blender's Info area
   - Current scene structure (Outliner view)
   - Blender version and system information

### Bug Report Contents

The generated JSON file contains:

```json
{
  "timestamp": "2025-12-23T10:30:45.123456",
  "bug_report_data": {
    "system_info": {
      "platform": "Windows-10-10.0.19041-SP0",
      "architecture": ["64bit", "WindowsPE"],
      "processor": "Intel64 Family 6 Model 158 Stepping 10, GenuineIntel",
      "python_version": "3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)]"
    },
    "blender_info": {
      "version": "5.0.0",
      "build_info": "Blender 5.0.0 (hash:abcd1234 built 2025-11-18)",
      "binary_path": "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
    },
    "scene_info": {
      "name": "TestScene.blend",
      "filepath": "C:\\Projects\\TestScene.blend",
      "objects_count": 45,
      "collections_count": 8,
      "usdme_endpoints_count": 3
    },
    "operation_log": [
      {
        "timestamp": "2025-12-23T10:30:40.000000",
        "level": "INFO",
        "message": "Started operation: batch_export",
        "context": {"total_endpoints": 3, "verbose_mode": true}
      }
    ],
    "recent_errors": []
  }
}
```

### Filing Bug Reports

**Required Information:**
- [ ] Generated JSON bug report file
- [ ] Steps to reproduce the issue
- [ ] Expected vs actual behavior
- [ ] Blender console output (if verbose logging was enabled)
- [ ] Screenshots of UI state and error messages
- [ ] Test scene file (if issue is scene-specific)

**Bug Report Template:**
```markdown
## Bug Report: [Brief Description]

### Environment
- **Blender Version**: 5.0.x
- **OS**: Windows/macOS/Linux [version]
- **Addon Version**: v0.1.3

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Error Messages
```
[Console output or Info area messages]
```

### Attachments
- [ ] Bug report JSON file
- [ ] Test scene file (if applicable)
- [ ] Screenshots
```

---

## 📊 Test Data Requirements

### Test Scenes

Create the following test scenes for comprehensive testing:

#### Scene 1: Basic Functionality
- 3-5 collections with simple objects
- Basic materials and textures
- Mixed object types (meshes, lights, cameras)

#### Scene 2: Complex Content
- Large scene (100+ objects)
- Complex materials (PBR, transparency, emission)
- Animation data
- Particle systems and modifiers

#### Scene 3: Error Scenarios
- Missing collections
- Invalid file paths
- Empty collections
- Corrupted data

#### Scene 4: Performance Testing
- 1000+ objects across multiple collections
- Heavy geometry and textures
- Complex scene hierarchy

### Test Assets

- **Textures**: Various formats (PNG, JPG, EXR, HDR)
- **Materials**: Simple diffuse, complex PBR, transparent, emissive
- **Geometry**: Simple primitives, complex meshes, instanced objects
- **Animation**: Object animation, armature animation, shape keys

---

## ✅ Phase Completion Checklist

### Pre-Testing Setup
- [ ] Blender 5.0+ installed and verified
- [ ] Addon ZIP created or development environment ready
- [ ] Test scenes created with required content
- [ ] Export directories created with proper permissions
- [ ] External text editor available for JSON review

### Phase 1 Completion
- [ ] Addon installation successful
- [ ] UI elements functional
- [ ] Basic endpoint management works
- [ ] Single endpoint export successful

### Phase 2 Completion
- [ ] Batch export functional
- [ ] All content types export correctly
- [ ] Scene state preservation verified

### Phase 3 Completion
- [ ] All error scenarios handled appropriately
- [ ] Recovery mechanisms functional
- [ ] No crashes during error conditions

### Phase 4 Completion
- [ ] Verbose logging provides detailed information
- [ ] Bug reports contain all required data
- [ ] Error context sufficient for debugging

### Phase 5 Completion
- [ ] Performance meets requirements
- [ ] Large scenes handled efficiently
- [ ] Resource usage acceptable

### Phase 6 Completion
- [ ] Windows testing completed
- [ ] macOS testing completed
- [ ] Linux testing completed
- [ ] Path handling verified on all platforms

---

## 📈 Test Metrics & Reporting

### Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Single endpoint export time | < 1s | ___ | ⏳ |
| 5 endpoint batch export time | < 5s | ___ | ⏳ |
| 10 endpoint batch export time | < 15s | ___ | ⏳ |
| Large scene (1000+ objects) | < 30s | ___ | ⏳ |
| Memory usage peak | < 2GB | ___ | ⏳ |

### Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Test case pass rate | 100% | ___ | ⏳ |
| Error scenario handling | 100% | ___ | ⏳ |
| Bug report completeness | 100% | ___ | ⏳ |
| Cross-platform compatibility | 100% | ___ | ⏳ |

### Coverage Metrics

| Test Category | Coverage Target | Actual | Status |
|---------------|-----------------|--------|--------|
| Basic functionality | 100% | ___ | ⏳ |
| Error handling | 100% | ___ | ⏳ |
| Performance | 100% | ___ | ⏳ |
| Compatibility | 100% | ___ | ⏳ |
| Logging & reporting | 100% | ___ | ⏳ |

---

## 🏁 Final Validation

### Release Readiness Checklist

- [ ] All testing phases completed successfully
- [ ] Performance requirements met
- [ ] No critical bugs remaining
- [ ] Documentation updated with known limitations
- [ ] Cross-platform compatibility verified
- [ ] Bug report system validated

### Post-Release Monitoring

- [ ] User feedback collection process established
- [ ] Bug report analysis workflow defined
- [ ] Performance monitoring in place
- [ ] Update process for future Blender versions

---

**Testing Plan Version**: v1.0.0
**Last Updated**: 23.12.2025
**Next Review**: After implementation completion