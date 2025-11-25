# Blender USD Stable Export - Requirements Questionnaire

**Purpose**: This questionnaire is designed to gather detailed requirements for the Blender USD Stable Export addon. Complete this questionnaire before proceeding with detailed requirements definition, module design, and implementation planning.

**Status**: ✅ In Progress - Many requirements confirmed and moved to Detailed Requirements  
**Date Created**: 25.11.2025  
**Version**: v1.2.0  
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)

**Important**: Many requirements have been confirmed and moved to `02_Detailed_Requirements.md`. This questionnaire now focuses only on unanswered questions. See the Detailed Requirements document for all confirmed requirements.

**Note**: This questionnaire is designed to be useful from beginner level upwards. For production use, consider using an online survey tool (e.g., Google Forms, Typeform) for easier completion and result collation, rather than requiring GitHub fork/PR workflow.

---

## Instructions

- Answer all questions that apply to your use case
- Provide specific examples where possible
- **Indicate priority levels (Critical, High, Medium, Low) for features** - Focus on priority ordering rather than exhaustive feature lists
- Note any constraints or limitations
- Add additional notes or clarifications as needed
- **For Endpoint questions**: Review [usd-wg-assets guidelines](https://github.com/usd-wg/assets) and [VFX Reference Platform](https://vfxplatform.com/) for alignment with ASWF standards

---

## 1. User Profile & Context

### 1.1 Primary Users (Split USD vs Omniverse Audiences)

**Note**: USD and Omniverse are distinct audiences with different needs. Please indicate which audience(s) you represent.

- [ ] **Which audience do you represent?** (Select all that apply)
  - [ ] **USD Users** (working with USD files, USD-compatible tools, VFX pipelines)
  - [ ] **Omniverse Users** (working with NVIDIA Omniverse platform)
  - [ ] **Both** (working with both USD and Omniverse)

- [ ] **User Role** (Select all that apply)
  - [ ] 3D Artists/Modelers
  - [ ] Technical Artists
  - [ ] Pipeline Developers
  - [ ] TD/Technical Directors
  - [ ] Other: _________________

- [ ] **Blender Experience Level** (This addon should be useful from beginner upwards)
  - [ ] Beginner
  - [ ] Intermediate
  - [ ] Advanced
  - [ ] Expert

- [ ] **USD Experience Level** (For USD audience)
  - [ ] No experience
  - [ ] Basic (import/export)
  - [ ] Intermediate (composition, variants)
  - [ ] Advanced (custom schemas, pipelines)

- [ ] **Omniverse Experience Level** (For Omniverse audience)
  - [ ] No experience
  - [ ] Basic (using Omniverse apps)
  - [ ] Intermediate (Omniverse workflows, connectors)
  - [ ] Advanced (Omniverse extensions, custom pipelines)

### 1.2 Use Case Context
- [ ] **What is the primary use case?**
  - [ ] Exporting assets for Omniverse workflows
  - [ ] Exporting assets for other USD-compatible tools
  - [ ] Creating asset libraries
  - [ ] Pipeline integration
  - [ ] Other: _________________

- [ ] **What types of scenes will be exported?** (Select all that apply)
  - [ ] **Single assets** (1-10 objects) - Primary use case: Export individual assets for composition in Omniverse
  - [ ] **Small scenes** (1-40 objects) - Single to a couple of assets
  - [ ] **Medium scenes** (40-100 objects) - Multiple assets
  - [ ] **Large scenes** (100-1000 objects) - May require automation/scripting to define endpoints
  - [ ] **Very large scenes** (> 1000 objects) - Requires automation/scripting to define endpoints
  
- [ ] **Scene animation type:**
  - [ ] Static scenes (no animation)
  - [ ] Animated scenes (with animation)
  - [ ] Mixed (both animated and static endpoints)
  
**Note**: Blender is typically used to generate single assets that are then composed in Omniverse. For scenes with 1000+ objects, automated endpoint definition via scripting may be required. Focus is on single assets to small collections (1-40 objects).

- [ ] **How many endpoints per scene (typical)?**
  - [ ] 1 endpoint (single asset export)
  - [ ] 2-5 endpoints (small asset collection)
  - [ ] 6-10 endpoints (medium asset collection)
  - [ ] 11-20 endpoints (large asset collection)
  - [ ] 20+ endpoints (very large - may require automation)

- [ ] **For large scenes (1000+ objects), should the addon support:**
  - [ ] Automated endpoint definition via scripting/Python API (priority: ___)
  - [ ] Batch endpoint creation from collections (priority: ___)
  - [ ] Import/export endpoint configurations (priority: ___)
  - [ ] Template-based endpoint generation (priority: ___)
  - [ ] Not needed - focus on single assets only

---

## 2. Endpoint Definition & Management

**Note**: For production alignment, review:
- [usd-wg-assets guidelines](https://github.com/usd-wg/assets) - USD asset organization standards
- [VFX Reference Platform](https://vfxplatform.com/) - Industry standards alignment
- **Goal**: Align with ASWF (Academy Software Foundation) standards to avoid parsing multiple structures

### 2.1 Endpoint Selection Methods
- [ ] **How should users define endpoints?** (Select all that apply, **prioritize**)
  - [ ] By Collection (priority: ___)
  - [ ] By Object selection (priority: ___)
  - [ ] By custom property markers (priority: ___)
  - [ ] By naming convention (priority: ___)
  - [ ] By view layer (priority: ___)
  - [ ] Aligned with usd-wg-assets structure (priority: ___)
  - [ ] Other: _________________ (priority: ___)

- [ ] **Should endpoints support nested collections?**
  - [ ] Yes, include all nested collections automatically
  - [ ] Yes, but allow user to choose nested inclusion
  - [ ] No, only direct collection members

- [ ] **Should endpoints support multiple collections?**
  - [ ] Yes, allow combining multiple collections into one endpoint
  - [ ] No, one collection per endpoint

### 2.2 Endpoint Properties
- [ ] **What properties should each endpoint have?** (Select all that apply)
  - [ ] Name (required: Yes/No)
  - [ ] Description/Notes (required: Yes/No)
  - [ ] Export filepath (required: Yes/No)
  - [ ] Root prim path (required: Yes/No, default: ___)
  - [ ] Export preset/template (required: Yes/No)
  - [ ] Custom export options (required: Yes/No)
  - [ ] Tags/Labels (required: Yes/No)
  - [ ] Other: _________________

- [ ] **Should endpoints support filepath patterns/tokens?**
  - [ ] Yes, support tokens like {collection_name}, {date}, {version}
  - [ ] No, static filepaths only

**Note**: Endpoints are saved with the .blend file (scene-specific) and support enable/disable toggle. See `02_Detailed_Requirements.md` for confirmed requirements.

### 2.3 Endpoint Organization
- [ ] **How should endpoints be organized/managed?**
  - [ ] Simple list (add, remove, reorder)
  - [ ] Grouped by category/type
  - [ ] Hierarchical organization
  - [ ] Tagged/labeled system
  - [ ] Other: _________________

---

## 3. Export Functionality

**Note**: Assume all Blender 5.0 USD export options are available. **Focus on priority ordering** rather than exhaustive feature lists.

### 3.1 Export Options (Priority Ordering)

**Note**: All USD export options are available per endpoint (all enabled by default), export presets are supported (predefined + user-defined), and export options support both global defaults and per-endpoint overrides. See `02_Detailed_Requirements.md` section "Export Functionality Requirements" for confirmed requirements.

### 3.2 Export Workflow
- [ ] **How should export be triggered?**
  - [ ] Export all endpoints (single button)
  - [ ] Export selected endpoint(s)
  - [ ] Export active endpoint
  - [ ] Export via menu (File > Export)
  - [ ] Export via keyboard shortcut
  - [ ] All of the above
  - [ ] Other: _________________

**Note**: Batch export operations are supported (with progress indicator and cancellation), all export feedback options are required (progress, current endpoint, cancellation, export log), and all validation is performed automatically in the background with errors logged and displayed as warnings. See `02_Detailed_Requirements.md` sections "Export Functionality Requirements" and "Error Handling & Feedback Requirements" for confirmed requirements.

### 3.3 Export Validation

**Note**: All validation checks are performed automatically in the background, and validation errors are logged and displayed as warnings. See `02_Detailed_Requirements.md` section "Export Functionality Requirements" for confirmed requirements.

---

## 4. User Interface

### 4.1 UI Location
- [ ] **Where should the addon UI be located?** (Select all that apply)
  - [ ] Properties Panel > Scene Properties tab
  - [ ] Properties Panel > Object Properties tab
  - [ ] Properties Panel > Collection Properties tab
  - [ ] 3D Viewport > N-Panel (Sidebar)
  - [ ] Custom menu (File > Export > USD Endpoints)
  - [ ] Separate window/panel
  - [ ] Other: _________________

**Note**: UI uses collapsible sections (collapsed as default with presets), endpoints are displayed as simple list with add/remove buttons and tree view option, and all endpoint information is visible in the list. See `02_Detailed_Requirements.md` section "User Interface Requirements" for confirmed requirements.

### 4.2 Endpoint Management UI

**Note**: Endpoint display and information visibility requirements are confirmed. See `02_Detailed_Requirements.md` section "User Interface Requirements" for details.

- [ ] **How should users edit endpoint properties?**
  - [ ] Inline editing in list
  - [ ] Expandable details panel
  - [ ] Separate dialog window
  - [ ] Properties panel integration
  - [ ] Other: _________________

### 4.3 Export UI

**Note**: All export controls are required (Export All, Export Selected, Export Active, Export defined Endpoints, progress indicator, export log/results, export settings/preferences). See `02_Detailed_Requirements.md` section "User Interface Requirements" for confirmed requirements.

### 4.4 Support & Feedback UI

**Note**: Support buttons (Bug Report, Feature Request, Documentation, Help/Support) are required in an extra tab/expandable section, bug report opens GitHub Issues with pre-filled template, and all system/scene information is auto-collected. See `02_Detailed_Requirements.md` section "User Interface Requirements" for confirmed requirements.

---

## 5. Error Handling & Feedback

### 5.1 Error Reporting

**Note**: Error reporting follows best practices (popup for critical errors, status messages, Blender info area, log file, console output), and both simple and detailed error messages are available. See `02_Detailed_Requirements.md` section "Error Handling & Feedback Requirements" for confirmed requirements.

### 5.2 Success Feedback

**Note**: All success feedback methods are required (status message, notification popup, visual indicator, export log). See `02_Detailed_Requirements.md` section "Error Handling & Feedback Requirements" for confirmed requirements.

### 5.3 Logging

**Note**: Export operations are logged to file (next to exported files, time tag in filename), and all relevant information is logged. See `02_Detailed_Requirements.md` section "Error Handling & Feedback Requirements" for confirmed requirements.

---

## 6. Performance & Scalability

**Note**: Performance and Scalability are **basic requirements**, not optional features. These must be addressed in the core design.

### 6.1 Performance Requirements (Basic Requirements)
- [ ] **What are acceptable export times?** (Required - not optional)
  - [ ] < 1 second per endpoint (priority: ___)
  - [ ] < 5 seconds per endpoint (priority: ___)
  - [ ] < 30 seconds per endpoint (priority: ___)
  - [ ] No specific requirement (not recommended)

**Note**: UI shows progress and allows cancellation during export. See `02_Detailed_Requirements.md` section "Performance Requirements" for confirmed requirements.

### 6.2 Large Scene Handling (Basic Requirements)

**Note**: All large scene handling requirements are confirmed (optimize visibility operations, selective export, progress indicators, cancellation, efficient state management, batch export optimization). See `02_Detailed_Requirements.md` section "Performance Requirements" for confirmed requirements.

---

## 7. Integration & Compatibility

### 7.1 Blender Version Support
- [x] **Which Blender versions should be supported?**
  - [x] Blender 5.0+ only (officially released November 18, 2025) - **CONFIRMED**
  - [x] Blender 5.0+ and future versions (with version checks) - **CONFIRMED**
  - [ ] Blender 5.0+ and 4.x (backward compatibility) - **NOT RECOMMENDED**
  
  **Note**: Blender 4.x versions are deprecated. The addon targets Blender 5.0+ only.
  
  **Blender 5.0 USD Export Key Points:**
  - Only visible objects can be exported (no invisible object export)
  - No USD composition arcs authoring (layers, variants, references)
  - Supported data types: meshes, cameras (perspective), curves, text (as meshes), lights, hair (as curves), point clouds, metaballs (animated meshes), volumes, armatures
  - Experimental instancing support (objects, collections, partial geometry node point instances)
  - Material handling via USD Preview Surface (color, metallic, roughness)
  - HDR and wide-gamut color management may affect material appearance
  - Limitations: no absolute shape keys in animation, no bendy bones in armatures

### 7.2 Other Addon Compatibility

**Note**: We cannot promise compatibility with unknown elements outside our direct influence in uncontrollable combinations. This section focuses on **known conflicts** and **non-intrusive design principles** rather than promises.

- [ ] **Known conflicts to avoid:**
  - [ ] List known conflicting addons: _________________
  - [ ] List known conflicting features: _________________

- [ ] **Non-intrusive design principles:**
  - [ ] Use Blender's standard addon patterns
  - [ ] Avoid modifying global Blender settings
  - [ ] Use isolated namespaces for custom properties
  - [ ] Document known conflicts if discovered
  - [ ] Other: _________________

**Note**: Non-intrusive design principles are confirmed. See `02_Detailed_Requirements.md` section "Compatibility Requirements" for confirmed requirements. We cannot guarantee compatibility with all addons. Focus on non-intrusive design and documenting known conflicts.

### 7.3 Pipeline Integration

**Note**: This section mixes **basic requirements** (CLI, Python API) with **optional features** (external tool integration). Please indicate which are requirements vs. nice-to-have.

#### Basic Requirements (Must Have) - **DEFERRED TO v2.0**
- [ ] **Command-line/batch export** (Required: Yes/No, priority: ___) - **DEFERRED TO v2.0**
  - [ ] Support headless Blender execution
  - [ ] Support batch script execution
  - [ ] Support command-line arguments

- [ ] **Python API for scripting** (Required: Yes/No, priority: ___) - **DEFERRED TO v2.0**
  - [ ] Programmatic endpoint creation
  - [ ] Programmatic export execution
  - [ ] Access to export results/status
  - [ ] Other: _________________

#### Optional Features (Nice to Have) - **DEFERRED TO v2.0**
- [ ] **Integration with external tools** (Required: Yes/No, priority: ___) - **DEFERRED TO v2.0**
  - [ ] Asset management systems
  - [ ] Version control systems
  - [ ] CI/CD pipelines
  - [ ] Other: _________________

- [ ] **Custom property reading/writing** (Required: Yes/No, priority: ___) - **DEFERRED TO v2.0**
  - [ ] Read custom properties from objects
  - [ ] Write custom properties to USD
  - [ ] Custom metadata handling
  - [ ] Other: _________________

---

## 8. Advanced Features (Future Considerations)

### 8.1 USD Composition

**Note**: USD composition features are out-of-scope for v1.0. Focus on simple export only. See `02_Detailed_Requirements.md` section "Out-of-Scope for v1.0" for details.

### 8.2 Metadata & Customization

**Note**: Custom metadata and custom export hooks are out-of-scope for v1.0. Standard properties and standard export only. See `02_Detailed_Requirements.md` section "Out-of-Scope for v1.0" for details.

### 8.3 Asset Management

**Note**: Asset management integration is out-of-scope for v1.0. See `02_Detailed_Requirements.md` section "Out-of-Scope for v1.0" for details.

---

## 9. Documentation & Support

### 9.1 Documentation Needs
- [ ] **What documentation is needed?** - **ROADMAP: More documentation planned for later**
  - [ ] User manual/guide - **ROADMAP**
  - [ ] Quick start tutorial - **ROADMAP**
  - [ ] Video tutorials - **ROADMAP**
  - [ ] API documentation (for developers) - **ROADMAP**
  - [ ] Example scenes - **ROADMAP**
  - [ ] Troubleshooting guide - **ROADMAP**

### 9.2 Help & Support
- [ ] **How should users get help?** - **ROADMAP: Enhanced help features planned**
  - [ ] Built-in tooltips - **ROADMAP**
  - [ ] Help button linking to docs - **ROADMAP**
  - [ ] Example scenes with comments - **ROADMAP**
  - [ ] Support forum/community - **ROADMAP**

---

## 10. Constraints & Limitations

### 10.1 Technical Constraints
- [ ] **Are there any technical constraints?** - **ROADMAP: Additional OS support planned for later**
  - [ ] Must work on Windows only
  - [ ] Must work on Linux only
  - [ ] Must work on macOS only
  - [ ] Cross-platform required - **ROADMAP: Additional OS support planned**
  - [ ] Python version requirements: 3.11+ (bundled with Blender 5.0)
  - [ ] Other: _________________

### 10.2 Workflow Constraints
- [ ] **Are there workflow constraints?**
  - [ ] Must not modify original scene
  - [ ] Must support undo/redo
  - [ ] Must be non-destructive
  - [ ] Must work in headless mode
  - [ ] Other: _________________

### 10.3 Resource Constraints
- [ ] **Are there resource constraints?**
  - [ ] Memory limitations
  - [ ] Disk space considerations
  - [ ] Performance requirements
  - [ ] Other: _________________

---

## 11. Priority & Phasing

### 11.1 Feature Priority
- [ ] **Which features are critical for v1.0?**
  List top 5-10 critical features:
  1. _________________
  2. _________________
  3. _________________
  4. _________________
  5. _________________

- [ ] **Which features can wait for v2.0?**
  List features for future versions:
  1. _________________
  2. _________________
  3. _________________

### 11.2 Implementation Phases
- [ ] **Should the addon be released in phases?**
  - [ ] Yes, MVP first, then enhancements
  - [ ] No, full feature set in v1.0

- [ ] **If phased, what should be in Phase 1 (MVP)?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

---

## 12. Additional Notes & Requirements

### 12.1 Special Requirements
- [ ] **Any special requirements not covered above?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 12.2 Use Case Examples
- [ ] **Please provide 2-3 specific use case examples:**
  
  **Example 1:**
  - Scenario: _________________
  - Expected workflow: _________________
  - Expected outcome: _________________

  **Example 2:**
  - Scenario: _________________
  - Expected workflow: _________________
  - Expected outcome: _________________

  **Example 3:**
  - Scenario: _________________
  - Expected workflow: _________________
  - Expected outcome: _________________

---

## 13. What Did We Miss?

### 13.1 Additional Features
- [ ] **Are there any features or capabilities not covered in the previous sections?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.2 Edge Cases & Scenarios
- [ ] **Are there specific edge cases or scenarios that should be considered?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.3 Integration Points
- [ ] **Are there integration points with other tools or workflows not mentioned?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.4 User Workflow Considerations
- [ ] **Are there workflow considerations or user habits that should be accommodated?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.5 Technical Considerations
- [ ] **Are there technical considerations or constraints not covered?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.6 Naming & Conventions
- [ ] **Are there naming conventions or standards that should be followed?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________
  - **Note**: See [Naming Conventions](NAMING_CONVENTIONS.md) for USD/Omniverse reserved names

### 13.7 Future-Proofing
- [ ] **Are there considerations for future Blender or USD versions?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________
  - **Note**: See [Research Document - Blender 5.0 Readiness](Blender_USD_StableExport_RESEARCH.md#blender-50-readiness-and-compatibility-planning) for planned compatibility review

### 13.8 Open Questions
- [ ] **What questions or uncertainties remain?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 13.9 Additional Feedback
- [ ] **Any other feedback, suggestions, or concerns?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

---

## 14. Existing Solutions & User Needs

**Note**: This section is refocused on **user needs** rather than author research. What solutions have you (the user) tried? What gaps exist from your perspective?

### 14.1 User Experience with Existing Solutions
- [ ] **Have you tried existing Blender USD export solutions?**
  - [ ] Yes, Blender's built-in USD exporter
  - [ ] Yes, other Blender addons: _________________
  - [ ] Yes, external tools: _________________
  - [ ] No, this would be my first USD export solution

- [ ] **What gaps or limitations have you encountered?** (From user perspective)
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

- [ ] **What features are missing that you need?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.2 User Requirements Not Met by Existing Solutions
- [ ] **What specific needs are not addressed by existing solutions?**
  - [ ] Endpoint-based export workflow
  - [ ] Batch export of multiple scene parts
  - [ ] Better integration with your pipeline
  - [ ] Specific export options: _________________
  - [ ] Other: _________________

- [ ] **What would make this addon valuable to you?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.3 User Workflow Integration
- [ ] **How would this addon fit into your current workflow?**
  - [ ] Replace existing solution
  - [ ] Complement existing solution
  - [ ] New workflow entirely
  - [ ] Other: _________________

- [ ] **What would make adoption easier for you?**
  - [ ] Documentation
  - [ ] Example scenes
  - [ ] Tutorial videos
  - [ ] Pipeline integration examples
  - [ ] Other: _________________

---

## Completion Checklist

- [ ] All relevant sections completed (1-14)
- [ ] **Priorities assigned to features** (focus on priority ordering)
- [ ] Use case examples provided
- [ ] Constraints documented
- [ ] **User needs documented** (Section 14 - user-focused, not author research)
- [ ] **Performance requirements specified** (Section 6 - basic requirements)
- [ ] **Pipeline integration requirements clarified** (Section 7.3 - basic vs optional)
- [ ] Ready for requirements analysis

---

## Alternative: Online Survey Tool

**Note**: For easier completion and result collation, consider using an online survey tool (e.g., Google Forms, Typeform, SurveyMonkey) instead of requiring GitHub fork/PR workflow. This makes it easier for users to complete and for you to collate results, especially if many people respond.

**Benefits of Online Survey:**
- Easier for users to complete
- Automatic result collation
- Better data analysis tools
- No GitHub workflow required
- Can be shared easily via link

**If using online survey:**
- Link to survey: _________________
- Survey completion deadline: _________________

---

## Next Steps

Once this questionnaire is completed:

1. ✅ **Requirements Analysis** → Create detailed requirements list (`02_Detailed_Requirements.md`)
2. ✅ **Module Design** → Define addon modules (`03_Module_Design.md`)
3. ✅ **Implementation Plan** → Create step-by-step implementation plan (`04_Implementation_Plan.md`)

---

**Document Status**: ✅ In Progress - Confirmed requirements moved to Detailed Requirements  
**Last Updated**: 25.11.2025

