bl_info = {
    "name": "Batch Mesh Simplification",
    "author": "Pentagram",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > BMS",
    "description": "Batch simplify meshes and export LOD models",
    "category": "Object",
}

import bpy

from .props import register_props, unregister_props
from .operators import register_operators, unregister_operators
from .ui import register_ui, unregister_ui


def register():
    register_props()
    register_operators()
    register_ui()


def unregister():
    unregister_ui()
    unregister_operators()
    unregister_props()


if __name__ == "__main__":
    register()