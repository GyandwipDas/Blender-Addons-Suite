bl_info = {
    "name": "Duplicate Light Remover", #Can change name here shown in addon page
    "author": "Qwertymama",
    "version": (0, 0, 0, 1),
    "blender": (5, 0, 1),
    "location": "view3d > tool panel"
}

import bpy

from bpy.types import(Panel, Operator)

class DupObjectDeleteOP(Operator):
    """Deletes dulicate objects that get are linked with the lights when appended/copied"""
    bl_idname = "delete.dup_obj"
    bl_label = "Delete Duplicate Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ltlist_old={}
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                ltlist = {}
                lkltcol = obj.light_linking.receiver_collection
                init_size = len(lkltcol.collection_objects)
                for i,lkobj in enumerate(lkltcol.collection_objects):
                    if i >= init_size:
                        for j in ltlist.keys():
                            lkltcol.objects.unlink(bpy.data.objects[j])
                            print("UNLINKING ->", lkltcol, j)
                        print('im out of here')
                        break

                    if "." not in lkobj.id_data.all_objects[i].name:
                        print("Looks like my job is done")
                        break;
                    ltlist[lkobj.id_data.all_objects[i].name]='INCLUDE' if lkobj.light_linking.link_state == "INCLUDE" else 'EXCLUDE'
                    base, num = lkobj.id_data.all_objects[i].name.rsplit('.', 1)
                    print("BASE", base, "NUM", num)
                    new_name = ""
                    if num == "001":
                        num = ""
                        new_name = f"{base}"
                    elif f"{int(num) - 1:03d}" > '000':
                        new_name = f"{base}.{int(num) - 1:03d}"
                    else:
                        break
                    

                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.data.objects[new_name].select_set(1)
                    print("SELECTING", new_name)

                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(1)

                    bpy.ops.object.light_linking_receivers_link(link_state='INCLUDE' if lkobj.light_linking.link_state == "INCLUDE" else 'EXCLUDE')
                bpy.context.scene.collection.children.unlink(lkltcol)
        return {"FINISHED"}


class DupLightRemoverPanel(Panel):
    bl_label = "Duplicate Light Remover"
    bl_idname = "PT_DupLightRemover"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Duplicate Light Remover"
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.object
        row = layout.row()
        row.label(text = "Delete Duplicate Lights", icon = "HIDE_ON")
        row = layout.row()
        row.operator(DupObjectDeleteOP.bl_idname, text="Delete", icon = "REMOVE")



classes = [
    DupObjectDeleteOP,
    DupLightRemoverPanel,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
