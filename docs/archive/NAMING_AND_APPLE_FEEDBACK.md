# Naming and Apple Perspective - Feedback Response

**Date**: 25.11.2025  
**Status**: Open Discussion  
**Feedback Source**: Apple User

---

## Feedback Summary

### 1. Naming Concern: "Blender_USD_StableExport"

**Issue**: The name "StableExport" implies that Blender's built-in USD export is not stable, which is not accurate and may be misleading.

**Current Name**: `Blender_USD_StableExport`

**Problem**: 
- "Stable" suggests the built-in export is unstable
- Doesn't clearly communicate the actual functionality (endpoint-based, multi-export)
- May create confusion about Blender's native USD export capabilities

**Proposed Alternatives**:

1. **`Blender_USD_EndpointExport`** ✅ (Recommended)
   - Clearly describes the endpoint-based functionality
   - Doesn't imply anything negative about Blender's export
   - Focuses on the unique feature (endpoints)

2. **`Blender_USD_MultiExport`**
   - Emphasizes the multi-endpoint batch export capability
   - Clear and descriptive

3. **`Blender_USD_EndpointManager`**
   - Emphasizes the management/organization aspect
   - Suggests workflow enhancement

4. **`Blender_USD_CompositionExport`**
   - References the composition arc workaround
   - May be too technical for some users

5. **`Blender_USD_BatchExport`**
   - Simple and clear
   - Focuses on batch functionality

**Recommendation**: **`Blender_USD_EndpointExport`** - Most accurately describes the core functionality without implying anything about Blender's built-in export stability.

---

### 2. Missing Apple Perspective

**Issue**: Nowhere in the project documentation does Apple's perspective on USD usage appear, despite Apple being a founding member of AOUSD (Alliance for OpenUSD).

**Current State**:
- Documentation focuses on Omniverse and general VFX pipelines
- No mention of Apple's USD workflows or requirements
- Missing Apple-specific use cases or considerations

**Apple's USD Context**:
- **Founding Member of AOUSD**: Apple co-founded the Alliance for OpenUSD in August 2023
- **Industry Leadership**: Apple plays a key role in USD standardization
- **Potential Use Cases**: 
  - AR/VR content creation (RealityKit, ARKit)
  - 3D asset pipelines for Apple platforms
  - Content creation tools integration
  - Cross-platform 3D workflows

**Required Actions**:

1. **Add Apple to User Profiles**:
   - Update questionnaire to include Apple-specific audience
   - Add Apple workflows section

2. **Add Apple Use Cases**:
   - AR/VR content creation workflows
   - RealityKit/ARKit integration
   - Apple platform asset pipelines
   - Cross-platform content creation

3. **Add Apple Requirements**:
   - Apple-specific USD structure requirements
   - RealityKit compatibility considerations
   - Apple platform integration needs

4. **Update Research Document**:
   - Add Apple's USD perspective section
   - Reference AOUSD and Apple's role
   - Include Apple-specific workflows

5. **Update README**:
   - Mention Apple/AOUSD in acknowledgments
   - Add Apple use cases to examples
   - Reference Apple's USD leadership role

---

## Proposed Changes

### Immediate Actions

1. **Rename Project** (if approved):
   - From: `Blender_USD_StableExport`
   - To: `Blender_USD_EndpointExport` (or alternative)
   - Update all references in documentation

2. **Add Apple Perspective Section**:
   - Create `APPLE_USD_PERSPECTIVE.md` document
   - Add Apple section to questionnaire
   - Update research document with Apple workflows
   - Add Apple to README acknowledgments

3. **Clarify Naming Intent**:
   - Update README to clarify that "stable" refers to reliable endpoint management, not Blender's export
   - Or rename to avoid confusion entirely

---

## Discussion Points

### Naming Decision

**Question**: Should we rename the project to better reflect its functionality?

**Options**:
- A) Rename to `Blender_USD_EndpointExport` (recommended)
- B) Keep current name but clarify intent in documentation
- C) Other suggestion: _________________

### Apple Perspective

**Question**: What specific Apple USD workflows should we document?

**Areas to Explore**:
- AR/VR content creation (RealityKit)
- Apple platform asset pipelines
- Cross-platform workflows
- AOUSD alignment requirements
- Apple-specific USD structure needs

---

## Next Steps

1. **Get Feedback**: Discuss naming alternatives with stakeholders
2. **Research**: Gather Apple USD workflow information
3. **Document**: Add Apple perspective to all relevant documents
4. **Update**: Rename project if consensus is reached
5. **Collaborate**: Engage with Apple users for specific requirements

---

## Decision Made

**✅ Project Renamed**: `Blender_USD_StableExport` → `Blender_USD_MultiExport`

**Reason**: The name "Stable Export" referred to reliable endpoint management and consistent export workflows, but it led to confusion as it could imply that Blender's built-in USD export is unstable (which is not the case - Blender's native USD export is stable and well-maintained). The new name "Multi Export" better reflects the core functionality: **multi-endpoint batch export capabilities**.

**Status**: ✅ Renamed and documented  
**Last Updated**: 25.11.2025

