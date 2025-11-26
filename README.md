# Blender USD Multi Export

A Blender Python addon that enables users to define specific endpoints (collections or objects) in Blender's scene hierarchy and export them as separate USD files, compensating for Blender's lack of native USD composition arc support.

> **📝 Note on Project Name**: This project was previously named "Blender USD Stable Export". The name was changed to "Multi Export" to better reflect its core functionality: **multi-endpoint batch export capabilities**. The previous name "Stable" referred to reliable endpoint management and consistent export workflows, but it led to confusion as it could imply that Blender's built-in USD export is unstable (which is not the case - Blender's native USD export is stable and well-maintained). This addon enhances workflow by adding endpoint-based batch export functionality on top of Blender's solid foundation.
>
> **🔗 Repository Note**: This GitHub repository was renamed from `Blender_USD_StableExport` to `Blender_USD_MultiExport`. Old links still work thanks to GitHub's automatic redirects, but if you're cloning the repository, use the new name: `git clone https://github.com/jph2/Blender_USD_MultiExport.git`

## 📊 Project Status

**Current Status**: 🚧 **In Development** - Planning & Requirements Phase

> **⚠️ Important**: This project is currently in the **planning and requirements gathering phase**. The addon is **not yet available** for installation or use. See development phases below for current progress.

### Development Phases

- [x] **Research & Discovery** - Complete
- [x] **Designing Requirements Questionnaire** - Complete
- [ ] **Requirements Questionnaire (to be filled out)** - In Progress
- [ ] **Detailed Requirements** - In Progress
- [ ] **Module Design** - In Progress
- [ ] **Implementation** - Pending
- [ ] **Testing & Documentation** - Pending

See the [Implementation Process](README_Implementation.md) for details.

---

## 🎯 Overview

**Blender USD Multi Export** is a Blender addon designed to streamline USD export workflows by allowing users to define multiple export endpoints within a single Blender scene. Since Blender doesn't support USD composition arcs natively, this addon provides a workaround by enabling batch export of different scene parts as separate USD files.

### Planned Key Features

- ✅ **Endpoint-Based Export**: Define collections or objects as export endpoints
- ✅ **Batch Export**: Export multiple endpoints in a single operation
- ✅ **Material Preservation**: Automatically preserves materials and textures
- ✅ **Scene State Safety**: Non-destructive export with automatic scene state restoration
- ✅ **User-Friendly UI**: Integrated panel within Blender's interface
- ✅ **Export Validation**: Built-in validation and error reporting
- ✅ **Bug Report Button**: Direct bug reporting from within Blender UI

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

> **⚠️ Note**: The addon is not yet available for installation. This section describes the planned installation process for future releases.

### Method 1: Install from ZIP (Planned)

1. Download the latest release from the [Releases](../../releases) page (when available)
2. Open Blender
3. Go to `Edit > Preferences > Add-ons`
4. Click `Install...`
5. Select the downloaded ZIP file
6. Enable the addon by checking the box next to "USD Multi Export"
7. Click `Save Preferences`

> **✅ Cross-Platform Compatibility**: The same ZIP file works on **Windows, macOS, and Linux**. Blender addons are Python-based and platform-independent. No separate builds needed for different operating systems.

### Method 2: Install from Source (Planned)

1. Clone this repository:
   ```bash
   git clone https://github.com/jph2/Blender_USD_MultiExport.git
   ```

2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...`
4. Navigate to the cloned repository and select the `addon` folder
5. Enable the addon

## 📖 Usage

> **⚠️ Note**: The addon is not yet available. This section describes the planned usage workflow.

### Planned Basic Workflow

1. **Open Your Scene**: Load your Blender scene with organized collections
2. **Access the Addon**: Open the USD Multi Export panel (typically in Scene Properties or N-Panel)
3. **Define Endpoints**: 
   - Click "Add Endpoint"
   - Select a collection or objects
   - Set the export filepath
   - Configure export options
4. **Export**: Click "Export All Endpoints" or export individual endpoints

### Defining Endpoints

An **endpoint** is a collection or set of objects that you want to export as a single USD file. For example:
- A "Characters" collection → exports to `characters.usd`
- A "Props" collection → exports to `props.usd`
- A "Vehicles" collection → exports to `vehicles.usd`
- Selected objects → exports to `selected_objects.usd`

> **⚠️ Naming Note**: Avoid using "Environment" as a collection name. In Omniverse, `/World` (default prim) and `/environment` are siblings at root level. `/environment` is reserved for lighting and is NOT imported when referencing (only content under `/World` is imported). Using "Environment" creates conflicts. Use descriptive names like "Props", "Set", "Location", or "SceneElements" instead. See [Naming Conventions](NAMING_CONVENTIONS.md) for details.

### Planned Export Options

Each endpoint can be configured with:
- Export filepath
- Root prim path
- Material and texture export settings
- Animation export settings
- Custom export options

## 📚 Documentation

### Project Documentation

- **[Research Document](Blender_USD_MultiExport_RESEARCH.md)**: Comprehensive research and analysis
- **[Discovery Document](Blender_USD_MultiExport_DISCOVERY.md)**: Initial discovery and planning
- **[Apple USD Perspective](APPLE_USD_PERSPECTIVE.md)**: Apple's USD workflows and requirements
- **[Implementation Process](README_Implementation.md)**: Step-by-step implementation workflow
- **[Requirements Questionnaire](01_Requirements_Questionnaire.md)**: Requirements gathering questionnaire
- **[Detailed Requirements](02_Detailed_Requirements.md)**: Confirmed requirements and specifications
- **[Module Design](03_Module_Design.md)**: Architecture and module structure
- **[Implementation Plan](04_Implementation_Plan.md)**: Step-by-step implementation guide

## 🍎 Apple USD Perspective

Apple is a founding member of the Alliance for OpenUSD (AOUSD) and plays a key role in USD standardization. This addon supports Apple workflows including:

- **AR/VR Content Creation**: Export assets for RealityKit and ARKit
- **Apple Platform Pipelines**: Integration with Apple's content creation ecosystem
- **Cross-Platform Workflows**: USD as interchange format for multi-platform content

See **[APPLE_USD_PERSPECTIVE.md](APPLE_USD_PERSPECTIVE.md)** for detailed information about Apple's USD usage, requirements, and how this addon aligns with Apple workflows.

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
├── addon/                          # Addon source code (to be created)
│   └── blender_usd_multiexport/
│       ├── __init__.py
│       ├── ops_export.py
│       ├── props.py
│       └── ui.py
├── docs/                           # Documentation
│   └── Blender_USD_MultiExport_RESEARCH.md
├── tests/                          # Test scripts (to be created)
├── 01_Requirements_Questionnaire.md
├── 02_Detailed_Requirements.md
├── 03_Module_Design.md
├── 04_Implementation_Plan.md
├── APPLE_USD_PERSPECTIVE.md        # Apple USD workflows
├── README.md                       # This file
└── README_Implementation.md
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

### Blender Version Support

This addon is developed for **Blender 5.0** (officially released November 18, 2025). Blender 4.x versions are not supported. See the [Research Document](Blender_USD_MultiExport_RESEARCH.md#blender-50-readiness-and-compatibility-planning) for API compatibility details.

## 🤝 Contributing

Contributions are welcome! However, please note that this project is currently in early development. 

### How to Contribute

1. **Review Documentation**: Read the [Research Document](Blender_USD_MultiExport_RESEARCH.md) and [Implementation Process](README_Implementation.md)
2. **Complete Questionnaire**: If you have use cases or requirements, complete the [Requirements Questionnaire](01_Requirements_Questionnaire.md)
3. **Follow Development**: Check the implementation plan as it's developed
4. **Stay Tuned**: Once implementation begins, contributions will be welcome!

### Contribution Guidelines

- Follow Blender's addon development best practices
- Maintain code quality and documentation
- Test thoroughly with various scene configurations
- Provide clear commit messages

## 🐛 Known Limitations

- **USD Composition**: Blender doesn't support USD composition arcs natively. This addon exports separate files that must be composed manually in the target application (e.g., Omniverse).
- **Blender Version**: Targets Blender 5.0+ only. Blender 4.x versions are not supported.
- **Scene Modification**: The addon temporarily modifies scene visibility during export but always restores the original state.

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

**Note on Project Name**: This project was renamed from "Blender USD Stable Export" to "Blender USD Multi Export" to better reflect its core functionality: multi-endpoint batch export capabilities. The previous name "Stable" referred to reliable endpoint management and consistent export workflows, but it led to confusion as it could imply that Blender's built-in USD export is unstable (which is not the case). See `NAMING_AND_APPLE_FEEDBACK.md` for the full naming discussion.

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

**Last Updated**: November 25, 2025

