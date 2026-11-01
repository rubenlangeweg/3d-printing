# Render the accessories on the Linea

Follow the [product rendering guide](../../../docs/product-renders-and-animations.md) for the workflow. The settings below reproduce the lighting and camera approach used for this project.

All product images and animations show the accessories mounted on the Leander Linea table. The full-table hero gives the context; closer shelf and organizer views show their position and mounting details.

The [local gallery](../index.html) brings the three clips together. The sequences use 24 fps and no audio.

All three clips were fully decoded and their first, middle and last frames visually checked. [Media checks](media-checks.json) records the output hashes, frame counts and dimensions. The accepted print meshes are unchanged.

| Clip | Frames | Duration |
| --- | ---: | ---: |
| [Shelf on the Linea](../animations/shelf-v4.mp4) | 144 | 6 seconds |
| [Organizer on the Linea](../animations/organizer.mp4) | 144 | 6 seconds |
| [Both accessories on the Linea](../animations/combination.mp4) | 192 | 8 seconds |

## Scene files

Complete Blender scenes are saved locally. They contain the [Linea table asset by Shopot on 3dsky](https://3dsky.org/3dmodels/show/pielienal_nyi_stolik_i_komod_ot_leander), whose redistribution terms prevent including its 3D geometry and textures here. The repository contains the finished images and videos, our editable accessory meshes, model generators and shared styling tools.

To assemble a matching scene, obtain the table asset separately under its licence and combine it locally with the [accepted accessory models](../models/). Keep the full scene outside the public repository. Use the actual table for both the full view and detail shots.

## Style and output

Use Blender 5.0 and the [shared warm ivory preset](../../../rendering/README.md) as a starting point. Apply material changes to the accessories while keeping their mounting position and geometry unchanged. The table lighting and materials remain part of the local scene.

Render a still first to check the visible table, mounting position, framing and shadows. Then render the camera sequence and encode it as H.264 at 24 fps. Keep numbered frame sequences and scene copies local; share only the finished media and source files that may be redistributed.

## Exact scene recipe

[scene-recipe.json](scene-recipe.json) records the settings extracted from the final local scenes and render scripts in Blender 5.0.1. It contains material values, lights, camera positions, motion formulas and output profiles. It contains no furniture geometry or textures.

The saved scenes use numeric millimetres: one coordinate unit represents one millimetre, with Metric units and Unit Scale `0.001`. The table, lamps and cameras share that coordinate system. The original organizer scene has metre-based vertices and a `1000` scale transform; exported STLs already use millimetres. Check dimensions before importing or scaling anything.

The following positions apply to the saved assembly's origin. If you rebuild the scene with a different origin, move the light/camera rig with the assembly or retarget it in a preview.

### Materials and colour

Use Principled BSDF for the ivory accessories: Base Color `(0.78, 0.735, 0.645, 1)`, Roughness `0.52`, Specular IOR Level `0.28`, IOR `1.5`, Metallic `0`. The cream floor uses `(0.72, 0.665, 0.575, 1)` and Roughness `0.82`. These are linear node values.

Set World Background to `(0.90, 0.855, 0.76, 1)` at strength `0.4`. Use AgX, Medium High Contrast, exposure `+0.2`, gamma `1`, and sRGB display. The general warm-ivory palette uses a lower world strength of `0.22`; preserve or set `0.4` for this mounted scene.

### Lights

All three are disk area lights, with shadows on and shadow jitter off. Coordinates and diameters below use the numeric millimetre setup.

| Light | Position XYZ | Aim target XYZ | Diameter | Blender power | RGB |
| --- | --- | --- | ---: | ---: | --- |
| Main window | `(-1000, -1300, 2000)` | `(0, 0, 550)` | 1500 | 28,000,000 | `(1, .95, .85)` |
| Fill | `(1300, -500, 1500)` | `(100, -50, 750)` | 1300 | 15,000,000 | `(1, .985, .94)` |
| Edge | `(0, 1300, 1900)` | `(0, 0, 650)` | 1100 | 16,000,000 | `(1, .93, .80)` |

Keep these powers with this coordinate scale. A metre-sized reconstruction needs a consistently rescaled rig and adjusted powers; changing the unit display alone does not perform that conversion.

### Cameras and movement

All cameras are orthographic, with depth of field off. Camera names in the local scene copies are:

| Local scene | Still camera | Animation camera |
| --- | --- | --- |
| `linea-v4-shelf-and-organizer.blend` | `Linea V4 \| full table` or `Linea V4 \| combined detail` | `Linea V4 \| context to accessories` |
| `shelf-mounted-media.blend` | `Shelf mounted hero` or `Shelf curved ribs with Linea context` | `Shelf on Linea motion` |
| `organizer-on-linea-warm.blend` | `Organizer \| warm mounted hero` | `Organizer \| mounted gentle move` |

The organizer scene opens on its hero camera. Select its motion camera before rendering an animation.

| Move | Orthographic Scale | Path |
| --- | --- | --- |
| Combined, 192 frames | 1750 to 790 | Hold the opening full-table view for 18%, then move closer with a 20° azimuth change |
| Shelf, 144 frames | 620 to 480 | Sweep 70° and lower the camera to reveal the ribs |
| Organizer, 144 frames | 820 to 600 | Move closer with an 18° azimuth change |

The recipe's `motion_formula` section gives the exact target, radius, height and scale for every frame. It uses `e = t*t*(3-2*t)` for smooth acceleration and deceleration. Each frame gets location, rotation and orthographic-scale keys; the saved curves use Bézier interpolation with Auto Clamped handles. The product geometry and mounting transforms remain fixed.

### Production settings

| Output | Engine and quality | Resolution | Frames / format |
| --- | --- | --- | --- |
| Full table and shelf stills | EEVEE, 128 samples, ray tracing on | 2000 × 1500 | PNG |
| Combined close still | EEVEE, 128 samples, ray tracing on | 1600 × 1200 | PNG |
| Combined clip | EEVEE, 64 samples, ray tracing on | 1280 × 960 | 1–192, JPEG quality 96 |
| Shelf clip | EEVEE, 64 samples, ray tracing on | 1280 × 960 | 1–144, JPEG quality 96 |
| Organizer stills | Cycles CPU, 32 samples, denoising on | 2000 × 1500 | PNG |
| Organizer clip | EEVEE, 32 samples, ray tracing off | 1280 × 960 | 1–144, PNG compression 15 |

All clips use 24 fps, RGB, an opaque background and disabled render stamps. The renders used four CPU threads. The H.264 target was 8 Mbps for shelf/combined and 20 Mbps for organizer. Saved scene defaults do not include every still-render override in this table.

### Render a saved combined scene

Copy your complete local scene to the repository's ignored `local/linea.blend`. These commands keep the source file unchanged. Run them from the repository root:

```sh
# Full-table still, using its named camera and final still settings.
blender -b local/linea.blend --python-expr "import bpy; s=bpy.context.scene; s.camera=bpy.data.objects['Linea V4 | full table']; s.render.resolution_x=2000; s.render.resolution_y=1500; s.eevee.taa_render_samples=128" -o //generated/stills/linea-hero-#### -F PNG -f 1

# Eight-second move, explicitly selecting the motion camera.
blender -b local/linea.blend --python-expr "import bpy; s=bpy.context.scene; s.camera=bpy.data.objects['Linea V4 | context to accessories']" -o //generated/combination/#### -F PNG -s 1 -e 192 -a

# Encode after all 192 frames exist.
swift rendering/encode_mp4.swift local/generated/combination local/linea-combination.mp4 192 24 8
```

The animation command uses lossless PNG frames rather than the original JPEG 96 intermediate files. It keeps the scene, camera, resolution and render settings; the encoded file will not have the original binary checksum. Compare its decoded frames and appearance.
