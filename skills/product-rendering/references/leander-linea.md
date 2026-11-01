# Leander Linea reference

Use the actual Linea table in every product image and animation for this project. Both accessories remain mounted in their accepted positions. Use a folded muslin cloth and an unbranded baby-care tube if props help. Leave out phones and presentation labels such as “3D render”. Technical strength-study views are a separate output.

The accepted shelf is V4, with a 180 × 150 mm platform and 13 mm mounting opening. The original organizer measures 140 × 115 × 110 mm. Use the [published models](https://github.com/rubenlangeweg/3d-printing/tree/main/projects/leander-linea/models) or matching accepted local files. Do not change geometry to improve a render.

Read [linea-recipe.json](linea-recipe.json) when recreating the final appearance. It records lights, materials, cameras, motion formulas and production settings from Blender 5.0.1. It is a recipe, not a complete scene generator.

The saved scenes use numeric millimetres, with Metric Unit Scale `0.001`. One coordinate unit represents one millimetre. The original organizer scene uses metre-based vertices with a `1000` scale transform; its exported STL already uses millimetres. Check dimensions and avoid applying that conversion twice. The rig coordinates assume the saved assembly's origin. Retarget the rig if rebuilding at a different origin.

The recipe's high light powers belong to that numeric scale. Its mounted World strength is `0.4`, while the reusable warm-ivory preset uses `0.22`. Keep the mounted value when matching the existing scenes.

Select the camera explicitly. The organizer scene opens on its hero camera; animation needs `Organizer | mounted gentle move`. Shelf motion uses `Shelf on Linea motion`, and combined motion uses `Linea V4 | context to accessories`. Organizer stills use Cycles CPU with denoising; its animation uses EEVEE without ray tracing. Shelf and combination use EEVEE with ray tracing. Saved scene defaults do not include every production override; use the recipe's production profiles.

The full scenes contain the [table asset by Shopot on 3dsky](https://3dsky.org/3dmodels/show/pielienal_nyi_stolik_i_komod_ot_leander). Obtain that asset separately if existing local scenes are unavailable. Its meshes, textures and complete scenes are excluded from the public repository and this skill. Finished images and videos are handled under the [asset terms](https://3dsky.org/faq/115/show), with credit and exclusions recorded in the [project licensing notes](https://github.com/rubenlangeweg/3d-printing/blob/main/LICENSING.md).
