# Make product renders and animations

Use the accepted print mesh, soft light and a slow camera move. The Linea images work because you can see the accessory on the actual table, with its mounting and proportions intact.

This workflow was used with Blender 5.0.1. The [exact Linea recipe](../projects/leander-linea/rendering/README.md#exact-scene-recipe) records the lights, materials, cameras and output settings. For the black holder, use the [Volvo rendering setup](../projects/volvo-xc60-holder/rendering/README.md).

For Codex, use the self-contained [product-rendering skill](../skills/product-rendering/SKILL.md). It includes the workflow, material presets, video exporter and Linea recipe. Installation and invocation are in the [repository README](../README.md#repository-layout).

## 1. Prepare a scene copy

Start from a complete scene when you have one. Save a working copy under `local/`, which is ignored by Git. Keep the accepted STL in `models/` unchanged.

For a new scene, import the accepted model and check its dimensions. The shelf platform is 180 × 150 mm; the organizer is 140 × 115 × 110 mm. Place it in its mounted position before setting cameras. Keep the same assembly and material setup across the whole image set.

For Linea product views, keep the actual table visible in every shot. Use a folded cloth and an unbranded baby-care tube for scale and context. Keep the mounting edge and the feature you want to explain visible. The full table scene and its textures stay local; the public repository contains the finished views and our accessory sources.

## 2. Set the material and colour management

The warm look uses matte ivory plastic, pale wood and a cream ground. The [warm ivory preset](../rendering/presets/warm-ivory.json) supplies the reusable material values. These are Blender linear RGB node values, not sRGB hexadecimal colours.

| Setting | Linea value |
| --- | --- |
| Product Base Color | `(0.78, 0.735, 0.645, 1)` |
| Product Roughness | `0.52` |
| Product Specular IOR Level / IOR | `0.28` / `1.5` |
| Floor Base Color / Roughness | `(0.72, 0.665, 0.575, 1)` / `0.82` |
| View Transform / Look | AgX / Medium High Contrast |
| Exposure / Gamma | `+0.2` / `1.0` |
| World colour / strength | `(0.90, 0.855, 0.76, 1)` / `0.4` |

The palette preset's world strength is `0.22`; the final mounted Linea scenes use `0.4`. Set `0.4` when rebuilding those scenes. The style helper changes selected materials and AgX; lights, the contrast look, exposure and camera setup are separate settings.

To restyle a copy from the repository root:

```sh
blender -b local/linea.blend --python rendering/apply_style.py -- --preset warm-ivory --material 'Warm ivory matte accessories' --output local/linea-styled.blend
```

Use the exact material name from your scene. Repeat `--material` for several materials. `black`, `graphite` and `neutral-technical` are also available. The helper saves a new file and preserves geometry and camera motion. Leave `--world` out to keep the mounted scene's world lighting.

## 3. Build soft lighting

Use three large area lights: a warm main light above and to one side, a weaker fill on the other side, and a light behind the object to separate its edge from the background. Aim them at the product area. Large sources create broad highlights that reveal curved ribs and rounded corners.

The Linea rig uses disk lights, shadows on and shadow jitter off. Its exact positions, sizes and powers are in the [scene recipe](../projects/leander-linea/rendering/scene-recipe.json). Those large power values belong to its numeric millimetre coordinates. Keep geometry, light distances, light sizes and camera scale in the same coordinate system.

Render one frame while adjusting the balance. Keep a visible contact shadow where the accessory meets the wood. If the image looks flat, reduce the fill or world brightness slightly before changing the product colour. If the edges look harsh, increase the light size and check the shadow in another preview.

## 4. Choose three useful views

| View | What it should show |
| --- | --- |
| Full context | The complete table with both accessories mounted |
| Product hero | The accessory occupies roughly half the image width, with the table still visible |
| Detail | The mounting lip, rounded edge or curved ribs at a readable angle |

The Linea cameras are orthographic, with depth of field off. Set **Orthographic Scale** to change framing; moving an orthographic camera closer does not enlarge the product. Keep enough space for props and the moving camera's final view.

Aim the camera at a point near the feature being shown. From Python, the original scenes use:

```python
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
```

`target` is a `mathutils.Vector`. For manual setup, use a Track To constraint aimed at an Empty, with Track Axis `-Z` and Up Axis `Y`.

## 5. Make a short camera move

Use 24 fps. Six seconds is frames 1–144; eight seconds is frames 1–192. Keep the assembly fixed and animate the camera position, aim and orthographic scale.

The combined Linea clip holds the full-table view for the first 18% of its duration, then moves closer to both accessories. The shelf clip lowers toward the ribs. The organizer clip makes a smaller move toward the container. Their exact paths are recorded in `motion_formula` in the [recipe](../projects/leander-linea/rendering/scene-recipe.json).

For a new move, set start and end positions and use a gentle ease-in/ease-out. The original paths calculate each rendered frame with `e = t*t*(3-2*t)`, where `t` runs from 0 to 1. Position, aim target and scale interpolate using `e`, and the camera is aimed again before each key is inserted. This keeps the feature centred through the move.

Check the first, middle and last frames before rendering the sequence. Check a low-angle frame too if the camera passes beneath the shelf.

## 6. Render previews, stills and frames

In Blender, choose the active camera, then set **Output Properties** to the required resolution and frame range. Turn off render stamps. Use **Render Image** for a still and **Render Animation** for the numbered sequence.

Our Linea full-table and shelf stills used EEVEE at 128 samples with ray tracing on. Their clips used 64 samples. The organizer used different final settings, listed in the project recipe. Start with 32 samples and a smaller preview; use the checked production profile for the final output.

| Output | Size | Format |
| --- | --- | --- |
| Main stills | 2000 × 1500 | PNG, RGB |
| Combined close-up | 1600 × 1200 | PNG, RGB |
| Video frames | 1280 × 960, 24 fps | PNG or JPEG quality 96 |

Render to numbered frames so encoding can be repeated without rendering again. Keep previews in a separate folder from the complete sequence. Select the motion camera, set the production settings and save the scene before these commands:

```sh
# First, middle and last previews for a six-second clip.
blender -b local/product-motion.blend -o //generated/previews/#### -F PNG -f 1,73,144

# Complete six-second sequence: 0001.png through 0144.png.
blender -b local/product-motion.blend -o //generated/frames/#### -F PNG -s 1 -e 144 -a
```

`//` means relative to the Blender file. Here the frames go into `local/generated/frames/`. Place `-f` or `-a` last because Blender processes arguments in order. See [Blender's command-line rendering reference](https://docs.blender.org/manual/en/5.0/advanced/command_line/render.html).

On macOS, if `blender` is not on your PATH, replace it with `"/Applications/Blender.app/Contents/MacOS/Blender"`.

## 7. Encode the video

On macOS, the repository's Swift encoder uses AVFoundation. It writes H.264 MP4 without audio and then decodes every frame to check the result. Run it after all frames have finished:

```sh
# Frame directory, output, frame count, fps, target bitrate in Mbps.
swift rendering/encode_mp4.swift local/generated/frames local/product-clip.mp4 144 24 8

# More bitrate for fine wood texture, as used for the organizer.
swift rendering/encode_mp4.swift local/generated/frames local/product-clip-detail.mp4 144 24 20
```

The final bitrate argument is optional and defaults to 8. The shelf and combined clips used 8 Mbps; the organizer used 20 Mbps. Use 192 frames for the eight-second combined clip. Choose a fresh output filename; the encoder preserves existing files.

The encoder also writes first/middle/last decoded previews and a JSON verification report in `encoded-checks/` beside the frame directory. Check the decoded video, since compression can soften wood grain even when the source PNG looks good. Users on other systems can encode the same frame sequence with their own H.264 video tool.

## 8. Finish the set

Watch the full clip once. Check that the product and props remain in frame, the mounting looks plausible, and the final view explains a useful detail. Keep colours and lighting consistent between the poster, stills and video.

Publish the final PNGs and MP4s in the project's `renders/` and `animations/` folders. Remove personal file paths and location metadata from exported copies. Keep frame sequences, scene backups and restricted reference assets local. Link the finished media from the project README and retain the original asset credit.
