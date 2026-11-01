"""Apply a palette to named materials and save a new Blender scene.

Run with an existing scene open, for example:
blender -b scene.blend --python rendering/apply_style.py -- \
    --preset warm-ivory --material 'Warm ivory matte plastic' \
    --output generated/styled.blend

Only explicitly named materials change. Meshes, transforms, cameras and lights
are preserved. World changes require --world.
"""
import argparse
import json
from pathlib import Path
import sys
import bpy


def apply_material(name, settings):
    material = bpy.data.materials.get(name)
    if material is None:
        raise ValueError(f"Material not found: {name}")
    material.use_nodes = True
    shader = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if shader is None:
        raise ValueError(f"No Principled BSDF in material: {name}")
    color = settings['base_color']
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = settings['roughness']
    if 'specular_ior_level' in settings:
        shader.inputs['Specular IOR Level'].default_value = settings['specular_ior_level']
    material.diffuse_color = color


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preset', choices=['warm-ivory', 'neutral-technical'], default='warm-ivory')
    parser.add_argument('--material', action='append', required=True, help='Exact product-material name; repeat for multiple materials.')
    parser.add_argument('--floor-material', action='append', default=[])
    parser.add_argument('--world', action='store_true')
    parser.add_argument('--output', type=Path, required=True, help='New .blend output; the input scene is never overwritten.')
    options = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    destination = options.output.expanduser().resolve()
    if destination.suffix != '.blend':
        parser.error('--output must be a .blend file')
    if bpy.data.filepath and destination == Path(bpy.data.filepath).resolve():
        parser.error('Choose a new output path; the input scene cannot be overwritten')
    if destination.exists():
        parser.error('Output already exists; choose a new path')
    settings = json.loads((Path(__file__).resolve().parent / 'presets' / f'{options.preset}.json').read_text())
    # Validate the full selection before any material changes.
    for name in options.material + options.floor_material:
        material = bpy.data.materials.get(name)
        if material is None or not material.use_nodes or not any(n.type == 'BSDF_PRINCIPLED' for n in material.node_tree.nodes):
            parser.error(f'Missing node-based Principled material: {name}')
    for name in options.material:
        apply_material(name, settings['product'])
    for name in options.floor_material:
        apply_material(name, settings['floor'])
    scene = bpy.context.scene
    scene.view_settings.view_transform = settings['view_transform']
    if options.world:
        world = scene.world or bpy.data.worlds.new('Style world')
        scene.world = world
        world.use_nodes = True
        shader = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if shader is None:
            parser.error('The world has no Background shader')
        shader.inputs['Color'].default_value = settings['world']['color']
        shader.inputs['Strength'].default_value = settings['world']['strength']
    scene.render.filepath = '//generated/'
    bpy.context.preferences.filepaths.save_version = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    print(f'Saved styled scene: {destination.name}')


if __name__ == '__main__':
    main()
