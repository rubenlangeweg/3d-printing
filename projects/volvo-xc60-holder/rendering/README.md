# Holder renders

The renderer loads the accepted Blender source, converts millimetres to metres for lighting, and assigns the same black satin material to both parts. It does not change the printed geometry. The model's Y axis points up; the module moves 42 mm down that axis into its seated position.

Run from the repository root with Blender 5.0:

```sh
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- preview
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- stills
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- animation
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- orbit
```

`preview` writes a smaller assembled image. `stills` writes the three finished images. `animation` writes `assembly.blend` and 144 PNG frames under `../generated/frames/`, at 800 × 800 and 24 fps. The six-second clip pauses before insertion and after seating. `orbit` writes `orbit.blend` and 96 frames under `../generated/orbit-frames/`. It moves the camera through a full circle in four seconds, with a fixed assembled model. Render commands replace their own previous outputs.

The saved `assembly.blend` is self-contained. Render it directly to keep manual changes to lighting or materials:

```sh
blender -b projects/volvo-xc60-holder/rendering/assembly.blend -a
```

Encode with the repository's macOS tool:

```sh
swift rendering/encode_mp4.swift \
  projects/volvo-xc60-holder/generated/frames \
  projects/volvo-xc60-holder/animations/assembly.mp4 144 24
```

The encoder preserves existing video files. Choose another output path when rebuilding an existing video. It verifies duration, frame count and successful decoding.

Create the GIF with `python3 projects/volvo-xc60-holder/rendering/encode_gif.py` after installing Pillow. The GIF is a smaller 12 fps preview of the same rendered frames. The MP4 is the full-resolution version. Keep frame sequences local; commit the finished media and scene.

These are assembly views of the holder itself. No vehicle vent geometry is included, so the media does not demonstrate vehicle fit. The black material is also available as the repository's shared `black` preset.

For the rotation video, use `generated/orbit-frames`, `animations/orbit.mp4` and a frame count of `96` with the same encoder. Create its GIF with `python3 projects/volvo-xc60-holder/rendering/encode_gif.py orbit`.
