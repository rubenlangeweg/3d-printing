"""Build a presentation-only Mous head from measured external dimensions.
The internal socket and collar engagement are illustrative, not manufacturing CAD.
Run with Blender --python this-file -- --diameter MM --thickness MM --depth MM.
"""
import argparse, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector, Matrix

p=argparse.ArgumentParser()
p.add_argument('--diameter',type=float,default=63)
p.add_argument('--thickness',type=float,default=10.5)
p.add_argument('--depth',type=float,default=28.3,help='Estimated total depth; not measured')
p.add_argument('--socket-diameter',type=float,default=26.37)
p.add_argument('--tab-span',type=float,default=39)
p.add_argument('--mode',choices=['preview','stills','animation'],default='preview')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert 30<a.diameter<100 and 2<a.thickness<a.depth<60
PROJECT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(PROJECT/'rendering/orbit.blend'))
s=bpy.context.scene
for o in bpy.data.objects:
    o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data_clear'):o.data.animation_data_clear()
cam=s.camera
cx,cy,cz=.00006852,.00004406,.019912
head=bpy.data.objects.new('Mous head | visual reference',None);s.collection.objects.link(head)
head.location=(cx,cy,cz)
head['description']='Photo-based external form; measured envelope. Internal socket and collar motion illustrative.'
head['measured_dimensions_mm']=[a.diameter,a.thickness,a.socket_diameter,a.tab_span]
head['estimated_total_depth_mm']=a.depth

def mat(name,value,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(value,value,value,1)
    b.inputs['Roughness'].default_value=roughness
    b.inputs['Specular IOR Level'].default_value=.28
    return m
shell=mat('Mous black housing',.007,.48)
rubber=mat('Mous magnetic face',.012,.72)
collar_mat=mat('Mous locking collar',.005,.53)

def lathe(name,profile,material,parent=head):
    # Closed radial/z cross-section, millimetres; axis is Z.
    n=128;verts=[];faces=[]
    for r,z in profile:
        for i in range(n):
            q=2*math.pi*i/n;verts.append((r*math.cos(q)*.001,r*math.sin(q)*.001,z*.001))
    for j in range(len(profile)):
        k=(j+1)%len(profile)
        for i in range(n):
            h=(i+1)%n;faces.append((j*n+i,j*n+h,k*n+h,k*n+i))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);o.parent=parent
    o.data.materials.append(material)
    for f in mesh.polygons:
        zs=[mesh.vertices[i].co.z for i in f.vertices]
        f.use_smooth=max(zs)-min(zs)>1e-7
    return o

r=a.diameter/2
# Rear opening is 5 mm behind the ball centre, based on photos, not a measured socket.
rear=-5;front=rear-.6+a.depth;back=front-a.thickness
cr=a.socket_diameter/2
lathe('Mous | circular housing',[(.01,back),(r-2,back),(r-.6,back+.4),(r,back+1.2),(r,front-1),(r-.5,front-.3),(r-1.5,front-.1),(.01,front-.1)],shell)
lathe('Mous | inset contact pad',[(.01,front),(r-2,front),(r-1.7,front-.2),(r-1.7,front-.5),(.01,front-.5)],rubber)
# Internal clearance is illustrative; the measured external sleeve is preserved.
lathe('Mous | socket housing',[(cr-2,rear),(cr-1.5,rear+1),(cr-1.5,back-3),(15,back),(.01,back),(.01,9),(9.1,9),(9.1,1),(7.4,rear)],shell)
collar=bpy.data.objects.new('Mous | collar control',None);s.collection.objects.link(collar);collar.parent=head
lathe('Mous | collar ring',[(7.4,rear-.6),(cr-.7,rear-.6),(cr,rear),(cr,rear+5.5),(cr-.5,rear+6),(cr-1.2,rear+6),(cr-1.2,rear+1),(7.4,rear+1)],collar_mat,collar)
for sign in [-1,1]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    tab=bpy.context.object;tab.name='Mous | collar grip';tab.parent=collar
    tab.location=(0,sign*(a.tab_span/2-4)*.001,(rear+2)*.001);tab.dimensions=(.006,.008,.006)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=tab.modifiers.new('Moulded grip corners','BEVEL');bevel.width=.0008;bevel.segments=4
    tab.data.materials.append(collar_mat)
# The complete assembly remains fixed, with the lowest product edge on the ground.
bpy.data.objects['Studio ground'].location.y=min(-.0252,cy-r*.001)-.0001

def aim(position,target):
    cam.location=Vector(position)*.001
    f=(Vector(target)*.001-cam.location).normalized()
    right=f.cross(Vector((0,1,0))).normalized();up=right.cross(f)
    cam.rotation_euler=Matrix((right,up,-f)).transposed().to_euler()
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
s.frame_start=1;s.frame_end=240;s.render.fps=24
s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=100
s.eevee.taa_render_samples=64
for frame in range(1,241):
    seat=smooth((frame-30)/105);turn=smooth((frame-145)/48);orbit=smooth((frame-193)/47)
    head.location.z=cz+.055*(1-seat);head.keyframe_insert(data_path='location',frame=frame)
    collar.rotation_euler.z=math.radians(-60+60*turn);collar.keyframe_insert(data_path='rotation_euler',frame=frame)
    aim((195-20*orbit,90,115+30*orbit),(0,0,33))
    cam.data.ortho_scale=.17
    cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
s.frame_set(1)
folder=PROJECT/'generated/mous-attachment';folder.mkdir(parents=True,exist_ok=True)
s.render.filepath='//../generated/mous-attachment/frames/'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'rendering/mous-attachment.blend'))
if a.mode=='preview':
    s.render.resolution_percentage=50;s.eevee.taa_render_samples=32
    dest=folder/'previews';dest.mkdir(exist_ok=True)
    for frame in [1,83,145,193,240]:
        s.frame_set(frame);s.render.filepath=str(dest/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
elif a.mode=='stills':
    s.frame_set(240);cam.animation_data_clear();s.render.resolution_x=2000;s.render.resolution_y=1500;s.eevee.taa_render_samples=128
    aim((150,85,155),(0,0,14));cam.data.ortho_scale=.145
    s.render.filepath=str(PROJECT/'renders/mous-assembled.png');bpy.ops.render.render(write_still=True)
else:
    dest=folder/'frames';dest.mkdir(exist_ok=True);s.render.filepath=str(dest)+'/'
    bpy.ops.render.render(animation=True)

# Export a normal editable Blender scene containing only the reference head.
bpy.ops.wm.open_mainfile(filepath=str(PROJECT/'rendering/mous-attachment.blend'))
s=bpy.context.scene;s.frame_set(240)
for obj in list(bpy.data.objects):
    if not obj.name.startswith('Mous'):
        bpy.data.objects.remove(obj,do_unlink=True)
    else:
        obj.animation_data_clear()
bpy.data.objects['Mous head | visual reference'].location=(0,0,0)
bpy.data.objects['Mous | collar control'].rotation_euler=(0,0,0)
s.name='Mous head reference | not a print model';s.camera=None
s.frame_start=1;s.frame_end=1;s.frame_set(1)
s.render.filepath='//../generated/mous-reference/'
bpy.data.orphans_purge(do_recursive=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=(0,0,.01)
            area.spaces.active.region_3d.view_distance=.14
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'rendering/mous-head-reference.blend'))
