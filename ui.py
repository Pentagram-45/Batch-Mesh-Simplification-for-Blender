import bpy

from bpy.types import (
    Panel,
    UIList,
)


#----------------------------------------
# LOD List
#----------------------------------------

class BMS_UL_levels(UIList):

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):

        row = layout.row(align=True)
        row.prop(item, "mode", text="")

        if item.mode == "TRIS":
            row.prop(item, "target_tris", text="")

        elif item.mode == "PERCENT":
            row.prop(item, "target_percent", text="")

        else:
            row.prop(item, "target_ratio", text="")


#----------------------------------------
# Main Panel
#----------------------------------------

class BMS_PT_main(Panel):

    bl_label = "Batch Mesh Simplification"
    bl_idname = "BMS_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BMS"

    def draw(self, context):
        layout = self.layout

        props = context.scene.bms

        #----------------------------------------
        # Export
        #----------------------------------------

        box = layout.box()
        box.label(text="Export", icon='EXPORT')
        box.prop(props, "export_dir")
        box.prop(props, "filename_pattern")

        #----------------------------------------
        # Target objects(s)
        #----------------------------------------

        box = layout.box()
        box.label(text="Target", icon='OUTLINER_COLLECTION')
        box.prop(props, "use_selected")
        box.prop(props, "use_collection")

        if props.use_collection:
            box.prop(props, "collection")

        #----------------------------------------
        # LOD
        #----------------------------------------

        box = layout.box()
        box.label(text="LOD Levels", icon='MOD_DECIM')

        row = box.row()
        row.template_list("BMS_UL_levels", "", props, "levels", props, "level_index", rows=5)

        col = row.column(align=True)
        col.operator("bms.level_add", icon='ADD', text="")
        col.operator("bms.level_remove", icon='REMOVE', text="")
        col.separator()

        op = col.operator("bms.level_move", icon='TRIA_UP', text="")
        op.direction = 'UP'
        op = col.operator("bms.level_move", icon='TRIA_DOWN', text="")
        op.direction = 'DOWN'

        #----------------------------------------
        # Quick add
        #----------------------------------------

        box.separator()
        box.prop(props, "quick_add_text")
        box.operator("bms.quick_add", icon='PLUS')

        #----------------------------------------
        # Run
        #----------------------------------------

        layout.separator()
        layout.scale_y = 1.6
        layout.operator("bms.run", icon='FILE_TICK')

#----------------------------------------
#Register & Unregister
#----------------------------------------

classes = (
    BMS_UL_levels,
    BMS_PT_main,
)


def register_ui():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_ui():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)