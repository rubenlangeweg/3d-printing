"""Blender 5: render accepted geometry. Paths resolve from this script.
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- preview
Modes: preview, stills, animation, orbit. Frames remain in generated/.
"""
import bpy, math, sys, shutil, json, argparse
from pathlib import Path
from mathutils import Vector, Matrix

PROJECT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('mode',choices=['preview','stills','animation','orbit'],nargs='?',default='preview')
parser.add_argument('--preset',type=Path,default=PROJECT.parents[1]/'rendering/presets/black.json')
options=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
mode=options.mode
palette=json.loads(options.preset.read_text())
bpy.ops.wm.open_mainfile(filepath=str(PROJECT/'source/holder-without-ribs.blend'))
scene=bpy.context.scene
base=bpy.data.objects['Base - rounded roots - no ribs']
ball=bpy.data.objects['Ball module - 17 mm']
for o in [base,ball]:
    o.data.transform(Matrix.Scale(.001,4));o.location*=.001
    o.data.materials.clear()
    for p in o.data.polygons:p.use_smooth=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1

def material(name,color,roughness,specular=.28):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    shader=m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1)
    m.diffuse_color=(*color,1)
    shader.inputs['Roughness'].default_value=roughness
    shader.inputs['Specular IOR Level'].default_value=specular
    return m
black=material('Black satin plastic',palette['product']['base_color'][:3],palette['product']['roughness'],palette['product'].get('specular_ior_level',.28))
base.data.materials.append(black)
ball.data.materials.append(black)
for p in ball.data.polygons:
    # Smooth the ball; keep its flat underside, neck and dovetail edges crisp.
    if p.center.z>.013: p.use_smooth=True
world=bpy.data.worlds.new('Studio world');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=palette['world']['color']
world.node_tree.nodes['Background'].inputs[1].default_value=palette['world']['strength'];scene.world=world
def aim(obj,position,target):
    obj.location=Vector(position)*.001
    f=(Vector(target)*.001-obj.location).normalized()
    right=f.cross(Vector((0,1,0))).normalized();up=right.cross(f)
    obj.rotation_euler=Matrix((right,up,-f)).transposed().to_euler()
def light(name,position,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size*.001
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);aim(o,position,(0,0,0))
light('Key softbox',(-80,100,110),.6,90)
light('Fill softbox',(100,40,60),.25,80)
light('Rim softbox',(10,100,-100),.8,70)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,-.0253,0),rotation=(math.pi/2,0,0))
floor=bpy.context.object;floor.name='Studio ground';floor.data.materials.append(material('Warm grey ground',palette['floor']['base_color'][:3],palette['floor']['roughness']))
camera_data=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camera_data);scene.collection.objects.link(cam);scene.camera=cam
cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=20
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.use_persistent_data=True
if sys.platform=='darwin':
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL';prefs.get_devices()
    if any(d.type=='METAL' for d in prefs.devices):
        for d in prefs.devices:d.use=(d.type=='METAL')
        scene.cycles.device='GPU'
scene.render.use_compositing=False;scene.render.use_sequencer=False
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.view_settings.view_transform=palette['view_transform']
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=144
scene.render.use_file_extension=True
scene.render.image_settings.color_mode='RGB'
scene.render.use_stamp=False
def view(position,target,scale,width=1400,height=1100):
    aim(cam,position,target);cam.data.ortho_scale=scale*.001
    scene.render.resolution_x=width;scene.render.resolution_y=height
def render(name):
    scene.render.filepath=str(PROJECT/'renders'/name);bpy.ops.render.render(write_still=True)

if mode in ('stills','preview'):
    view((95,70,135),(0,0,0),102)
    if mode=='preview':
        scene.render.resolution_percentage=60;scene.cycles.samples=24
    render('assembled.png')
    if mode=='stills':
        ball.hide_render=True
        view((-90,80,-130),(0,0,-6),95);render('rear-roots.png')
        ball.hide_render=False;ball.location.y=.042
        view((85,65,155),(0,17,3),118,1400,1400);render('exploded.png')
        ball.location.y=0
elif mode=='animation':
    view((70,50,155),(0,16,4),123,800,800)
    scene.cycles.samples=16
    for frame,y in [(1,.042),(24,.042),(108,0),(144,0)]:
        ball.location.y=y;ball.keyframe_insert(data_path='location',frame=frame)
    scene.frame_set(1)
    frames=PROJECT/'generated/frames';frames.mkdir(parents=True,exist_ok=True)
    scene.render.filepath='//../generated/frames/'
    bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'rendering/assembly.blend'))
    for frame in range(1,145):
        path=frames/f'{frame:04d}.png'
        held=1 if 1<frame<=24 else 108 if frame>108 else None
        if held is not None:
            shutil.copyfile(frames/f'{held:04d}.png',path)
            continue
        scene.frame_set(frame);scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
elif mode=='orbit':
    view((95,65,135),(0,0,0),102,800,800)
    scene.cycles.samples=16;scene.frame_end=288
    pivot=bpy.data.objects.new('Camera orbit',None);scene.collection.objects.link(pivot)
    cam.parent=pivot
    for frame,angle in [(1,0),(289,2*math.pi)]:
        pivot.rotation_euler.y=angle;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
    for layer in pivot.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(1)
    frames=PROJECT/'generated/orbit-frames';frames.mkdir(parents=True,exist_ok=True)
    scene.render.filepath='//../generated/orbit-frames/'
    bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'rendering/orbit.blend'))
    scene.render.filepath=str(frames)+'/'
    bpy.ops.render.render(animation=True)
else: raise ValueError(mode)
