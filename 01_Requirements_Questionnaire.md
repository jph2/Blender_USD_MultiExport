# Blender USD Stable Export - Requirements Questionnaire

**Purpose**: This questionnaire is designed to gather detailed requirements for the Blender USD Stable Export addon. Complete this questionnaire before proceeding with detailed requirements definition, module design, and implementation planning.

**Status**: ⏳ Pending completion  
**Date Created**: 25.11.2025  
**Version**: v1.0.0
**your name** ( name of the person completing the questionnaire):

---

## Instructions

- Answer all questions that apply to your use case
- Provide specific examples where possible
- Indicate priority levels (Critical, High, Medium, Low) for features
- Note any constraints or limitations
- Add additional notes or clarifications as needed

---

## 1. User Profile & Context

### 1.1 Primary Users
- [ ] **Who are the primary users?**
  - [ ] 3D Artists/Modelers
  - [ ] Technical Artists
  - [ ] Pipeline Developers
  - [ ] Other: _________________

- [ ] **What is their Blender experience level?**
  - [ ] Beginner
  - [ ] Intermediate
  - [ ] Advanced
  - [ ] Expert

- [ ] **What is their USD/Omniverse experience level?**
  - [ ] No experience
  - [ ] Basic (import/export)
  - [ ] Intermediate (composition, variants)
  - [ ] Advanced (custom schemas, pipelines)

### 1.2 Use Case Context
- [ ] **What is the primary use case?**
  - [ ] Exporting assets for Omniverse workflows
  - [ ] Exporting assets for other USD-compatible tools
  - [ ] Creating asset libraries
  - [ ] Pipeline integration
  - [ ] Other: _________________

- [ ] **What types of scenes will be exported?**
  - [ ] Simple scenes (< 100 objects)
  - [ ] Medium scenes (100-1000 objects)
  - [ ] Large scenes (> 1000 objects)
  - [ ] Animated scenes
  - [ ] Static scenes
  - [ ] Mixed (both animated and static)

- [ ] **How many endpoints per scene (typical)?**
  - [ ] 1-3 endpoints
  - [ ] 4-10 endpoints
  - [ ] 11-20 endpoints
  - [ ] 20+ endpoints

---

## 2. Endpoint Definition & Management

### 2.1 Endpoint Selection Methods
- [ ] **How should users define endpoints?** (Select all that apply, prioritize)
  - [ ] By Collection (highest priority: ___)
  - [ ] By Object selection (priority: ___)
  - [ ] By custom property markers (priority: ___)
  - [ ] By naming convention (priority: ___)
  - [ ] By view layer (priority: ___)
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

- [ ] **Should endpoints be saved with the .blend file?**
  - [ ] Yes, endpoints are scene-specific
  - [ ] Yes, but allow saving/loading presets
  - [ ] No, endpoints are session-only

### 2.3 Endpoint Organization
- [ ] **How should endpoints be organized/managed?**
  - [ ] Simple list (add, remove, reorder)
  - [ ] Grouped by category/type
  - [ ] Hierarchical organization
  - [ ] Tagged/labeled system
  - [ ] Other: _________________

- [ ] **Should endpoints support enable/disable toggle?**
  - [ ] Yes, allow disabling endpoints without deleting
  - [ ] No, delete to remove

---

## 3. Export Functionality

### 3.1 Export Options
- [ ] **Which USD export options should be exposed per endpoint?** (Select all that apply)
  - [ ] Export animation (Yes/No)
  - [ ] Export materials (Yes/No)
  - [ ] Export textures (Yes/No)
  - [ ] Export cameras (Yes/No)
  - [ ] Export lights (Yes/No)
  - [ ] Export armatures (Yes/No)
  - [ ] Export shape keys (Yes/No)
  - [ ] Export hair/curves (Yes/No)
  - [ ] Export UV maps (Yes/No)
  - [ ] Export normals (Yes/No)
  - [ ] Export mesh colors (Yes/No)
  - [ ] Export custom properties (Yes/No)
  - [ ] Use instancing (Yes/No)
  - [ ] Export subdivision (Yes/No, method: ___)
  - [ ] Evaluation mode (Render/Viewport)
  - [ ] Other: _________________

- [ ] **Should there be export presets?**
  - [ ] Yes, predefined presets (e.g., "Full Export", "Geometry Only", "Materials Only")
  - [ ] Yes, user-defined presets
  - [ ] No, configure each time

- [ ] **Should export options be:**
  - [ ] Per-endpoint (each endpoint has its own settings)
  - [ ] Global defaults (all endpoints use same settings)
  - [ ] Both (global defaults, per-endpoint overrides)

### 3.2 Export Workflow
- [ ] **How should export be triggered?**
  - [ ] Export all endpoints (single button)
  - [ ] Export selected endpoint(s)
  - [ ] Export active endpoint
  - [ ] Export via menu (File > Export)
  - [ ] Export via keyboard shortcut
  - [ ] All of the above
  - [ ] Other: _________________

- [ ] **Should export support batch operations?**
  - [ ] Yes, export multiple endpoints sequentially
  - ] Yes, with progress indicator
  - [ ] Yes, with ability to cancel
  - [ ] No, one at a time

- [ ] **What should happen during export?**
  - [ ] Show progress bar/indicator
  - [ ] Show current endpoint being exported
  - [ ] Allow cancellation
  - [ ] Show export log/results
  - [ ] Other: _________________

### 3.3 Export Validation
- [ ] **What validation should be performed?**
  - [ ] Check endpoint collection/objects exist
  - [ ] Check filepath is valid
  - [ ] Check disk space available
  - [ ] Check write permissions
  - [ ] Validate exported USD file
  - [ ] Check material/texture references
  - [ ] Other: _________________

- [ ] **How should validation errors be handled?**
  - [ ] Show error dialog
  - [ ] Show error in UI panel
  - [ ] Log to file
  - [ ] Skip invalid endpoints, continue with others
  - [ ] Stop export on first error
  - [ ] Other: _________________

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

- [ ] **What is the preferred UI layout?**
  - [ ] Single panel with all controls
  - [ ] Tabbed interface (Endpoints, Settings, Export)
  - [ ] Collapsible sections
  - [ ] Other: _________________

### 4.2 Endpoint Management UI
- [ ] **How should endpoints be displayed?**
  - [ ] Simple list with add/remove buttons
  - [ ] List with expandable details
  - [ ] Card/tile view
  - [ ] Tree view (if hierarchical)
  - [ ] Other: _________________

- [ ] **What information should be visible in the list?**
  - [ ] Endpoint name
  - [ ] Collection/object name
  - [ ] Export filepath
  - [ ] Status (enabled/disabled)
  - [ ] Last export time
  - [ ] Export options summary
  - [ ] Other: _________________

- [ ] **How should users edit endpoint properties?**
  - [ ] Inline editing in list
  - [ ] Expandable details panel
  - [ ] Separate dialog window
  - [ ] Properties panel integration
  - [ ] Other: _________________

### 4.3 Export UI
- [ ] **What export controls should be visible?**
  - [ ] Export All button
  - [ ] Export Selected button
  - [ ] Export Active button
  - [ ] Export progress indicator
  - [ ] Export log/results
  - [ ] Export settings/preferences
  - [ ] Other: _________________

---

## 5. Error Handling & Feedback

### 5.1 Error Reporting
- [ ] **How should errors be reported?**
  - [ ] Popup dialog for critical errors
  - [ ] Status message in UI panel
  - [ ] Blender's info area
  - [ ] Log file
  - [ ] Console output
  - [ ] Combination of above: _________________

- [ ] **What level of error detail is needed?**
  - [ ] Simple messages (user-friendly)
  - [ ] Detailed technical messages
  - [ ] Both (simple + detailed toggle)

### 5.2 Success Feedback
- [ ] **How should successful exports be indicated?**
  - [ ] Status message
  - [ ] Notification popup
  - [ ] Visual indicator (checkmark, color change)
  - [ ] Export log with results
  - [ ] Other: _________________

### 5.3 Logging
- [ ] **Should export operations be logged?**
  - [ ] Yes, to Blender's console
  - [ ] Yes, to file
  - [ ] Yes, to both
  - [ ] No logging needed

- [ ] **What should be logged?**
  - [ ] Export start/end times
  - [ ] Endpoints exported
  - [ ] File paths
  - [ ] Errors/warnings
  - [ ] Export options used
  - [ ] Other: _________________

---

## 6. Performance & Scalability

### 6.1 Performance Requirements
- [ ] **What are acceptable export times?**
  - [ ] < 1 second per endpoint
  - [ ] < 5 seconds per endpoint
  - [ ] < 30 seconds per endpoint
  - [ ] No specific requirement

- [ ] **How should the UI behave during export?**
  - [ ] Remain responsive (background export)
  - [ ] Show progress, allow cancellation
  - [ ] Block UI (simpler implementation)
  - [ ] Other: _________________

### 6.2 Large Scene Handling
- [ ] **How should large scenes be handled?**
  - [ ] Optimize visibility operations
  - [ ] Support selective export (skip some endpoints)
  - [ ] Add progress indicators
  - [ ] Allow cancellation
  - [ ] Other: _________________

---

## 7. Integration & Compatibility

### 7.1 Blender Version Support
- [ ] **Which Blender versions should be supported?**
  - [ ] 4.2 LTS only
  - [ ] 4.2+ (including 4.3, 4.4, etc.)
  - [ ] 4.2+ and 5.0+ (with version checks)
  - [ ] Latest stable only

### 7.2 Other Addon Compatibility
- [ ] **Should the addon work alongside:**
  - [ ] Other USD-related addons
  - [ ] Asset management addons
  - [ ] Export workflow addons
  - [ ] Any addon (non-intrusive design)

- [ ] **Are there known conflicts to avoid?**
  - [ ] List: _________________

### 7.3 Pipeline Integration
- [ ] **Should the addon support:**
  - [ ] Command-line/batch export
  - [ ] Python API for scripting
  - [ ] Integration with external tools
  - [ ] Custom property reading/writing
  - [ ] Other: _________________

---

## 8. Advanced Features (Future Considerations)

### 8.1 USD Composition
- [ ] **Should the addon prepare for future USD composition features?**
  - [ ] Yes, design with composition in mind
  - [ ] No, focus on simple export only

- [ ] **If yes, what composition features might be needed?**
  - [ ] Reference management
  - [ ] Sublayer support
  - [ ] Variant sets
  - [ ] Payloads
  - [ ] Other: _________________

### 8.2 Metadata & Customization
- [ ] **Should endpoints support custom metadata?**
  - [ ] Yes, custom properties on endpoints
  - ] Yes, custom USD metadata
  - [ ] No, standard properties only

- [ ] **Should the addon support custom export hooks?**
  - [ ] Yes, via USDHook
  - [ ] Yes, via custom scripts
  - [ ] No, standard export only

### 8.3 Asset Management
- [ ] **Should the addon integrate with asset management?**
  - [ ] Blender's Asset Browser
  - [ ] External asset management systems
  - [ ] Version control integration
  - [ ] No asset management integration

---

## 9. Documentation & Support

### 9.1 Documentation Needs
- [ ] **What documentation is needed?**
  - [ ] User manual/guide
  - [ ] Quick start tutorial
  - [ ] Video tutorials
  - [ ] API documentation (for developers)
  - [ ] Example scenes
  - [ ] Troubleshooting guide
  - [ ] Other: _________________

### 9.2 Help & Support
- [ ] **How should users get help?**
  - [ ] Built-in tooltips
  - [ ] Help button linking to docs
  - [ ] Example scenes with comments
  - [ ] Support forum/community
  - [ ] Other: _________________

---

## 10. Constraints & Limitations

### 10.1 Technical Constraints
- [ ] **Are there any technical constraints?**
  - [ ] Must work on Windows only
  - [ ] Must work on Linux only
  - [ ] Must work on macOS only
  - [ ] Cross-platform required
  - [ ] Python version requirements: ___
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

## 14. Does Something Similar Already Exist?

### 14.1 Existing Solutions Research
- [ ] **Have you searched for existing Blender USD export addons or solutions?**
  - [ ] Yes, I have searched
  - [ ] No, I haven't searched yet
  - [ ] Not sure where to search

- [ ] **If yes, what did you find?** (List any similar addons, tools, or solutions)
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.2 Known Similar Addons/Tools
- [ ] **Are you aware of any existing Blender addons that do something similar?**
  - [ ] Name: _________________ (URL/Link: _________________)
  - [ ] Name: _________________ (URL/Link: _________________)
  - [ ] Name: _________________ (URL/Link: _________________)

- [ ] **If yes, what do they do well?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

- [ ] **If yes, what are their limitations or gaps?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.3 Comparison with Existing Solutions
- [ ] **How would this addon differ from or improve upon existing solutions?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

- [ ] **What unique value does this addon provide?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.4 Open Source / Community Solutions
- [ ] **Are there open-source solutions we could contribute to instead?**
  - [ ] Yes: _________________ (URL: _________________)
  - [ ] No, nothing suitable found
  - [ ] Not sure

- [ ] **Would it be better to extend an existing solution rather than create new?**
  - [ ] Yes, extend: _________________
  - [ ] No, create new solution
  - [ ] Not sure

### 14.5 Commercial Solutions
- [ ] **Are there commercial solutions that address this need?**
  - [ ] Yes: _________________ (URL: _________________)
  - [ ] No commercial solutions found
  - [ ] Not applicable

- [ ] **If yes, what are the limitations (cost, licensing, features)?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.6 Research Sources
- [ ] **Where have you searched?** (Check all that apply)
  - [ ] Blender Add-ons repository
  - [ ] GitHub
  - [ ] Blender Artists forum
  - [ ] Blender Stack Exchange
  - [ ] Other forums/communities: _________________
  - [ ] Google/web search
  - [ ] Other: _________________

### 14.7 Avoiding Duplication
- [ ] **Based on your research, are we duplicating existing work?**
  - [ ] No, nothing similar exists
  - [ ] Yes, but existing solutions have significant gaps
  - [ ] Yes, but we're taking a different approach
  - [ ] Yes, and we should consider contributing to existing solution instead
  - [ ] Not sure, need more research

- [ ] **If duplicating, what is the justification for creating a new solution?**
  - [ ] _________________
  - [ ] _________________
  - [ ] _________________

### 14.8 Collaboration Opportunities
- [ ] **Are there opportunities to collaborate with existing projects?**
  - [ ] Yes: _________________ (Project: _________________)
  - [ ] No
  - [ ] Not sure

- [ ] **Would you be open to contributing to an existing project instead?**
  - [ ] Yes, if it meets our needs
  - [ ] No, we need our own solution
  - [ ] Maybe, depends on the project

---

## Completion Checklist

- [ ] All relevant sections completed (1-14)
- [ ] Priorities assigned to features
- [ ] Use case examples provided
- [ ] Constraints documented
- [ ] Existing solutions researched (Section 14)
- [ ] Duplication analysis completed
- [ ] Ready for requirements analysis

---

## Next Steps

Once this questionnaire is completed:

1. ✅ **Requirements Analysis** → Create detailed requirements list (`02_Detailed_Requirements.md`)
2. ✅ **Module Design** → Define addon modules (`03_Module_Design.md`)
3. ✅ **Implementation Plan** → Create step-by-step implementation plan (`04_Implementation_Plan.md`)

---

**Document Status**: ⏳ Awaiting completion  
**Last Updated**: 25.11.2025

