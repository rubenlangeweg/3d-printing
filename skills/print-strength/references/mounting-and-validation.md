# Mounting and numerical checks

## Load path and contact

Follow the force from the load patch through the plate, ribs and clip, into the rail and the rest of the furniture. A rigid rail approximation ends at the rail. It does not calculate furniture joint forces, tipping or floor reactions unless those bodies and connections are included.

For separating rail contact, use exposed faces oriented toward the rail. Check candidate nodes, normals and physical contact spans in a setup view. Define the normal/gap convention explicitly. Contact should carry compression and permit separation, with no tensile adhesion. A zero-clearance fit is an assumption to record. Do not interpret staircase offsets from voxelization as measured clearance.

The historical shelf extension used a small-displacement penalty active-set solve around the external VoxelSim stiffness operator. It was project-specific code, not a feature of the stock add-on's support selector. Reimplement or adapt it only after validating the current geometry and API. The original source is not bundled as a general contact solver.

Add only the gauge constraints needed to remove free rigid motion, and check their reactions are negligible. A substantial artificial support reaction means the fixture is carrying a real load and must be explained. Check contact penetration against relevant dimensions, active-set convergence, compression-only forces, force balance and moment balance. Vary mesh pitch and contact penalty to expose numerical dependence.

Include self-weight as body forces. For a solid voxel of side h metres and density rho kg/m³, its mass is rho*h³ kg. In the earlier studies its gravity force was distributed over its eight nodes. A full-density volume overestimates the mass of a sparse-infill print. Record the chosen density model and compare with measured print mass where available.

For total displacement use the loaded solution including gravity. For additional displacement solve the gravity-only state, then subtract displacement vectors node by node. Do not subtract two maximum magnitudes. A changed contact active set requires a new solve. Linear scaling and superposition apply only while stiffness and boundary conditions remain fixed.

## Headless VoxelSim integration

These details refer to the pinned 2.5.6 core, not a stable cross-version API.

- Internal coordinates and voxel pitch h use metres, force uses N and physical E uses Pa.
- `VoxelFEA` uses a unit-cube element kernel. Supply `E*h` for stiffness. Recover stress with physical E, then divide by h. Displacement is in metres. Convert final displacement to mm and stress to MPa.
- Use the solver's `edof_full`, `used_dofs`, `remap` and node helper functions. Active element masks follow `np.meshgrid(..., indexing='ij')` with C flattening, Z fastest. Global node IDs use X fastest. Matching an array's length does not prove matching order.
- Never restore an old active mask with a new origin, pitch, transformed mesh or load selection. Hash the source and store the complete grid and fixture identity beside the cache.
- The local backend previously used NumPy and threadpoolctl. Mesh import/voxelization also used Blender BVH or trimesh and rtree. Inspect imports for the chosen path and use the relevant Python environment. Bundled Blender Python and the system Python can have different packages.

Before a custom solve, run the included benchmark with a Python environment that can import NumPy and the external core dependencies.

```sh
python "$STRENGTH_SKILL/scripts/check_solver.py" \
  --solver-root /path/to/VoxelSim-FEA --output work/cantilever-check.json
```

`--solver-root` is the folder containing `core/fea.py`. The benchmark uses two voxel sizes and a known rectangular cantilever. It checks equilibrium, residual, energy and agreement with a beam calculation including shear. This is a backend check, followed by separate checks for the actual part, fixture and voxelization.

## Accept a study

Record the following evidence with every result.

1. Expected dimensions and orientation, source hash, positive volume, watertightness and represented thin features.
2. Active and removed voxel counts, voxel volume error, grid pitch and origin, selector counts, force sum and load centroid.
3. Convergence flag and a recomputed free-DOF residual using the actual stiffness/contact operator. A progress indicator alone is insufficient.
4. Applied force plus support reactions, and their moments about one stated origin. Use tolerances relative to the load and moment scale, with absolute floors for small values.
5. Consistency of 0.5*uᵀKu and 0.5*fᵀu for the linear fixed system. For contact, include its penalty potential and use the appropriate nonlinear equilibrium checks.
6. Mesh refinement and, for contact, penalty sensitivity. Compare like-for-like loads, material, mount and lattice when ranking variants. Document what has and has not converged.

Stress at a perfectly fixed edge or concentrated load can remain singular as the grid is refined. Report the peak and its location, then assess an away-from-fixture region or percentile with a stated definition. Do not silently clip peaks to make a design appear stronger.

Printed plastics require additional evidence for layer-direction strength, actual infill and shells, long-term creep, temperature, impact and failure. A homogeneous elastic screen answers relative stiffness and load-path questions under its assumptions. Assign a capacity only with suitable material, failure and physical validation evidence.
