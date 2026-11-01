"""Render the saved holder animation to a fresh PNG sequence. MIT licensed."""
import argparse
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--frames", type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
destination = args.frames.resolve()
if destination.exists() and any(destination.iterdir()):
    raise SystemExit("Use an empty frame directory to avoid mixing sequences.")
destination.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.image_settings.media_type = "IMAGE"
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(destination) + "/"
scene.render.use_stamp = False
scene.render.use_stamp_filename = False
scene.render.use_stamp_date = False
bpy.ops.render.render(animation=True)
