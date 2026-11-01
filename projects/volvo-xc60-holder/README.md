# Volvo XC60 phone holder

Vent mount for the 2022 Volvo XC60 T8, with a separate 17 mm ball module. This is the restored v10 design without cross ribs. It keeps the rounded outer corners and curved reinforcement at both arm roots.

![Assembled holder](renders/assembled.png)

## Print files

| File | Use |
| --- | --- |
| [Bambu Studio project](models/holder-without-ribs.3mf) | Both parts arranged on one plate, with the saved print profile |
| [Base STL](models/base-front-down.stl) | Base already oriented front down |
| [Ball module STL](models/ball-module.stl) | Separate ball module, oriented on its flat back |
| [Editable Blender model](source/holder-without-ribs.blend) | Both parts assembled, in millimetres |

The selected files are in `models/`. Their [SHA-256 hashes](models/SHA256SUMS) identify this revision. The ball module is unchanged from v07. Earlier ribbed variants are not included.

## Dimensions and printing

The base is approximately **56.57 × 50.38 × 28.00 mm**. The ball diameter is **17 mm**. Outer corner radii are **1.5 mm**; the curved inner roots have a **5 mm** radius. The root curves occupy 5 mm of clearance inside each arm. Small hook end-face corrections reach approximately 0.31 mm; the hook cross-section and overall envelope are retained.

The saved profile uses a Bambu X1 Carbon, PETG-CF, a 0.4 mm nozzle, 0.2 mm layers, six walls and 25% infill. Both parts were sliced without supports. The base has an approximately 12 mm bridge across its recessed slide. The recorded slicer estimate is **55 minutes and 25.7 g** for both parts. Check the preview and material settings for your printer.

## Rotation view

Both parts are shown in black, matching the intended print colour.

![Rotation around the black holder](animations/orbit.gif)

[Download the four-second rotation video](animations/orbit.mp4).

## Assembly

Slide the ball module down into the dovetail from the open top until it reaches the stop. Check the vent clearance and phone position before gluing the module in place. The design uses glue rather than a retaining screw; the animation shows the dry assembly motion.

![Ball module sliding into the base](animations/assembly.gif)

[Download the six-second assembly video](animations/assembly.mp4). Both parts use the same black finish.

![Exploded assembly](renders/exploded.png)

![Rear view showing the curved arm roots](renders/rear-roots.png)

## Checks and limits

The selected base export is one closed solid, with no non-manifold edges or zero-area triangles. The 3MF geometry matches the STL within 0.00000005 mm. Seven sampled positions along the module's insertion path show no solid intersection. Bambu Studio completed slicing without reported warnings. Reports are in [analysis](analysis/).

These are digital checks. Physical vent fit, glue retention, strength and resistance to heat have not been validated for this revision. Test the fit before final assembly.

## Edit and render

Open the clean Blender source to edit the model. The source contains only the base and ball module. Accepted STL and 3MF files remain separate from rendering work. The [rendering instructions](rendering/README.md) reproduce the images and animation in Blender 5.0.

Models and original media follow the repository's [CC BY-NC 4.0 terms](../../LICENSING.md); the rendering script is MIT. Volvo names and trademarks retain their respective rights. This is an independently designed compatible accessory, not an official Volvo product.
