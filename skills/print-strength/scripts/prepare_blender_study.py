"""Prepare an added-load, fixed-support VoxelSim scene inside Blender."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def evaluated_geometry(name, factor):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != 'MESH':
        raise ValueError(f'Expected a mesh object: {name}')
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        vertices = [list((evaluated.matrix_world @ v.co) * factor) for v in mesh.vertices]
        faces = [list(p.vertices) for p in mesh.polygons]
    finally:
        evaluated.to_mesh_clear()
    edges = Counter(tuple(sorted((face[i], face[(i + 1) % len(face)])))
                    for face in faces for i in range(len(face)))
    if not faces or any(count != 2 for count in edges.values()):
        raise ValueError(f'{name} must be a closed manifold mesh')
    return {'vertices': vertices, 'faces': faces}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', required=True)
    parser.add_argument('--support', action='append', required=True)
    parser.add_argument('--load-object', required=True)
    parser.add_argument('--metres-per-unit', type=float, required=True)
    parser.add_argument('--mass-kg', type=float, required=True)
    parser.add_argument('--direction', nargs=3, type=float, default=[0, 0, -1])
    parser.add_argument('--youngs-gpa', type=float, required=True)
    parser.add_argument('--poisson', type=float, required=True)
    parser.add_argument('--resolution', type=int, default=64)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    values = [args.metres_per_unit, args.mass_kg, args.youngs_gpa, args.poisson, *args.direction]
    if not all(math.isfinite(value) for value in values):
        parser.error('Physical inputs must be finite')
    if min(args.metres_per_unit, args.mass_kg, args.youngs_gpa) <= 0:
        parser.error('Scale, mass and modulus must be positive')
    if args.youngs_gpa < 0.0001:
        parser.error('VoxelSim requires a modulus of at least 0.0001 GPa')
    if not 0 <= args.poisson <= 0.49 or not 4 <= args.resolution <= 200:
        parser.error('Use Poisson ratio 0..0.49 and resolution 4..200')
    direction = Vector(args.direction)
    if direction.length == 0:
        parser.error('Load direction must be nonzero')
    if len(set([args.part, *args.support, args.load_object])) != 2 + len(args.support):
        parser.error('Part, supports and load selector must be distinct objects')
    output = args.output.expanduser().resolve()
    report = output.with_suffix('.study.json')
    if output.suffix != '.blend' or output.exists() or report.exists():
        parser.error('Choose a fresh .blend output and sidecar path')
    if not hasattr(bpy.context.scene, 'blendfea'):
        parser.error('Enable the external VoxelSim FEA add-on before running this helper')
    source = Path(bpy.data.filepath) if bpy.data.filepath else None
    names = [args.part, *args.support, args.load_object]
    geometry = {name: evaluated_geometry(name, args.metres_per_unit) for name in names}
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest() if source else None
    geometry_hash = hashlib.sha256(json.dumps(geometry, sort_keys=True).encode()).hexdigest()
    # Retain only the selected, evaluated meshes in the analysis file.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if not hasattr(scene, 'blendfea'):
        raise RuntimeError('VoxelSim settings did not survive the scene reset')
    objects = {}
    for name, data in geometry.items():
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(data['vertices'], [], data['faces'])
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        objects[name] = obj
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    settings = scene.blendfea
    settings.part = objects[args.part]
    settings.bearings.clear()
    settings.loads.clear()
    for name in args.support:
        bearing = settings.bearings.add()
        bearing.obj = objects[name]
        bearing.fix_x = bearing.fix_y = bearing.fix_z = True
        objects[name].display_type = 'WIRE'
    load = settings.loads.add()
    load.obj = objects[args.load_object]
    force = direction.normalized() * (args.mass_kg * 9.80665)
    load.force = force
    objects[args.load_object].display_type = 'WIRE'
    settings.material_preset = 'CUSTOM'
    settings.youngs_modulus = args.youngs_gpa
    settings.poisson = args.poisson
    settings.yield_strength = 0
    settings.resolution = args.resolution
    settings.compute_mode = 'CPU'
    settings.cpu_threads = 4
    settings.result_view = 'NONE'
    bpy.context.view_layer.objects.active = objects[args.part]
    objects[args.part].select_set(True)
    scene['study_scope'] = 'Fixed support, added load only, isotropic solid reference'
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    manifest = vars(args).copy()
    manifest['output'] = output.name
    manifest.update(source_scene_sha256=source_hash, evaluated_geometry_sha256=geometry_hash,
                    force_N=list(force), self_weight_included=False,
                    support_model='All XYZ translations fixed on selected support nodes',
                    analysis_coordinates='Raw world metres; Unit Scale 1',
                    solved=False, blender_version=bpy.app.version_string)
    report.write_text(json.dumps(manifest, indent=2))
    print(f'Prepared {output.name}; open Blender and run FEA after inspecting the selectors.')


if __name__ == '__main__':
    main()
