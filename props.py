import bpy

from bpy.types import PropertyGroup

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty,
)


# ----------------------------------------
# Single LOD settings
# ----------------------------------------

class BMSLevel(PropertyGroup):

    mode: EnumProperty(
        name="Mode",
        items=[
            ("TRIS", "Target Tris", "Target triangle count"),
            ("PERCENT", "Percent", "Percentage of original mesh"),
            ("RATIO", "Ratio", "Direct decimate ratio"),
        ],
        default="TRIS"
    )

    target_tris: IntProperty(
        name="Triangles",
        default=10000,
        min=1
    )

    target_percent: FloatProperty(
        name="Percent",
        default=50.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE'
    )

    target_ratio: FloatProperty(
        name="Ratio",
        default=0.5,
        min=0.0,
        max=1.0
    )

    def get_ratio(self, base_tris: int):
        if base_tris <= 0:
            return 1.0

        if self.mode == "TRIS":
            return max(0.0, min(1.0, self.target_tris / float(base_tris)))

        elif self.mode == "PERCENT":
            return self.target_percent / 100.0

        else:
            return self.target_ratio


# ----------------------------------------
# Addon settings
# ----------------------------------------

class BMSProperties(PropertyGroup):

    export_dir: StringProperty(
        name="Export Folder",
        subtype='DIR_PATH'
    )

    filename_pattern: StringProperty(
        name="Filename",
        default="{obj}_LOD{n}"
    )

    use_selected: BoolProperty(
        name="Selected Only",
        default=True
    )

    use_collection: BoolProperty(
        name="Use Collection",
        default=False
    )

    collection: PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    )

    levels: CollectionProperty(
        type=BMSLevel
    )

    level_index: IntProperty(
        default=0
    )

    quick_add_text: StringProperty(
        name="Quick Add",
        default="10k,5k,2k,1k"
    )


# ----------------------------------------
# Register & Unregister
# ----------------------------------------

classes = (
    BMSLevel,
    BMSProperties,
)


def register_props():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bms = PointerProperty(type=BMSProperties)


def unregister_props():
    del bpy.types.Scene.bms

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)