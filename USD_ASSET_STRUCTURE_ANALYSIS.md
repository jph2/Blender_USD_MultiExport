# USD Asset Structure Guidelines - Relevance Analysis

**Date**: 25.11.2025  
**Version**: v1.0.0  
**Status**: Analysis Document

---

## Overview

This document analyzes the relevance of two key USD asset structuring resources for the Blender USD Stable Export project:

1. **[ASWF USD Working Group - Guidelines for Structuring USD Assets](https://lf-aswf.atlassian.net/wiki/spaces/WGUSD/pages/11273723/Guidelines+for+Structuring+USD+Assets)**
2. **[USD-WG Assets - Intent-VFX Repository](https://github.com/usd-wg/assets/tree/main/intent-vfx)**

---

## 1. ASWF USD Working Group Guidelines

### Resource Location
- **Primary**: [Atlassian Wiki](https://lf-aswf.atlassian.net/wiki/spaces/WGUSD/pages/11273723/Guidelines+for+Structuring+USD+Assets)
- **GitHub**: [usd-wg/assets - asset-structure-guidelines.md](https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md)

### Key Concepts Relevant to Our Project

#### 1.1 Component vs Assembly Models

**Guideline Definition**:
- **Component**: Self-contained assets with geometry behind a payload; publishable assets that keep geometry deferred
- **Assembly**: Assets that reference components or other assemblies; used for composition

**Relevance to Blender USD Stable Export**:
- ✅ **CRITICAL**: Our "endpoints" are essentially **Component models**
- ✅ Each exported endpoint should be structured as a Component
- ✅ Components should have:
  - Component `kind` on the root prim
  - Payload for geometry (deferrable)
  - Self-contained/portable structure
  - Inherit from at least one Class prim

**Implementation Impact**:
- Need to set `kind` metadata on root prim: `component` or `assembly`
- Consider payload structure (though Blender 5.0 has limitations)
- Root prim should be an Xform with `defaultPrim` set

#### 1.2 Primitive Hierarchy

**Guideline Recommendations**:
- Use **Scopes** for organizing primitives (avoid unnecessary Xforms)
- Shorter names help with prim path inspection
- Set Purpose on Scope primitives (cleaner than individual gprim purposes)
- Transform ("Xformable") prim at root as `defaultPrim`

**Relevance to Our Project**:
- ✅ **HIGH**: Affects how we structure exported USD hierarchy
- ✅ Should use Scopes for organization (`geo`, `mtl`, etc.)
- ✅ Root prim should be an Xform, not a Scope
- ✅ Purpose should be set appropriately

**Implementation Impact**:
- Root prim path generation should create Xform primitives
- Consider organizing geometry under Scope primitives
- Set Purpose metadata correctly (render, proxy, guide)

#### 1.3 Root Prim Naming

**Guideline**: Root prim should follow asset naming conventions

**Relevance to Our Project**:
- ✅ **CRITICAL**: Already identified in our requirements (REQ-EXP-006)
- ✅ Our `RootPrimPathGenerator` should follow these conventions
- ✅ Endpoint name "MyChair" → root prim `/MyChair` (already planned)

**Implementation Impact**:
- Enforce naming convention: endpoint name → root prim path
- Avoid collisions: `/Mesh`, `/root`, `/World` (already documented in NAMING_CONVENTIONS.md)

#### 1.4 File Organization & Composition

**Guideline Recommendations**:
- Use `.usd` extension for root file (allows ascii/binary switching)
- Organize layers by department/work/contribution
- Store layers as child directories with relative paths (portability)
- Bare minimum: `asset.usd` and `payload.usd`

**Relevance to Our Project**:
- ⚠️ **LIMITED**: Blender 5.0 doesn't support composition arcs natively
- ⚠️ We export single USD files, not multi-layer structures
- ✅ **File naming**: Should use `.usd` extension (supports ascii/binary)
- ✅ **Portability**: Store paths relative to blend file (already planned)

**Implementation Impact**:
- Export as `.usd` files (not `.usdc` or `.usda` exclusively)
- Consider future support for multi-layer exports (v2.0+)
- Document that we export "atomic" components, not full asset structures

#### 1.5 Materials Organization

**Guideline**: Materials must be encapsulated within the asset's root primitive, but may reference global libraries

**Relevance to Our Project**:
- ✅ **HIGH**: Materials are exported with geometry
- ✅ Material references should be under root prim
- ⚠️ Blender exports `UsdPreviewSurface` (not MDL) - documented limitation

**Implementation Impact**:
- Ensure materials are under root prim hierarchy
- Material paths should be relative/portable
- Document USD Preview Surface limitation

#### 1.6 Payloads

**Guideline**: Heavy geometry should be behind payloads; components should have their own payloads

**Relevance to Our Project**:
- ⚠️ **LIMITED**: Blender 5.0 USD export has limited payload control
- ✅ **Future consideration**: May want to support payload structure in v2.0+
- ⚠️ Current Blender export doesn't easily support payload authoring

**Implementation Impact**:
- Document payload limitations in current implementation
- Consider payload support as future enhancement
- For now, export geometry directly (not behind payload)

#### 1.7 Inherits and Classes

**Guideline**: Models should inherit from at least one Class primitive for flexibility

**Relevance to Our Project**:
- ⚠️ **FUTURE**: Not critical for v1.0 (simple export)
- ✅ **v2.0 consideration**: Class inheritance for asset flexibility
- ⚠️ Blender 5.0 export doesn't easily support inherits authoring

**Implementation Impact**:
- Document as out-of-scope for v1.0
- Plan for v2.0+ if needed
- Focus on basic component structure first

---

## 2. USD-WG Assets - Intent-VFX Repository

### Resource Location
- **GitHub**: [usd-wg/assets/tree/main/intent-vfx](https://github.com/usd-wg/assets/tree/main/intent-vfx)

### Purpose
Contains sample USD assets demonstrating VFX-focused implementations of the structuring guidelines.

### Relevance to Our Project

#### 2.1 Practical Examples

**Value**:
- ✅ **HIGH**: Real-world examples of properly structured USD assets
- ✅ Shows how guidelines are applied in practice
- ✅ Reference for testing our exports

**Use Cases**:
- Compare our exported USD structure against these examples
- Validate that our exports follow industry standards
- Use as test cases for import/validation

#### 2.2 Structure Patterns

**What We Can Learn**:
- How components are organized in practice
- Material organization patterns
- Geometry hierarchy examples
- Variant usage (if applicable)

**Implementation Impact**:
- Use examples as validation targets
- Document structure comparisons
- Create test cases based on examples

#### 2.3 VFX Pipeline Alignment

**Value**:
- ✅ **HIGH**: Aligns with our VFX/Omniverse audience
- ✅ Demonstrates production-ready structures
- ✅ Shows integration patterns

**Implementation Impact**:
- Ensure our exports are compatible with VFX pipelines
- Test against VFX reference platform requirements
- Document VFX-specific considerations

---

## 3. Direct Relevance Summary

### Critical (Must Implement)

1. **Component Model Structure**
   - Set `kind` metadata: `component` on root prim
   - Root prim as Xform with `defaultPrim`
   - Self-contained structure

2. **Root Prim Naming**
   - Enforce naming convention (endpoint name → root prim path)
   - Avoid collisions (`/World`, `/environment`, `/Mesh`)

3. **Primitive Hierarchy**
   - Use Scopes for organization
   - Root prim as Xform
   - Set Purpose appropriately

### High Priority (Should Implement)

4. **File Naming**
   - Use `.usd` extension (allows ascii/binary switching)

5. **Materials Organization**
   - Materials under root prim hierarchy
   - Relative/portable paths

6. **Purpose Setting**
   - Set Purpose on Scope primitives
   - Support render/proxy/guide purposes

### Medium Priority (Consider for v1.0)

7. **Structure Validation**
   - Validate exported structure against guidelines
   - Compare with intent-vfx examples

8. **Documentation**
   - Document alignment with ASWF guidelines
   - Reference intent-vfx examples

### Future (v2.0+)

9. **Payload Support**
   - Support payload structure for heavy geometry

10. **Class Inheritance**
    - Support inherits from Class primitives

11. **Multi-Layer Structure**
    - Support multi-layer asset organization

---

## 4. Implementation Recommendations

### For v1.0 (Current Scope)

**Must Do**:
1. ✅ Set `kind` metadata on root prim (`component`)
2. ✅ Root prim as Xform (not Scope)
3. ✅ Enforce root prim naming convention
4. ✅ Use `.usd` file extension
5. ✅ Set Purpose metadata appropriately
6. ✅ Organize geometry under Scopes (if possible)

**Should Do**:
1. ✅ Validate structure against guidelines
2. ✅ Document alignment with ASWF standards
3. ✅ Reference intent-vfx examples in documentation

**Cannot Do** (Blender 5.0 Limitations):
1. ❌ Multi-layer composition
2. ❌ Payload authoring (limited control)
3. ❌ Inherits authoring (limited control)
4. ❌ Variants authoring (not supported)

### For v2.0+ (Future Enhancements)

1. **Payload Support**: Allow geometry to be behind payloads
2. **Class Inheritance**: Support inherits from Class primitives
3. **Multi-Layer Export**: Support multi-layer asset structures
4. **Structure Validation**: Automated validation against guidelines
5. **Template System**: Pre-configured structures based on guidelines

---

## 5. Documentation Updates Needed

### Update These Documents:

1. **`02_Detailed_Requirements.md`**
   - Add requirement: Set `kind` metadata on root prim
   - Add requirement: Root prim as Xform
   - Add requirement: Use Scopes for organization
   - Reference ASWF guidelines

2. **`03_Module_Design.md`**
   - Update `RootPrimPathGenerator` to set `kind` metadata
   - Ensure root prim is Xform, not Scope
   - Add Purpose setting logic

3. **`04_Implementation_Plan.md`**
   - Add tasks for `kind` metadata setting
   - Add tasks for Purpose setting
   - Add validation tasks against guidelines

4. **`Blender_USD_StableExport_RESEARCH.md`**
   - Add section on ASWF guidelines alignment
   - Reference intent-vfx examples
   - Document structure requirements

5. **`README.md`**
   - Add reference to ASWF guidelines
   - Mention alignment with industry standards

---

## 6. References

### Primary Resources

1. **ASWF USD Working Group Guidelines**
   - Wiki: https://lf-aswf.atlassian.net/wiki/spaces/WGUSD/pages/11273723/Guidelines+for+Structuring+USD+Assets
   - GitHub: https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md

2. **USD-WG Assets - Intent-VFX**
   - GitHub: https://github.com/usd-wg/assets/tree/main/intent-vfx

### Related Resources

3. **VFX Reference Platform**
   - https://vfxplatform.com/

4. **USD-WG Assets Repository**
   - https://github.com/usd-wg/assets

---

## 7. Action Items

### Immediate (v1.0)

- [ ] Add `kind` metadata requirement to Detailed Requirements
- [ ] Update RootPrimPathGenerator design to set `kind`
- [ ] Add Purpose setting logic to module design
- [ ] Update implementation plan with structure tasks
- [ ] Add ASWF guidelines reference to README
- [ ] Review intent-vfx examples for validation targets

### Future (v2.0+)

- [ ] Research payload support in Blender USD export
- [ ] Plan Class inheritance support
- [ ] Design multi-layer export structure
- [ ] Create structure validation system
- [ ] Build template system based on guidelines

---

**Last Updated**: 25.11.2025  
**Next Review**: After v1.0 implementation

