bl_info = {
    "name": "PropRigGenerator", #Can change name here shown in addon page
    "author": "Qwertymama",
    "version": (0, 0, 0, 1),
    "blender": (4, 0, 0),
    "location": "view3d > tool panel"
}

import bpy
from bpy.types import (Panel, Operator)
from mathutils import Vector

class PropRigGeneratorOP(Operator):
    bl_label = "Prop Rig Generator Operator"
    bl_idname = "op.propriggenerator"
    

    def execute(self, context):
        bpy.ops.outliner.orphans_purge()
        #Saving rig as sel_rig
        sel_obj = bpy.context.active_object
#        curr_col_name = bpy.context.collection.name
        curr_col_name = sel_obj.users_collection[0].name
        
        
        #making selected objects collection the active collection
        act_col = bpy.context.view_layer.layer_collection.children[curr_col_name]
        bpy.context.view_layer.active_layer_collection = act_col

        
        #Setting curson location and rotations to 0
#        bpy.context.scene.cursor.location[0] = sel_obj.location[0]
#        bpy.context.scene.cursor.location[1] = sel_obj.location[1]
#        bpy.context.scene.cursor.location[2] = sel_obj.location[2]
        bpy.context.scene.cursor.location[0] = 0
        bpy.context.scene.cursor.location[1] = 0
        bpy.context.scene.cursor.location[2] = 0
        
#        org_loc[0] = sel_obj.location[0]
#        org_loc[1] = sel_obj.location[1]
#        org_loc[2] = sel_obj.location[2]
        org_loc = Vector((sel_obj.location[0], sel_obj.location[1], sel_obj.location[2]))
        
        sel_obj.location[0] = 0
        sel_obj.location[1] = 0
        sel_obj.location[2] = 0

        bpy.context.scene.cursor.rotation_euler[0] = 0
        bpy.context.scene.cursor.rotation_euler[1] = 0
        bpy.context.scene.cursor.rotation_euler[2] = 0

        #Setting origin world centre
#        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')


        #setting selected objects transforms
#        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        ##Adding bone to origind
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        meta_rig_bone = bpy.context.active_object
        bpy.context.object.show_in_front = True
        meta_rig_bone.scale[0] = sel_obj.dimensions[2]
        meta_rig_bone.scale[1] = sel_obj.dimensions[2]
        meta_rig_bone.scale[2] = sel_obj.dimensions[2]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        #Going to posemode to apply rigify type to bone
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.active_pose_bone.rigify_type = "basic.super_copy"
        bpy.ops.object.mode_set(mode='OBJECT')

        #Going back to obj mode to generate rig
        bpy.ops.armature.rigify_collection_set_ui_row(index=0, row=1)
        bpy.ops.pose.rigify_generate()
        
        #Saving rig as sel_rig
        sel_rig = bpy.context.object


        #Outline Clean
        #Renaming Armature -> ObjName_MetaRig and RIG_Armature -> Object_RIGArmature
        meta_rig_bone.name = str(sel_obj.name) + "_MetaRig"
        sel_rig.name = str(sel_obj.name) + "_RigArmature"
        #Creating collections and placing objects in proper collections
        rig_link_col = bpy.data.collections.new(name=str(sel_obj.name)+"_Rig_Link")
        scene_col = bpy.context.scene.collection
        scene_col.children.link(rig_link_col)
        rig_link_col.objects.link(bpy.data.objects[str(sel_rig.name)])
        
        
        bpy.data.collections[curr_col_name].objects.unlink(sel_rig)
        rig_link_col.objects.link(bpy.data.objects[str(sel_obj.name)])
        bpy.data.collections[curr_col_name].name = str(sel_obj.name) + '_ExtraCollection'
        bpy.context.view_layer.layer_collection.children[ str(sel_obj.name)+'_ExtraCollection'].children['WGTS_Armature'].exclude = False
        bpy.data.collections["WGTS_Armature"].hide_viewport = False
        bpy.context.object.data.collections["DEF"].is_visible = True
        
        #Parenting DefBone to object
        bpy.context.object.data.bones.active = bpy.context.object.data.bones["DEF-Bone"]
        bpy.ops.object.select_all(action='DESELECT')
        sel_obj.select_set(True)
        sel_rig.select_set(True)
        bpy.context.view_layer.objects.active = sel_rig
        bpy.ops.object.parent_set(type='BONE')
        
        #Hiding def bone
        bpy.ops.object.select_all(action='DESELECT')
        sel_rig.select_set(True)
        bpy.context.object.data.collections["DEF"].is_visible = False
        
        
        #Duplicating the original mesh to get proper scale of the root ctrl
        dup_obj = sel_obj.copy()
        dup_obj.data = sel_obj.data.copy()
        bpy.context.collection.objects.link(dup_obj)
        sel_obj.select_set(False)
        bpy.context.view_layer.objects.active = dup_obj
        
        inner_ctrl = bpy.data.objects['WGT-RIG-Armature_Bone']
        outer_ctrl = bpy.data.objects['WGT-RIG-Armature_root']
        
        org_inner_ctrl_scale = inner_ctrl.scale[0]
        org_outer_ctrl_scale = outer_ctrl.scale[0]
        
        inner_ctrl.dimensions = Vector((dup_obj.dimensions[0]*1.1, 0.0, dup_obj.dimensions[0]*1.1))
        outer_ctrl.dimensions = Vector((dup_obj.dimensions[0]*2.5, dup_obj.dimensions[0]*2.5, 0.0))
    
        #Setting new ctrl scale
        new_inner_ctrl_scale = inner_ctrl.scale[0]
        new_outer_ctrl_scale = outer_ctrl.scale[0]
        
        #Going back to original scale factors
        inner_ctrl.scale = Vector((org_inner_ctrl_scale, org_inner_ctrl_scale, org_inner_ctrl_scale))
        outer_ctrl.scale = Vector((org_outer_ctrl_scale, org_outer_ctrl_scale, org_outer_ctrl_scale))
       
        #Changing the scale of rigs
        bpy.ops.object.select_all(action='DESELECT')
        inner_ctrl.select_set(True)
        bpy.context.view_layer.objects.active = inner_ctrl
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(value=(new_inner_ctrl_scale/org_inner_ctrl_scale, new_inner_ctrl_scale/org_inner_ctrl_scale, new_inner_ctrl_scale/org_inner_ctrl_scale))
        
        bpy.ops.transform.translate(value=(sel_obj.location[0], sel_obj.location[1], sel_obj.location[2]))
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        outer_ctrl.select_set(True)
        bpy.context.view_layer.objects.active = outer_ctrl
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(value=(new_outer_ctrl_scale/org_outer_ctrl_scale, new_outer_ctrl_scale/org_outer_ctrl_scale, new_outer_ctrl_scale/org_outer_ctrl_scale))
        
        bpy.ops.transform.translate(value=(sel_obj.location[0], sel_obj.location[1], sel_obj.location[2]))
        
        bpy.ops.object.mode_set(mode='OBJECT')


        #Deleting the duplicated object
        bpy.ops.object.select_all(action='DESELECT')
        dup_obj.select_set(True)
        bpy.context.view_layer.objects.active = dup_obj
        bpy.ops.object.delete() 

        bpy.context.view_layer.layer_collection.children[str(sel_obj.name) + "_ExtraCollection"].exclude = True
        
        #placing object back in original location
        bpy.ops.object.select_all(action='DESELECT')
        sel_rig.select_set(True)
        bpy.context.view_layer.objects.active = sel_rig
        sel_rig.location[0] = org_loc[0]
        sel_rig.location[1] = org_loc[1]
        sel_rig.location[2] = org_loc[2]
        
        
        self.report({'INFO'}, "SUCCESSFULLY APPLIED PROP RIG")
        
        return {"FINISHED"}
    
    
    
class PropRigGeneratorPanel(Panel):
    bl_label = "Prop Rig Generator" #Shown in top of panel
    bl_idname = "PT_PropRigGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Prop Rog Generator" #Shown in side of panel
    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.label(text = "Prop Rig Generator", icon = "BONE_DATA")
        row = layout.row()
        row.operator(PropRigGeneratorOP.bl_idname, text = "Generate", icon = "PLAY")
        
        
        
classes = [
    PropRigGeneratorPanel,
    PropRigGeneratorOP
    ]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    
    
