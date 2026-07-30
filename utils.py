import bpy
import os


# ----------------------------------------
# Get triangle count
# ----------------------------------------

def get_triangle_count(obj):
    if obj is None:
        return 0

    if obj.type != 'MESH':
        return 0

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    try:
        mesh.calc_loop_triangles()
        return len(mesh.loop_triangles)

    finally:
        eval_obj.to_mesh_clear()


# ----------------------------------------
# Copy object
# ----------------------------------------

def duplicate_object(obj):
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()

    if obj.users_collection:
        obj.users_collection[0].objects.link(new_obj)

    else:
        bpy.context.scene.collection.objects.link(new_obj)

    return new_obj


# ----------------------------------------
# Apply Decimate modifier
# ----------------------------------------

def add_decimate_modifier(obj, ratio):
    modifier = obj.modifiers.new(
        name="BMS_Decimate",
        type='DECIMATE'
    )

    modifier.ratio = max(0.0, min(1.0, ratio))
    modifier.use_collapse_triangulate = True

    return modifier


# --------------------------------------------------------
# Apply Modifier
# --------------------------------------------------------

def apply_modifier(obj, modifier):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(
        modifier=modifier.name
    )


# ----------------------------------------
# Create LOD copies
# ----------------------------------------

def create_lod_copy(obj, ratio, suffix):
    lod = duplicate_object(obj)
    lod.name = f"{obj.name}_{suffix}"
    modifier = add_decimate_modifier(lod, ratio)
    apply_modifier(lod, modifier)

    return lod


# ----------------------------------------
# Export as .obj
# ----------------------------------------

def export_obj(obj, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=True,
        export_materials=False,
        export_triangulated_mesh=True
    )


# ----------------------------------------
# Delete objects
# ----------------------------------------

def delete_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.delete()


# ----------------------------------------
# Ensure extension
# ----------------------------------------

def ensure_obj_extension(filepath):
    if not filepath.lower().endswith(".obj"):
        filepath += ".obj"

    return filepath


# ----------------------------------------
# Create export directory
# ----------------------------------------

def ensure_directory(folder):
    folder = bpy.path.abspath(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


# ----------------------------------------
# Create filname
# ----------------------------------------

def build_filename(pattern, obj_name, level_index, triangle_count):
    filename = pattern.format(obj=obj_name, n=level_index, tris=triangle_count)

    return filename