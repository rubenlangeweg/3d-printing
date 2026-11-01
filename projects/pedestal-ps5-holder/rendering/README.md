# Render the holder

Use Blender 5.0.1 and the clean scene in `../source/pedestal-holder.blend`. The model uses metre coordinates; the exported STLs use millimetres.

The scene contains only the original holder mesh, a procedural ground plane, three area lights and an orthographic camera. The holder is placed upright on the floor with a rigid transform. Its geometry is unchanged. No external textures, linked libraries, frame or console meshes are included.

## Settings

- EEVEE, 32 render samples, 1920 × 1080.
- Frames 1–192 at 24 fps, eight seconds, no audio.
- AgX, Medium High Contrast, exposure 0.
- Graphite plastic, roughness 0.4; warm mineral ground, roughness 0.8.
- Key, fill and rim area lights at 32.4 W, 13.5 W and 25.2 W, sized 0.75 m, 0.6 m and 0.54 m.
- Orthographic scale 0.45 m. A slow 86-degree camera arc with eased endpoints. The product stays fixed.

From the repository root:

```sh
blender -b projects/pedestal-ps5-holder/source/pedestal-holder.blend \
  --python projects/pedestal-ps5-holder/rendering/render.py -- \
  --frames projects/pedestal-ps5-holder/generated/holder/frames

swift rendering/encode_mp4.swift \
  projects/pedestal-ps5-holder/generated/holder/frames \
  projects/pedestal-ps5-holder/generated/holder.mp4 192 24 16
```

The render script requires an empty output directory to prevent mixing sequences. The encoder requires a fresh MP4 output path. It fully decodes the result and checks frame count and duration. Inspect the decoded start, midpoint and end frames as well as playback.

The separate local assembly scene uses the original frame, TV and console, with the original mounting transforms. Its camera moves around the rear of the stand. Third-party sources and context media stay outside this repository pending confirmation of their publication terms.
