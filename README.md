---
arys_schema_version: '1.2'
id: 32503e19-abb5-4130-affd-9322f7ccc476
title: Blender USD Multi Export
type: TECHNICAL
status: active
trust_level: 2
visibility: internal
created: '2026-02-17T09:42:16Z'
last_modified: '2026-06-09T12:00:00Z'
---

**Version**: 1.0.1 | **Date**: 09.06.2026 | **Time**: 12:00 | **GlobalID**: 20260216_1200_Blender_USD_MultiExport_batch

**Tag block:**
#blender #framework_integration #export #conversion #joints #collections #openusd #usd_core #references #analysis #workflow_automation #validation #quality_assurance #case_study #workflow_optimization #deterministic_workflows #best_practices

# Blender USD Multi Export

> ⚠️ **WORKFLOW-MIGRATION AUSSTEHEND — vor weiterer Arbeit angleichen.**
> Die Doc-Struktur dieses Repos (`04*_Implementation_Plan*`, `09_Roadmap`, nummerierte Docs) stammt aus dem alten Workflow und entspricht **nicht** dem neu definierten Studio-Kanon: **Roadmap = Execution-Wrapper/Owner**, der Implementation Plan ist deren Execution-Section, **Specs bleiben separat & klein**, klare Trennung SPEC/IMP/VAL. Bevor hier substanziell weitergearbeitet wird, muss das Repo darauf gerade gezogen werden (Renumbering/Merge der `04`-Serie unter die Roadmap).
> Sonderfall hier: verirrte `22_IMPLEMENTATION_PLAN_CLEAN_Phase_14D.md` (+ `23_QUICK_REFERENCE_Phase_14D.md`) in die Roadmap/`04`-Serie einordnen.
> Kanon: `Studio_Framework/020_Standards_Definitions_Rules/040_Quality_enforcement/STANDARD_SPEC_IMPLEMENTATION_VALIDATION_SEPARATION.md` + `.../030_Process/Artifact_Lifecycle_Pipeline.md`. (Notiz: 09.06.2026)

[![License: To Be Determined](https://img.shields.io/badge/License-TBD-lightgrey.svg)](LICENSE)
[![Blender: 5.0+](https://img.shields.io/badge/Blender-5.0+-orange.svg)](https://www.blender.org/)
[![Version: 0.1.3](https://img.shields.io/badge/Version-0.1.3-blue.svg)](HANDOFF.md)
[![Status: MVP Complete](https://img.shields.io/badge/Status-MVP%20Complete-green.svg)](HANDOFF.md)

**Last Updated**: 03.02.2026 23:27

**Release Workflow (Mandatory)**: For every version update, we **version → commit → push**. No version change is considered complete until the commit is pushed.

A Blender Python addon that enables users to define **start points** (collections or objects) in Blender's scene hierarchy and export them as separate USD files. Start points are the stable DCC origins for the downstream USD pipeline and composition arcs; exported USD files are the **beginning** of further pipelining, not the terminus.

> **📝 Note on Project Name**: This project was previously named "Blender USD Stable Export". The name was changed to "Multi Export" to better reflect its core functionality: **multi–start point batch export capabilities**. Start points are the pipeline origins in the DCC; the previous "endpoint" framing referred to the DCC perspective. The addon now consistently uses "start point" to reflect that exported USD is the start of downstream pipeline and composition arcs.
>
> **🔗 Repository Note**: This GitHub repository was renamed from `Blender_USD_StableExport` to `Blender_USD_MultiExport`. Old links still work thanks to GitHub's automatic redirects, but if you're cloning the repository, use the new name: `git clone https://github.com/jph2/Blender_USD_MultiExport.git`

## 📊 Project Status

**Current Status**: ✅ **MVP Released** - v0.1.3 Available for Testing

> **🎉 MVP Available**: **Blender USD Multi Export v0.1.3** is now available! This functional MVP provides core endpoint-based USD export workflow. See installation instructions below for testing.

### Development Phases

- [x] **Research & Discovery** - Complete
- [x] **Designing Requirements Questionnaire** - Complete
- [ ] **Requirements Questionnaire** - Ongoing (confirmed requirements)
- [ ] **Detailed Requirements** - Ongoing
- [ ] **Module Design** - Ongoing
- [x] **MVP Implementation (v0.1.3)** - ✅ Complete & Released
- [ ] **Advanced Features (v0.2.0+)** - Post-MVP
- [ ] **Full Testing & ASWF Compliance** - In Progress

See the [Implementation Process](docs/archive/README_Implementation.md) for details (Archived - historical reference).

---

## 🎯 Overview

**Blender USD Multi Export v0.1.3** is a functional MVP that provides core endpoint-based USD export workflow. Define export endpoints (collections or objects) and export multiple USD files in batch operations, with automatic scene state restoration and comprehensive error handling.

### MVP v0.1.3 Key Features

- ✅ **Start point-Based Export**: Define collections or objects as export endpoints
- ✅ **Batch Export**: Export multiple endpoints in a single operation
- ✅ **Scene State Safety**: Non-destructive export with automatic state restoration
- ✅ **Cross-Platform Paths**: Relative path storage with absolute resolution
- ✅ **Comprehensive Logging**: Verbose mode and automated bug reports
- ✅ **User-Friendly UI**: Integrated panel within Blender's interface
- ✅ **Error Handling**: Detailed validation and actionable error messages

## 📋 Table of Contents

- [Project Status](#-project-status)
- [Overview](#-overview)
- [Use Cases](#-use-cases)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Documentation](#-documentation)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🎬 Use Cases

This addon is particularly useful for:

- **Omniverse Workflows**: Exporting Blender assets for use in NVIDIA Omniverse
- **Asset Libraries**: Creating organized USD asset libraries from Blender scenes
- **Pipeline Integration**: Integrating Blender into USD-based production pipelines
- **Multi-File Exports**: Exporting different parts of a scene as separate USD files

## 📦 Requirements

- **Blender**: 5.0 or later (primary target: Blender 5.0, released November 18, 2025)
- **Python**: 3.11+ (bundled with Blender 5.0)
- **USD Support**: Blender's built-in USD exporter (included with Blender 5.0+)
- **Platform**: Windows, macOS, and Linux (same ZIP file works on all platforms)

## 🚀 Installation

> **🎉 MVP Available**: Blender USD Multi Export v0.1.3 is now available for testing!

### Method 1: Install from ZIP (Recommended for Distribution)

**Build the ZIP file** (if you have the repository locally):

See [`11_BUILD_INSTRUCTIONS.md`](11_BUILD_INSTRUCTIONS.md) for detailed build instructions.

**Quick build**:
```bash
cd Blender_USD_MultiExport
python scripts/build_extension.py
```
This creates `dist/blender_usd_multiexport.zip` ready for installation.

2. **Install in Blender 5.0+**:
   - Open Blender 5.0+
   - Go to **Edit → Preferences → Extensions**
   - Click the **dropdown menu** (top right) → **Install from Disk**
   - Select `dist/blender_usd_multiexport.zip`
   - The extension will be installed and available

3. **Enable the extension**:
   - Search for "USD Multi Export" in the Extensions panel
   - Click the checkbox to enable it
   - The extension is now active

**Verify Installation**:
   - Look for "USD Multi Export" panel in the Scene Properties tab
   - The panel should show endpoint management controls

> **💡 Why Scene Properties?** This addon uses Scene Properties because USD export operations affect entire scenes, following Blender's conventions (the built-in USD exporter also uses Scene Properties). This placement provides persistent, non-intrusive access to export controls while you work. See [Best Practices](../../OV_Dev/OV_USD_Scripts/best_practise_Blender%20Extensions_addons/building_for_Blender.md#uiux-placement-best-practices) for more details.

> **✅ Cross-Platform Compatibility**: The same ZIP file works on **Windows, macOS, and Linux**. Blender extensions are Python-based and platform-independent. No separate builds needed for different operating systems.

#### Updating the Extension (Uninstall & Reinstall)

When updating to a new version:

1. **Uninstall the old version**:
   - Go to **Edit → Preferences → Extensions**
   - Find "USD Multi Export" in the list
   - Click **"Uninstall"** button
2. **Restart Blender** (important - ensures old code is cleared)
3. **Install the new ZIP file**:
   - Go to **Edit → Preferences → Extensions**
   - Click dropdown (top right) → **Install from Disk**
   - Select the new zip file
4. **Restart Blender again** (to load the new version)

> **Important**: Restarting Blender after uninstalling and reinstalling is required to ensure the old code is fully cleared and the new version loads correctly. If you experience issues after updating, restart Blender.

### Method 2: Install from Local Repository (Development/Testing)

For development or testing, you can install directly from the repository:

1. **Open Blender 5.0+**
2. **Go to `Edit > Preferences > Extensions`**
3. **Click the dropdown menu** (top right) → **Install from Disk**
4. **Navigate to your local repository** (`Blender_USD_MultiExport`) and select the `addon` folder
5. **Enable the extension** by checking the box next to "USD Multi Export"

**Note**: This method is for development/testing. For distribution, use Method 1 (ZIP installation).

### Method 3: Install from GitHub Release (Future)

1. Download the latest release ZIP from the [Releases](https://github.com/jph2/Blender_USD_MultiExport/releases) page
2. Follow **Method 1, steps 2-3** above to install in Blender

## 📖 Usage

> **🎯 MVP Features**: v0.1.3 provides core functionality for testing. Advanced features will be added in future versions.
>
> **📚 For detailed usage instructions**, see the **[User Guide](06_USER_GUIDE.md)** with step-by-step workflows, troubleshooting, and best practices.

### Basic Workflow

1. **Open Your Scene**: Load your Blender scene with organized collections
2. **Access the Addon**: Go to Scene Properties tab → "USD Multi Export" panel
3. **Define Start points**:
   - Click "Add" to create a new endpoint
   - Set endpoint name (used for root prim path)
   - Enter collection name (must match existing collection exactly)
   - Set filepath (use `//export/filename.usd` for relative paths)
   - Enable/disable endpoints as needed
4. **Export**: Click "Export Start points" to batch export all enabled endpoints

### Defining Start points

An **endpoint** is a collection or set of objects that you want to export as a single USD file. For example:
- A "Characters" collection → exports to `//export/characters.usd`
- A "Props" collection → exports to `//export/props.usd`
- A "Vehicles" collection → exports to `//export/vehicles.usd`

> **⚠️ Naming Note**: Avoid using "Environment" as a collection name. In Omniverse, `/World` (default prim) and `/environment` are siblings at root level. `/environment` is reserved for lighting and is NOT imported when referencing (only content under `/World` is imported). Using "Environment" creates conflicts. Use descriptive names like "Props", "Set", "Location", or "SceneElements" instead. See [Naming Conventions](NAMING_CONVENTIONS.md) for details (Active reference).

### MVP v0.1.3 Export Options

Each endpoint exports with these settings:
- **Materials**: ✅ Enabled (USD Preview Surface)
- **UV Maps**: ✅ Enabled
- **Normals**: ✅ Enabled
- **Animation**: ❌ Disabled (static exports only)
- **Root Prim Path**: Uses endpoint name (e.g., `/Characters`)
- **File Format**: `.usd` (ASCII/binary switching supported)

### Verbose Logging

Enable "Verbose Logging" in the panel for detailed console output during development and testing.

## 📚 Documentation

### Project Documentation

- **[Research Document](docs/archive/Blender_USD_StableExport_RESEARCH.md)**: Comprehensive research and analysis (Archived - historical reference)
- **[Discovery Document](docs/archive/Blender_USD_StableExport_DISCOVERY.md)**: Initial discovery and planning (Archived - historical reference)
- **[Apple USD Perspective](docs/archive/APPLE_USD_PERSPECTIVE.md)**: Apple's USD workflows and requirements (Archived - historical reference)
- **[Implementation Process](docs/archive/README_Implementation.md)**: Step-by-step implementation workflow (Archived - historical reference)
- **[Requirements Questionnaire](01_Requirements_Questionnaire.md)**: Requirements gathering questionnaire (Active reference)
- **[Detailed Requirements](02_Detailed_Requirements.md)**: Confirmed requirements and specifications (Active reference)
- **[Module Design](03_Module_Design.md)**: Architecture and module structure (Active reference)
- **[Implementation Plan](04_Implementation_Plan.md)**: Step-by-step implementation guide
- **[Testing Plan](05_Testing_Plan.md)**: Comprehensive testing procedures and bug reporting guidelines
- **[User Guide](06_USER_GUIDE.md)**: Complete user guide with workflows, troubleshooting, and best practices
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Platform-specific troubleshooting, debugging procedures, and common issues
- **[Complete Implementation Plan](04_Implementation_Plan.md)**: Complete development history, implementation details, and roadmap

## 🍎 Apple USD Perspective

Apple is a founding member of the Alliance for OpenUSD (AOUSD) and plays a key role in USD standardization. This addon supports Apple workflows including:

- **AR/VR Content Creation**: Export assets for RealityKit and ARKit
- **Apple Platform Pipelines**: Integration with Apple's content creation ecosystem
- **Cross-Platform Workflows**: USD as interchange format for multi-platform content

See **[docs/archive/APPLE_USD_PERSPECTIVE.md](docs/archive/APPLE_USD_PERSPECTIVE.md)** for detailed information about Apple's USD usage, requirements, and how this addon aligns with Apple workflows (Archived - historical reference).

### External Resources

- [Blender Python API Documentation](https://docs.blender.org/api/current/)
- [Blender USD Export Documentation](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)
- [Blender Addon Development Guide](https://developer.blender.org/docs/handbook/extensions/addon_dev_setup/)

### Important Notes

- **[Naming Conventions](NAMING_CONVENTIONS.md)**: Avoid using "Environment" as a collection name - it conflicts with Omniverse's `/World/environment` lighting setup. Use "Props", "Set", or other descriptive names instead.

## 🛠️ Development

### Project Structure

```
Blender_USD_MultiExport/
├── addon/                          # Addon source code
│   └── blender_usd_multiexport/
│       ├── __init__.py             # Addon registration
│       ├── props.py                # Data model & properties
│       ├── ui.py                   # User interface panels
│       ├── ops_export.py           # Export operations
│       ├── state_manager.py        # Scene state management
│       ├── path_resolver.py        # Cross-platform paths
│       └── logging_utils.py        # Logging & bug reports
├── dist/                           # Build output directory (generated)
│   └── blender_usd_multiexport.zip # Distribution ZIP file
├── scripts/
│   └── build_extension.py          # Build script for creating ZIP (see 11_BUILD_INSTRUCTIONS.md)
├── README.md                       # This file
└── [other project files...]
```

### Development Setup

1. **Prerequisites**:
   - Blender 5.0+ installed (released November 18, 2025)
   - Python 3.11+ (bundled with Blender 5.0, or for external IDE development)
   - Git

2. **IDE Setup** (Optional):
   ```bash
   pip install fake-bpy-module
   ```
   This provides code completion for Blender's Python API in external IDEs.

3. **Development Workflow**:
   - Make changes to addon code
   - Test in Blender (use "Reload Scripts" for quick iteration)
   - Follow the implementation plan phases

### Building the Extension

See [`11_BUILD_INSTRUCTIONS.md`](11_BUILD_INSTRUCTIONS.md) for detailed build instructions.

**Quick build**:
```bash
python scripts/build_extension.py
```

This will:
- Create `dist/blender_usd_multiexport.zip`
- Exclude development files (`__pycache__`, `.git`, `*.md`, etc.)
- Preserve correct directory structure for Blender 5.0+ Extensions system
- Provide build summary with file count and size

**Build Output**:
- ZIP file: `dist/blender_usd_multiexport.zip`
- Ready for installation via `Edit → Preferences → Extensions → Install from Disk`

**Note**: Rebuild the ZIP after code changes or version updates before testing installation.

### Version Update Workflow

When releasing a new version, follow this checklist:

1. **Update version in code**:
   - Update `addon/blender_usd_multiexport/__init__.py` → `bl_info["version"]`
   - Use semantic versioning: `(MAJOR, MINOR, PATCH)`

2. **Update documentation**:
   - Update `README.md` → Version references and changelog
   - Update `PROJECT_PROGRESS_LOG.md` → Version and date
   - Update any implementation plan documents with version references

3. **Rebuild ZIP file**:
   ```bash
   python scripts/build_extension.py
   ```
   Or see [`11_BUILD_INSTRUCTIONS.md`](11_BUILD_INSTRUCTIONS.md) for detailed instructions.

4. **Test installation**:
   - Uninstall old version in Blender
   - Restart Blender
   - Install new ZIP file
   - Restart Blender again
   - Verify functionality and version display

5. **Verify consistency**:
   - Check version appears correctly in Extensions list
   - Verify all documentation references match
   - Confirm no version mismatches

### Blender Version Support

This addon is developed for **Blender 5.0** (officially released November 18, 2025). Blender 4.x versions are not supported. See the [Research Document](docs/archive/Blender_USD_StableExport_RESEARCH.md#blender-50-readiness-and-compatibility-planning) for API compatibility details (Archived - historical reference).

## 🤝 Contributing

Contributions are welcome! However, please note that this project is currently in early development. 

### How to Contribute

1. **Review Documentation**: Read the [Research Document](docs/archive/Blender_USD_StableExport_RESEARCH.md) and [Implementation Process](docs/archive/README_Implementation.md) (Archived - historical references)
2. **Complete Questionnaire**: If you have use cases or requirements, complete the [Requirements Questionnaire](01_Requirements_Questionnaire.md) (Active reference)
3. **Follow Development**: Check the implementation plan as it's developed
4. **Stay Tuned**: Once implementation begins, contributions will be welcome!

### Contribution Guidelines

- Follow Blender's addon development best practices
- Maintain code quality and documentation
- Test thoroughly with various scene configurations
- Provide clear commit messages

## 🐛 Known Limitations (Version 0.1.3)

### Current MVP Limitations

- **USD Composition**: Blender doesn't support USD composition arcs natively. This addon exports separate files that must be composed manually in the target application (e.g., Omniverse).
- **Blender Version**: Targets Blender 5.0+ only. Blender 4.x versions are not supported.
- **Scene Modification**: The addon temporarily modifies scene visibility during export but always restores the original state.
- **Animation Export**: Static exports only. Animation export is not yet implemented (planned for v0.2.0).
- **Export Options**: Limited export options per endpoint. Uses default settings for all exports (materials enabled, relative paths disabled).
- **Pre-Flight Validation**: Basic validation only. No comprehensive pre-export checks or warnings (planned for v0.2.0+).

### Future Enhancements (Post-MVP)

**Planned for v0.2.0**:
- Per-endpoint export settings (materials, UVs, normals, animation)
- Pre-flight validation and warnings
- Export presets
- Advanced UI features (progress indicators, batch operations)

**Planned for v0.3.0+**:
- ASWF-compliant USD structure and metadata
- Root prim path generation
- Standards compliance verification

See [HANDOFF.md](HANDOFF.md) for detailed technical limitations and future roadmap.

## 📝 License

[License to be determined]

## 🙏 Acknowledgments

- **Pixar Animation Studios** for creating and open-sourcing Universal Scene Description (USD)
- **Blender Foundation** for the excellent Python API and open-source 3D creation suite
- **NVIDIA** for USD/Omniverse ecosystem and advancing USD adoption
- **Apple** as a founding member of the Alliance for OpenUSD (AOUSD) and for USD leadership in AR/VR workflows and Apple platform integration
- **Alliance for OpenUSD (AOUSD)** for fostering USD standardization and industry collaboration
- **Academy Software Foundation (ASWF)** for fostering open source software in the motion picture and media industries
- **OpenUSD community** for documentation, resources, and ongoing development

**Note on Project Name**: This project was renamed from "Blender USD Stable Export" to "Blender USD Multi Export" to better reflect its core functionality: multi-endpoint batch export capabilities. The previous name "Stable" referred to reliable endpoint management and consistent export workflows, but it led to confusion as it could imply that Blender's built-in USD export is unstable (which is not the case). See `docs/archive/NAMING_AND_APPLE_FEEDBACK.md` for the full naming discussion (Archived - naming resolved).

## 🐛 Bug Reports & Feature Requests

We use **GitHub Issues** for bug tracking and feature requests. The repository includes automated issue templates to help you provide all necessary information.

### Reporting Bugs

1. Go to [Issues](https://github.com/jph2/Blender_USD_MultiExport/issues)
2. Click **"New Issue"**
3. Select **"🐛 Bug Report"** template
4. Fill out the form with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Blender version and OS
   - Screenshots or error logs

### Requesting Features

1. Go to [Issues](https://github.com/jph2/Blender_USD_MultiExport/issues)
2. Click **"New Issue"**
3. Select **"💡 Feature Request"** template
4. Describe the feature, use case, and priority

### Asking Questions

For questions, use the **"❓ Question"** template or [GitHub Discussions](https://github.com/jph2/Blender_USD_MultiExport/discussions).

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📧 Contact & Support

- **🐛 Bug Reports**: [Create a Bug Report](https://github.com/jph2/Blender_USD_MultiExport/issues/new?template=bug_report.yml)
- **💡 Feature Requests**: [Request a Feature](https://github.com/jph2/Blender_USD_MultiExport/issues/new?template=feature_request.yml)
- **❓ Questions**: [Ask a Question](https://github.com/jph2/Blender_USD_MultiExport/issues/new?template=question.yml) or [GitHub Discussions](https://github.com/jph2/Blender_USD_MultiExport/discussions)
- **📚 Documentation**: See the [Documentation](#-documentation) section above
- **🤝 Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Note**: This project is in active development. Features and APIs may change. See the [Project Status](#-project-status) section at the top for current development phase.

**Last Updated**: December 26, 2025

