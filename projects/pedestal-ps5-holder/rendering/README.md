# Render the holder

Use Blender 5.0.1 and the clean scene in `../source/pedestal-holder.blend`. The model uses metre coordinates; the exported STLs use millimetres.

The scene contains only the original holder mesh, a procedural ground plane, three area lights and an orthographic camera. The holder is placed upright on the floor with a rigid transform. Its geometry is unchanged. No external textures, linked libraries, frame or console meshes are included.

## Settings

- EEVEE, 32 render samples, 1920 × 1080.
- Frames 1–192 at 24 fps, eight seconds, no audio.
- AgX, Medium High Contrast, exposure 0.
- Matte black plastic, linear RGB (0.004, 0.004, 0.004), roughness 0.56, specular IOR level 0.28; warm mineral ground, roughness 0.8.
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

The separate local assembly scene uses the original frame, TV and console, with the original mounting transforms. Its camera moves around the rear of the stand. Finished context media are published with permission; the third-party source scene and reference meshes remain local. They are excluded from the repository's CC grant.

## Assembly steps

`animations/pedestal-installation.mp4` uses two slow camera orbits with a gentle push-in over 288 frames at 24 fps (12 seconds), with a cut at frame 145. It uses the same black material, EEVEE samples and Full HD output as the other videos, encoded as H.264 with a 32 Mbps target.

- Frames 1–144: the console is hidden. The holder starts 100 mm above and 75 mm in front of its original mounting position. It approaches the frame, lowers along the frame's tilt, then pauses at its original position.
- Frames 145–288: the holder remains seated. The console starts 240 mm above its original position, lowers along the same tilted axis, then pauses in its original position.

Both object and camera movements use smooth easing. The first camera sweeps 20 degrees around the holder; the second sweeps 24 degrees around the console and follows it downward. The camera keeps moving while the parts pause in their final positions. There are no labels, titles or overlays. The product geometry, rotations and final mounting positions remain unchanged.

Camera settings in metres, with azimuth measured around world Z:

| Shot | Orbit radius | Azimuth | Target XYZ, start → end | Camera height above target | Orthographic scale |
| --- | --- | --- | --- | --- | --- |
| Holder | 0.91 | −45° → −65° | (−0.158, 0.065, 0.48) → (−0.158, 0.065, 0.44) | 0.29 → 0.24 | 0.84 → 0.77 |
| Console | 1.75 | −72° → −48° | (−0.16, 0.025, 0.65) → (−0.16, 0.025, 0.53) | 0.38 → 0.32 | 1.55 → 1.36 |

The supplied mounted scene contains intersections between the holder and TV reference mesh, and between the console and holder. The animation preserves those meshes and their final positions. The motion illustrates the intended assembly direction; clearances, hook engagement and the actual installation sequence need physical verification.

The context scene stays local because it contains third-party reference meshes. Only the finished video and poster are distributed.
