import bpy
import os
import json
from mathutils import *



#Script Config
render_top = 1       #render top perspective ingame
render_persp = 1     #render side perspective
target_dir = 0       #target directory (default "rendered for top", "persp" for side)
save_file = 0        #save file to "modified blends"
fix_script = 0       #fix sth
version  = "6"
#bpy.context.scene.cycles.device = "CPU"
bpy.context.scene.cycles.device = "GPU"


if fix_script:
    pass
render_info_txt = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-1])+'/render_info_.json'

#begin script
with open(render_info_txt, "r") as f:
    ship_dict = json.load(f)


def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#Render Setup
resolution_multiplier = 1
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_percentage = 100 *resolution_multiplier
bpy.context.scene.render.tile_x = 16*resolution_multiplier
bpy.context.scene.render.tile_y = 16*resolution_multiplier

bpy.context.scene.render.threads_mode = "FIXED"
bpy.context.scene.render.threads = 14

bpy.context.scene.render.use_compositing = True
bpy.context.scene.cycles.samples = 200 #100-500
bpy.context.scene.cycles.filter_width = 1

ship_name = bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[-1].split('.')[0]


#Read resolution config from render_info.txt
for key,item in ship_dict.items():
    if item['sprite'] == ship_name:
        ship_config = item
        res = item['scale_']
bpy.context.scene.render.resolution_y = res[0]
bpy.context.scene.render.resolution_x = res[1]
aspect_ratio = res[1]/(1.0*res[0])


#Save file
if save_file:
    blend_name = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-2])+"/blends/"+ship_name+".blend" #Check to modify 
    bpy.ops.wm.save_as_mainfile(filepath=blend_name)

#Render top
if render_top:
    #Switch camera and light setup
    bpy.context.scene.camera = bpy.data.objects['camera_top']
    bpy.data.objects['sun_top'].hide_render = False
    bpy.data.objects['sun_persp'].hide_render = True
    #Switch compositing setup:
    node = bpy.context.scene.node_tree.nodes['Group']
    node.inputs['Saturation'].default_value = 1
    node.inputs['Brightness'].default_value = 1

    #output and render top down
    fname =  bpy.path.abspath(bpy.context.blend_data.filepath)
    for ind  in range(4): #range 4
        png  = ship_config['sprite']+"={}.png".format(ind)
        img_name = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-2])+"/rendered_{}/".format(version)+png
        bpy.data.scenes['Scene'].render.filepath = img_name
        bpy.context.scene.frame_set(ind+1)
        bpy.ops.render.render( write_still=True )

#Render perspective
if render_persp:
    #Switch camera and light setup
    pi  = 3.141592645
    bpy.context.scene.render.tile_x = 16*resolution_multiplier*2
    bpy.context.scene.render.tile_y = 16*resolution_multiplier*2
    cam_top_scale  = bpy.data.objects['camera_top'].data.ortho_scale
    bpy.context.scene.frame_set(1)
    bpy.context.scene.cycles.samples = 200 #100-500
    cam_persp = bpy.data.objects['camera_persp']
    bpy.context.scene.camera = cam_persp
    bpy.data.objects['camera_persp']
    cam_persp.location = (12,22,18)
    cam_persp.rotation_euler = Euler((55.0*pi/180, 0.0*pi/360, 150*pi/180), 'XYZ')
    cam = cam_persp.data
    cam.ortho_scale =cam_top_scale+7
    bpy.data.objects['sun_top'].hide_render = True
    bpy.data.objects['sun_persp'].hide_render = False
    fname =  bpy.path.abspath(bpy.context.blend_data.filepath)
    img_name = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-2])+"/persp_{}/".format(version)+ship_name+".png"
    bpy.context.scene.render.resolution_percentage = 100 *.5
    bpy.data.scenes['Scene'].render.filepath = img_name
    bpy.context.scene.render.resolution_y = 1600
    bpy.context.scene.render.resolution_x = 1600
    #Switch compositing setup:
    node = bpy.context.scene.node_tree.nodes['Group']
    node.inputs['Saturation'].default_value = 1.3
    node.inputs['Brightness'].default_value = 0
    
    
    
    #Trigger render
    bpy.ops.render.render( write_still=True )

bpy.ops.wm.quit_blender()
