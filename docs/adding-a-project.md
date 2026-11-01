# Add a project

Create `projects/<short-name>/` and keep the print file, source and media together.

1. Put the accepted STL or 3MF in `models/`. State units and version in the project README.
2. Put editable models and generators in `source/`. Write rebuilds to `generated/` so they do not replace accepted files.
3. Keep rendering notes and any redistributable scenes or scripts in `rendering/`, finished images in `renders/`, and MP4 files in `animations/`.
4. Add calculations to `analysis/` with material, load, support and mesh assumptions. Keep predicted results separate from physical tests.
5. Record model hashes, dimensions and the revision selected for printing.
6. Add a row to the root project table.

Use repository-relative paths. Keep sources self-contained and remove unused meshes, packed images and linked libraries before sharing a Blender file. Strip personal file paths and location metadata from exported media. Credit any third-party context and check its redistribution terms.

For mounted accessories, show the actual host product in every published product image and animation. Keep a full-product view as the project hero, then use closer views to show the fit and details. For the Linea project, this means the Leander table remains visible in every product view.

When a reference asset permits finished images but prohibits sharing its 3D source, keep the complete scene and textures outside the public repository. Publish the finished media, credit the creator and link to the original asset. Keep the independently authored accessory meshes and generators available separately.

Frame sequences, caches and generated rebuilds stay local. Keep final images and videos in Git while they remain small enough to manage. Use release assets or Git LFS if a project grows substantially; [GitHub's large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) explains the limits.

For a new visual style, add a small preset in `rendering/presets/` and keep a checked preview with the project. The existing warm ivory setup is a starting point.
