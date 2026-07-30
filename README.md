# Batch Mesh Simplification for Blender v1.0
This is an automated pipeline add-on designed for batch mesh simplification and LOD (Level of Detail) creation in Blender. Based on Blender's native Decimate modifier, it allows you to batch simplify original models to multiple levels, export them to a specific directory, 
and automatically apply standardized naming conventions for game engines.

## How to install & use
1. Download the .zip file from the releases page.
2. In Blender, navigate to ***Edit > Preferences > Add-ons > Install...*** and select the .zip file.
3. After installation, press **N** in the 3D viewport to open the sidebar and locate the **BMS** panel.

## Core functions
### Export settings
You can select the export directory and customize the file naming convention. The default file name pattern is {obj}_LOD{n}, where {obj} is the name of the selected object(s) and {n} is the level index of the LOD.

### LOD settings
The LOD settings provide three representations for your target simplification: **Triangle Count**, **Percentage**, and **Ratio**. You can create each level manually or use the Quick Add feature to generate multiple levels in a single command.
The default Quick Add command is 10k, 5k, 2k, 1k, which creates 4 levels of simplification containing 10,000, 5,000, 2,000, and 1,000 triangles, respectively. Quick Add automatically identifies the representation method based on your input format:
- **xxx%**: percentage
- **0.0-1.0**: ratio
- **any integer number**: triangle count
- xxx**k** / xxx**m**: thousand / million representation

## Use case and limitations
This add-on is **best for**:
- Static props
- Background environment assets
- Models with low topological precision requirements (such as rocks or ruins)
- Rapid prototyping

It is **not recommended** for rigged characters with complex skinning animations or "Hero Assets" requiring precise hard-surface normals. Because the tool relies on Blender's native Decimate function, it may compromise specific topology that requires manual retopology.

## Future development
This Add-on is still in active development. I plan to add more features in the future, such as supporting alternative simplification modifiers beyond Decimate. I welcome anyone who wants to contribute to this small project!
