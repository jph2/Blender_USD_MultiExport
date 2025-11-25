# Blender USD Stable Export

A Blender Python addon that enables users to define specific endpoints (collections or objects) in Blender's scene hierarchy and export them as separate USD files, compensating for Blender's lack of native USD composition arc support.

## 🎯 Overview

**Blender USD Stable Export** is a Blender addon designed to streamline USD export workflows by allowing users to define multiple export endpoints within a single Blender scene. Since Blender doesn't support USD composition arcs natively, this addon provides a workaround by enabling batch export of different scene parts as separate USD files.

### Key Features

- ✅ **Endpoint-Based Export**: Define collections or objects as export endpoints
- ✅ **Batch Export**: Export multiple endpoints in a single operation
- ✅ **Material Preservation**: Automatically preserves materials and textures
- ✅ **Scene State Safety**: Non-destructive export with automatic scene state restoration
- ✅ **User-Friendly UI**: Integrated panel within Blender's interface
- ✅ **Export Validation**: Built-in validation and error reporting

## 📋 Table of Contents

- [Overview](#-overview)
- [Use Cases](#-use-cases)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Status](#-project-status)
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

- **Blender**: 4.2 LTS or later (primary target: 4.2 LTS)
- **Python**: 3.11+ (bundled with Blender)
- **USD Support**: Blender's built-in USD exporter (included with Blender 4.2+)

## 🚀 Installation

### Method 1: Install from ZIP (Recommended)

1. Download the latest release from the [Releases](../../releases) page
2. Open Blender
3. Go to `Edit > Preferences > Add-ons`
4. Click `Install...`
5. Select the downloaded ZIP file
6. Enable the addon by checking the box next to "USD Stable Export"
7. Click `Save Preferences`

### Method 2: Install from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Blender_USD_StableExport.git
   ```

2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...`
4. Navigate to the cloned repository and select the `addon` folder
5. Enable the addon

## 📖 Usage

### Basic Workflow

1. **Open Your Scene**: Load your Blender scene with organized collections
2. **Access the Addon**: Open the USD Stable Export panel (typically in Scene Properties or N-Panel)
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

### Export Options

Each endpoint can be configured with:
- Export filepath
- Root prim path
- Material and texture export settings
- Animation export settings
- Custom export options

## 📊 Project Status

**Current Status**: 🚧 In Development

This project is currently in the planning and requirements gathering phase. See the [Implementation Process](README_Implementation.md) for details.

### Development Phases

- [x] **Research & Discovery** - Complete
- [x] **Deigning Requirements Questionnaire** - Complete
- [ ] **Requirements Questionnaire (to be filled out)** - In Progress
- [ ] **Detailed Requirements** - In Progress
- [ ] **Module Design** - Pending
- [ ] **Implementation** - Pending
- [ ] **Testing & Documentation** - Pending

## 📚 Documentation

### Project Documentation

- **[Research Document](Blender_USD_StableExport_RESEARCH.md)**: Comprehensive research and analysis
- **[Discovery Document](Blender_USD_StableExport_DISCOVERY.md)**: Initial discovery and planning
- **[Implementation Process](README_Implementation.md)**: Step-by-step implementation workflow
- **[Requirements Questionnaire](01_Requirements_Questionnaire.md)**: Requirements gathering questionnaire

### External Resources

- [Blender Python API Documentation](https://docs.blender.org/api/current/)
- [Blender USD Export Documentation](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)
- [Blender Addon Development Guide](https://developer.blender.org/docs/handbook/extensions/addon_dev_setup/)

### Important Notes

- **[Naming Conventions](NAMING_CONVENTIONS.md)**: Avoid using "Environment" as a collection name - it conflicts with Omniverse's `/World/environment` lighting setup. Use "Props", "Set", or other descriptive names instead.

## 🛠️ Development

### Project Structure

```
Blender_USD_StableExport/
├── addon/                          # Addon source code (to be created)
│   └── blender_usd_stableexport/
│       ├── __init__.py
│       ├── ops_export.py
│       ├── props.py
│       └── ui.py
├── docs/                           # Documentation
│   └── Blender_USD_StableExport_RESEARCH.md
├── tests/                          # Test scripts (to be created)
├── 01_Requirements_Questionnaire.md
├── 02_Detailed_Requirements.md
├── 03_Module_Design.md
├── 04_Implementation_Plan.md
├── README.md                       # This file
└── README_Implementation.md
```

### Development Setup

1. **Prerequisites**:
   - Blender 4.2 LTS installed
   - Python 3.11+ (for external IDE development)
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

### Blender 5.0 Compatibility

This addon is initially developed for Blender 4.2 LTS. A comprehensive compatibility review for Blender 5.0 is planned once official API documentation is available. See the [Research Document](Blender_USD_StableExport_RESEARCH.md#blender-50-readiness-and-compatibility-planning) for details.

## 🤝 Contributing

Contributions are welcome! However, please note that this project is currently in early development. 

### How to Contribute

1. **Review Documentation**: Read the [Research Document](Blender_USD_StableExport_RESEARCH.md) and [Implementation Process](README_Implementation.md)
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
- **Blender Version**: Currently targets Blender 4.2 LTS. Blender 5.0 compatibility will be reviewed once official documentation is available.
- **Scene Modification**: The addon temporarily modifies scene visibility during export but always restores the original state.

## 📝 License

[License to be determined]

## 🙏 Acknowledgments

- Blender Foundation for the excellent Python API
- NVIDIA for USD/Omniverse ecosystem
- OpenUSD community for documentation and resources

## 📧 Contact & Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and community support
- **Documentation**: See the [Documentation](#-documentation) section above

---

**Note**: This project is in active development. Features and APIs may change. Check the [Project Status](#-project-status) section for current development phase.

**Last Updated**: November 25, 2025

