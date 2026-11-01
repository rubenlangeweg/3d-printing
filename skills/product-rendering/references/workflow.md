# Create the image set

Use a working copy of the scene. Check model dimensions before styling, especially when importing an STL without unit metadata. Leave the accepted print file unchanged.

## Materials and soft light

The bundled palettes contain linear Blender node colours, not sRGB hex values. Choose `warm-ivory`, `black`, `graphite` or `neutral-technical` to match the product. Use Principled BSDF and inspect texture links: a connected input can override the default value written by the helper.

For the warm treatment, use matte ivory plastic, a cream ground and slightly warm light. AgX, Medium High Contrast and exposure `+0.2` are a starting point from the Linea work. Adjust against a preview. The helper sets AgX but does not set contrast, exposure, metallic or IOR.

Use large area lights: a main light above and to one side, a weaker fill opposite, and an edge light behind. Aim them at the product. Keep a visible contact shadow. Reduce fill or world strength if the shape looks flat; enlarge the light if highlights or shadows feel harsh.

Keep light distances, sizes and powers appropriate to the scene scale. The Linea recipe's large powers belong to numeric millimetre coordinates and must not be copied directly into a metre-sized scene.

Set the actual skill location once. These commands assume the default local installation; for a repository copy, use that skill folder's absolute path:

```sh
RENDER_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/product-rendering"

blender -b local/product.blend --python "$RENDER_SKILL/scripts/apply_style.py" -- \
  --preset warm-ivory --material 'Product material' --output local/product-styled.blend
```

Replace the material name with its exact scene name. Repeat `--material` to select several materials. Use `--floor-material` for a named floor material. Add `--world` only when changing the world is intended. The warm preset's world strength is `0.22`; the mounted Linea scenes use `0.4`.

The output must be a new lowercase `.blend` filename. The helper resets render output to `//generated/` beside the new scene. It does not create lights or cameras.

## Camera and motion

Choose views that explain the product: context, hero and a useful detail. An orthographic camera with depth of field off worked for the Linea accessories. Orthographic Scale changes framing; moving the camera closer does not enlarge the object. Use perspective when it suits the requested result.

For an accessory animation, keep the mounted assembly fixed and move the camera. A standalone product can use a turntable if requested. Keep motion slow enough to read the shape. The reference clips use 24 fps, with 144 frames for six seconds or 192 for eight seconds.

For an eased camera move, interpolate position, aim target and orthographic scale with `e = t*t*(3-2*t)`, where `t = (frame - first)/(last - first)`. Aim at the interpolated target before inserting each frame's keys:

```python
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
```

`target` is a `mathutils.Vector`. For an orbit, use radians in `cos()` and `sin()`. Preview the complete path at low resolution to check framing, clipping and unexpected motion. Avoid changing the assembly to hide a bad angle.

## Render to a sequence

Select the active still or motion camera explicitly. Set engine, samples, resolution, frame range and fps, then save the working scene. Disable render stamps unless requested. Check dependencies and packed textures before moving a scene to another machine.

As a starting point, use 2000 × 1500 PNG stills and 1280 × 960 animation frames at 24 fps. Use a low-sample preview first. The exact Linea profiles vary between EEVEE and Cycles; read its recipe to reproduce those outputs.

On macOS, use `"/Applications/Blender.app/Contents/MacOS/Blender"` if `blender` is not on PATH. Run these after choosing and saving the motion camera and render settings:

```sh
blender -b local/product-motion.blend -o //generated/previews/#### -F PNG -f 1,73,144
blender -b local/product-motion.blend -o //generated/frames/#### -F PNG -s 1 -e 144 -a
```

Blender processes arguments in order, so keep `-f` or `-a` last. `//` is relative to the `.blend`, not the shell directory. Here frames land in `local/generated/frames/`. Use a separate job directory for each clip.

## Encode and verify

Wait for all frames to finish. Check sequential, zero-padded names such as `0001.png` through `0144.png`, identical dimensions, and no missing or duplicate frame numbers. The encoder sorts filenames lexically; frame count alone cannot catch numbering gaps. The frame directory must contain only the intended sequence. Width and height must be even.

On macOS with Swift and AVFoundation:

```sh
# Frame folder, fresh MP4 path, expected frames, fps, target Mbps.
swift "$RENDER_SKILL/scripts/encode_mp4.swift" local/generated/frames local/product-clip.mp4 144 24 8
```

The optional bitrate is a whole number, default `8`. The organizer clip used `20` to retain wood texture. Pass frame count explicitly; the encoder defaults to 192. It creates H.264 with no audio and refuses existing outputs. If encoding fails, inspect the error and use a fresh output path for a corrected retry because a partial file may remain.

The encoder fully decodes the video and checks count and duration. It saves first, middle and last decoded previews and a JSON report to `encoded-checks/` beside the frame folder. Separate job directories keep these reports from overwriting one another. Reports contain local paths, so keep them local or sanitize exported copies.

Inspect decoded previews and watch the full clip. Check texture quality, lighting consistency, mounting contact, clipping and start/end framing. Metadata checks do not prove visual quality. Keep final media separate from temporary frames and scene backups, and remove personal paths or location metadata from public copies.
