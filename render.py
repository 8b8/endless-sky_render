import bpy
import os
from mathutils import *

#image_file_dir = 'ships/'


#Script Config
render_top = True
render_persp = False
target_dir = False


render_info_txt = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-1])+'/render_info.txt'

with open(render_info_txt, "r") as f:
    render_info_ = f.readlines()
ship_dict = {}
for line in render_info_:
    if line.startswith('ship'):
        ship = line[6:][:-1]
        ship_dict.update({ship : {}})
    if line.find('sprite') > 0:
        ship_dict[ship].update({'sprite': line.split('\t')[-1][:-1]})
    if line.find('shape') > 0:
        ship_dict[ship].update({'shape': [int(x) for x in line.split('\t')[-1][1:-2].split(',')]})


def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#Render Setup
postfix = "_2"
resolution_multiplier = 2
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_percentage = 100 *resolution_multiplier
bpy.context.scene.render.tile_x = 16*resolution_multiplier
bpy.context.scene.render.tile_y = 16*resolution_multiplier
bpy.context.scene.render.use_compositing = True
bpy.context.scene.cycles.samples = 200 #100-500
bpy.context.scene.cycles.filter_width = .3





cam_top = [o for o in bpy.data.objects if o.type == 'CAMERA'][0]
scale = bpy.data.cameras[0].ortho_scale
bpy.context.scene.cycles.film_transparent = True
#bpy.context.scene.cycles.device = "CPU"
bpy.context.scene.cycles.device = "GPU"



material_file = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-1])+'/_materials_human.blend'
ship_name = bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[-1].split('.')[0]

for key,item in ship_dict.items():
    if item['sprite'] == ship_name:
        res = item['shape']

bpy.context.scene.render.resolution_y = res[0]
bpy.context.scene.render.resolution_x = res[1]
#match resolution
#image_file = bpy.data.images.load(image_file_dir.format(user,ship_name))
#bpy.context.scene.render.resolution_x = image_file.size[0]
#bpy.context.scene.render.resolution_y = image_file.size[1]


def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


#Shows a message box with a specific message 
#ShowMessageBox(material_file) 

with bpy.data.libraries.load(material_file, link=True) as (data_from, data_to):
    data_to.materials = data_from.materials
    data_to.node_groups = data_from.node_groups

#Material Setup
for material in bpy.data.materials:
    if not material.node_tree:
        material.use_nodes = True
        color = material.diffuse_color
        tree = material.node_tree
        for node in tree.nodes:
            tree.nodes.remove(node)
        #output = tree.nodes['Material Output'] 
        #shader = tree.nodes['Principled BSDF']
        #tree.nodes.remove(output)
        #tree.nodes.remove(shader)
        tree.nodes.new('ShaderNodeGroup')
        tree.nodes['Group'].node_tree = bpy.data.node_groups['Bulkhead']
        tree.nodes['Group'].inputs[0].default_value = tuple([k**.7 for k in color]+[1.0])

#Geometry soften
for object in bpy.data.objects:
    if object.type == 'MESH':
        object.modifiers.new(name = 'keep_geom', type = 'BEVEL')
        object.modifiers.new(name = 'smooth', type = 'SUBSURF')
        keep = object.modifiers['keep_geom']
        smooth = object.modifiers['smooth']
        keep.limit_method = "ANGLE"
        keep.offset_type = "WIDTH"
        #smooth.limit_method = "ANGLE"
        #smooth.offset_type = "WIDTH"
        keep.segments = 3
        smooth.levels = 2

 #Lighting Setup
bpy.context.scene.view_layers[0].use_pass_ambient_occlusion = True
bpy.context.scene.world.light_settings.use_ambient_occlusion = False
for lamp in bpy.data.lights:
    if lamp.type == "SUN":
        for o in bpy.data.objects:
            if o.data==lamp:
                sun = o
        #sun = bpy.data.objects[lamp.name]
                lamp.use_nodes  = True
                lamp.node_tree.nodes['Emission'].inputs['Strength'].default_value = 5 # 5 ,7
                lamp.shadow_soft_size = .1
    else:
        lamp.color = (0,0,0)

#bpy.data.lights['Sun'].use_nodes  = True
#bpy.data.lights['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 5

bpy.context.scene.world.use_nodes = True
#bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.04,0.04,0.04,1)

bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.08,0.08,0.08,1)

#Center Object:
largest_ob = 0
for o in bpy.data.objects:
    bb = o.bound_box
    break

# Setup Compositing
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

for node in tree.nodes:
    tree.nodes.remove(node)

input_node = tree.nodes.new('CompositorNodeRLayers')
output_node = tree.nodes.new('CompositorNodeGroup')
output_node.node_tree = bpy.data.node_groups['Compositing']
tree.links.new(input_node.outputs['Image'], output_node.inputs['Image'])
tree.links.new(input_node.outputs['Alpha'], output_node.inputs['Alpha'])
tree.links.new(input_node.outputs['AO'], output_node.inputs['AmbientOclusion'])

#output and render top down
fname =  bpy.path.abspath(bpy.context.blend_data.filepath)
#img_name = fname[:-6]+postfix+'.png'
#img_name = fname[:-6]+postfix+'.png'
if target_dir:
    img_name = target_dir+"/"+ship_name+".png"
else:
    img_name = os.sep.join(bpy.path.abspath(bpy.context.blend_data.filepath).split('/')[:-2])+"/rendered/"+ship_name+".png"
bpy.data.scenes['Scene'].render.filepath = img_name
if render_top:
    bpy.ops.render.render( write_still=True )
if render_persp:
#setup camera perspective render
    pi = 3.141592645
    cam = bpy.data.cameras.new("Camera")
    cam_ob = bpy.data.objects.new("Camera", cam)
    bpy.context.collection.objects.link(cam_ob)
    ##First cam from front left
    #cam_ob.location = (-65.6,175.4,95.4)
    #cam_ob.rotation_euler = Euler((63.0*pi/180, 0.0*pi/360, 200.0*pi/180), 'XYZ')
    ##Cam from front right
    #cam_ob.location = (6+cam_top.location[0],26+cam_top.location[1],8)
    #cam_ob.rotation_euler = Euler((73.0*pi/180, 0.0*pi/360, 167*pi/180), 'XYZ')
    #cam.type = 'PERSP'
    #cam.lens  = 400
    #cam.lens  = 60*28.0**.5/(scale*.1+scale**.5)
    #Cam Ortho front right

    cam_ob.location = (6+cam_top.location[0],26+cam_top.location[1],14)
    cam_ob.rotation_euler = Euler((62.0*pi/180, 0.0*pi/360, 167*pi/180), 'XYZ')
    cam.type = 'ORTHO'
    #cam.ortho_scale = 2*5.3**2/(scale**2)+28*scale/36
    cam.ortho_scale = 5+28*scale/36+20/scale
    print("Scale: {}, OrthoScale: {}".format(scale, cam.ortho_scale))

    #cam.lens  = 400
    #cam.lens  = 60*28.0**-5/(scale*.1+scale**.5)


    cam.sensor_width = 36
    bpy.context.scene.camera = cam_ob



    #Change sun rotation to make the lighting less flat
    sun.location = (-15,13,18)
    sun.rotation_euler = Euler((0*pi/180,65*pi/360, 147*pi/180), 'XYZ')
    #
    #quit after rendering


    fname =  bpy.path.abspath(bpy.context.blend_data.filepath)
    #img_name = fname[:-6]+'persp'+postfix+'.png'
    bpy.data.scenes['Scene'].render.filepath = img_name
    bpy.context.scene.render.resolution_y = 1600
    bpy.context.scene.render.resolution_x = 1600
    #bpy.ops.render.render( write_still=True )

bpy.ops.wm.quit_blender()
