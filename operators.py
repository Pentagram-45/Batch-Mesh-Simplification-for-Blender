import bpy
import re

from bpy.types import Operator
from bpy.props import EnumProperty
from .props import BMSLevel
from .utils import (
    get_triangle_count,
    create_lod_copy,
    export_obj,
    delete_object,
    ensure_directory,
    ensure_obj_extension,
    build_filename,
)



# ========================================================
# 添加一个LOD
# ========================================================

class BMS_OT_level_add(Operator):

    bl_idname = "bms.level_add"
    bl_label = "Add LOD Level"
    bl_description = "Add a new LOD level"

    def execute(self, context):

        props = context.scene.bms

        item = props.levels.add()

        item.mode = "TRIS"
        item.target_tris = 10000
        item.target_percent = 50.0
        item.target_ratio = 0.5

        props.level_index = len(props.levels) - 1

        return {'FINISHED'}


# ========================================================
# 删除LOD
# ========================================================

class BMS_OT_level_remove(Operator):

    bl_idname = "bms.level_remove"
    bl_label = "Remove LOD Level"
    bl_description = "Remove selected LOD level"

    @classmethod
    def poll(cls, context):

        return len(context.scene.bms.levels) > 0

    def execute(self, context):

        props = context.scene.bms

        index = props.level_index

        if index < 0:

            return {'CANCELLED'}

        if index >= len(props.levels):

            return {'CANCELLED'}

        props.levels.remove(index)

        if len(props.levels) == 0:

            props.level_index = 0

        else:

            props.level_index = min(
                index,
                len(props.levels) - 1
            )

        return {'FINISHED'}


# ========================================================
# 上下移动LOD
# ========================================================

class BMS_OT_level_move(Operator):

    bl_idname = "bms.level_move"
    bl_label = "Move LOD Level"

    direction: EnumProperty(
        items=[
            ('UP', "Up", ""),
            ('DOWN', "Down", "")
        ]
    )

    @classmethod
    def poll(cls, context):

        return len(context.scene.bms.levels) > 1

    def execute(self, context):

        props = context.scene.bms

        index = props.level_index

        if self.direction == 'UP':

            if index <= 0:

                return {'CANCELLED'}

            props.levels.move(index, index - 1)

            props.level_index -= 1

        else:

            if index >= len(props.levels) - 1:

                return {'CANCELLED'}

            props.levels.move(index, index + 1)

            props.level_index += 1

        return {'FINISHED'}

# ========================================================
# Quick Add
# ========================================================

class BMS_OT_quick_add(Operator):

    bl_idname = "bms.quick_add"
    bl_label = "Quick Add"
    bl_description = "Add LOD levels from text"

    # -------------------------
    # 解析一个字符串
    # -------------------------

    def parse_token(self, token):

        token = token.strip().lower()

        if token == "":
            return None

        # 50%

        if token.endswith("%"):

            try:
                value = float(token[:-1])
            except ValueError:
                return None

            return (
                "PERCENT",
                value
            )

        # 10k

        if token.endswith("k"):

            try:
                value = float(token[:-1]) * 1000
            except ValueError:
                return None

            return (
                "TRIS",
                int(value)
            )

        # 2m

        if token.endswith("m"):

            try:
                value = float(token[:-1]) * 1000000
            except ValueError:
                return None

            return (
                "TRIS",
                int(value)
            )

        # 普通数字

        try:

            value = float(token)

        except ValueError:

            return None

        # Ratio

        if 0.0 <= value <= 1.0:

            return (
                "RATIO",
                value
            )

        # Triangle Count

        return (
            "TRIS",
            int(value)
        )

    # -------------------------
    # Execute
    # -------------------------

    def execute(self, context):

        props = context.scene.bms

        text = props.quick_add_text

        if text.strip() == "":

            self.report(
                {'WARNING'},
                "Input is empty."
            )

            return {'CANCELLED'}

        count = 0

        for token in text.split(","):

            parsed = self.parse_token(token)

            if parsed is None:
                continue

            mode, value = parsed

            item = props.levels.add()

            item.mode = mode

            if mode == "TRIS":

                item.target_tris = int(value)

            elif mode == "PERCENT":

                item.target_percent = float(value)

            else:

                item.target_ratio = float(value)

            count += 1

        if count == 0:

            self.report(
                {'WARNING'},
                "No valid level found."
            )

            return {'CANCELLED'}

        props.level_index = len(props.levels) - 1

        self.report(
            {'INFO'},
            f"Added {count} LOD level(s)."
        )

        return {'FINISHED'}

class BMS_OT_run(Operator):

    bl_idname = "bms.run"
    bl_label = "Batch Simplify & Export"

    bl_options = {'REGISTER', 'UNDO'}

    # ----------------------------------------------------
    # 获取处理目标
    # ----------------------------------------------------

    def get_targets(self, context):

        props = context.scene.bms

        if props.use_collection and props.collection:

            return [
                obj
                for obj in props.collection.objects
                if obj.type == 'MESH'
            ]

        if props.use_selected:

            return [
                obj
                for obj in context.selected_objects
                if obj.type == 'MESH'
            ]

        return [
            obj
            for obj in context.scene.objects
            if obj.type == 'MESH'
        ]

    # ----------------------------------------------------
    # Execute
    # ----------------------------------------------------

    def execute(self, context):

        props = context.scene.bms

        if not props.export_dir:

            self.report(
                {'ERROR'},
                "Please choose an export folder."
            )

            return {'CANCELLED'}

        if len(props.levels) == 0:

            self.report(
                {'ERROR'},
                "No LOD level."
            )

            return {'CANCELLED'}

        targets = self.get_targets(context)

        if len(targets) == 0:

            self.report(
                {'WARNING'},
                "No mesh found."
            )

            return {'CANCELLED'}

        export_dir = ensure_directory(
            props.export_dir
        )

        view_layer = context.view_layer

        old_active = view_layer.objects.active

        old_selection = list(context.selected_objects)

        exported = 0

        try:

            for obj in targets:

                base_tris = get_triangle_count(obj)

                for index, level in enumerate(
                        props.levels,
                        start=1):

                    ratio = level.get_ratio(base_tris)

                    lod = create_lod_copy(
                        obj,
                        ratio,
                        f"LOD{index}"
                    )

                    lod_tris = get_triangle_count(lod)

                    filename = build_filename(

                        props.filename_pattern,

                        obj.name,

                        index,

                        lod_tris

                    )

                    filepath = os.path.join(

                        export_dir,

                        filename

                    )

                    filepath = ensure_obj_extension(
                        filepath
                    )

                    export_obj(

                        lod,

                        filepath

                    )

                    delete_object(lod)

                    exported += 1

        except Exception as e:

            self.report(
                {'ERROR'},
                str(e)
            )

            return {'CANCELLED'}

        finally:

            bpy.ops.object.select_all(
                action='DESELECT'
            )

            for obj in old_selection:

                if obj.name in bpy.data.objects:

                    obj.select_set(True)

            view_layer.objects.active = old_active

        self.report(
            {'INFO'},
            f"Exported {exported} mesh(es)."
        )

        return {'FINISHED'}


classes = (

    BMS_OT_level_add,

    BMS_OT_level_remove,

    BMS_OT_level_move,

    BMS_OT_quick_add,

    BMS_OT_run,

)


def register_operators():

    for cls in classes:

        bpy.utils.register_class(cls)


def unregister_operators():

    for cls in reversed(classes):

        bpy.utils.unregister_class(cls)