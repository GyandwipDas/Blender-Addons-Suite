bl_info = {
    "name": "TestOrFinalRenderer", #Can change name here shown in addon page
    "author": "Qwertymama",
    "version": (0, 1, 1, 0),
    "blender": (4, 0, 0),
    "location": "view3d > tool panel"
}

import bpy
from bpy.types import (Panel, Operator)

class TestORFinalRendererOP(Operator):
    bl_label = "Test/Final Renderer Operator"
    bl_idname = "op.testorfinalrenderer"

    render_type : bpy.props.StringProperty(name = "Render Type", default = "test")

    def execute(self, context):

        #-----------RENDER SETTINGS-----------
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'

        #sampling
        bpy.context.scene.cycles.preview_samples = 28
        bpy.context.scene.cycles.samples = 28 if self.render_type == "test" else 512

        #optionals
        # bpy.context.scene.cycles.use_preview_denoising = True
        # bpy.context.scene.cycles.preview_denoiser = 'OPTIX'

        #light bounces
        bpy.context.scene.cycles.max_bounces = 8
        bpy.context.scene.cycles.transmission_bounces = 8
        bpy.context.scene.cycles.diffuse_bounces = 4
        bpy.context.scene.cycles.glossy_bounces = 4
        bpy.context.scene.cycles.transmission_bounces = 8
        bpy.context.scene.cycles.volume_bounces = 0
        bpy.context.scene.cycles.transparent_max_bounces = 8

        #simplify
        #viewport
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0
        bpy.context.scene.render.simplify_subdivision = 0
        bpy.context.scene.cycles.texture_limit = '512'
        bpy.context.scene.render.simplify_volumes = 0
        bpy.context.scene.render.simplify_child_particles = 0

        #render
        bpy.context.scene.render.simplify_subdivision_render = 2
        bpy.context.scene.render.simplify_child_particles_render = 1
#        bpy.context.scene.cycles.texture_limit_render = '512' if self.render_type == "test" else '2048'
        bpy.context.scene.cycles.texture_limit_render = '2048'

        #film
        bpy.context.scene.render.film_transparent = True
        #optional(could make or break render)
        bpy.context.scene.cycles.film_transparent_glass = False

        #performance
        bpy.context.scene.render.use_persistent_data = True if self.render_type == "test" else False

        #color Mgt.
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.view_settings.look = 'None'


        #-----------OUTPUT SETTINGS-----------
        #format
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.resolution_percentage = 100
        bl_version = bpy.app.version_string.rsplit('.', 1)[0]
#        bpy.context.scene.render.filepath = bl_version
        bpy.ops.script.execute_preset(filepath="C:\\Program Files\\Blender Foundation\\Blender " + bl_version + "\\" + bl_version + "\\scripts\\presets\\framerate\\25.py", menu_idname="RENDER_MT_framerate_presets")

        #output
#        bpy.context.scene.render.filepath = "//"
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.render.image_settings.compression = 100
        bpy.context.scene.render.use_overwrite = True
        bpy.context.scene.render.use_placeholder = False
        bpy.context.scene.render.image_settings.color_management = 'FOLLOW_SCENE'


        #-----------FILE SETTINGS-----------
        #autopack
        bpy.data.use_autopack = True

        #cleanup
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


        #-----------SEQUENCER-----------
        #video/images
        bpy.context.area.ui_type = 'SEQUENCE_EDITOR'
        bpy.ops.sequencer.select_all(action = 'SELECT')
        bpy.ops.sequencer.delete()
        #markers
        bpy.ops.marker.add()
        bpy.ops.marker.select_all(action='SELECT')
        bpy.ops.marker.delete()


        #-----------COMPOSITOR-----------
        bpy.context.area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.scene.node_tree.nodes.new(type = "CompositorNodeOutputFile")
        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].format.file_format = 'PNG'
        bpy.data.scenes["Scene"].node_tree.nodes["Composite"].use_alpha = True


        #-----------ADDING LIGHT COLLECTION-----------
        # bpy.context.area.ui_type = 'OUTLINER'
        # bpy.ops.outliner.item_activate()
        # bpy.ops.outliner.collection_new(nested=True)

        # #checking if 3rd last, 2nd last and last collection names are lighting
        # for col in bpy.data.collections:
        #     count += 1
        # if (bpy.data.collections[count-1].name != "Lighting") and (bpy.data.collections[count-2].name != "Lighting") and (bpy.data.collections[count-3].name != "Lighting"):
        #     bpy.data.collections[count-1].name = "Lighting"




        #-----------3D VIEWPORT-----------
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False



        #-----------SUCCESS MESSAGE-----------
        self.report({'INFO'}, "SUCCESSFULLY APPLIED " + ("TEST" if self.render_type == "test" else "FINAL") + " SETTINGS!")



        return {"FINISHED"}



class TestORFinalRendererPanel(Panel):
    bl_label = "Test/Final Renderer" #Shown in top of panel
    bl_idname = "PT_TestOrFinalRenderer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Test/Final Rendereer" #Shown in side of panel

    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.label(text = "Test render", icon = "RENDER_STILL")
        row = layout.row()
        row.operator(TestORFinalRendererOP.bl_idname, text = "Test Render", icon = "PLAY").render_type = "test"


        obj = context.object
        row = layout.row()
        row.label(text = "Final render", icon = "RESTRICT_RENDER_OFF")
        row = layout.row()
        row.operator(TestORFinalRendererOP.bl_idname, text = "Final Render", icon = "PLAY").render_type = "final"





classes = [
    TestORFinalRendererPanel,
    TestORFinalRendererOP,

    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
