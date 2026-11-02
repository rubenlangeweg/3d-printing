"""Check an external VoxelSim core against a two-resolution cantilever."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def run_case(VoxelFEA, node_coords, np, limit_threads, pitch):
    dims = (round(0.1 / pitch), round(0.01 / pitch), round(0.01 / pitch))
    nodes = node_coords(dims, np.zeros(3), pitch)
    fixed = np.flatnonzero(nodes[:, 0] < 1e-10)
    loaded = np.flatnonzero(nodes[:, 0] > 0.1 - 1e-10)
    dofs = (fixed[:, None] * 3 + np.arange(3)).ravel()
    force = np.zeros(len(nodes) * 3)
    force[loaded * 3 + 2] = -1 / len(loaded)
    modulus = 2e9
    stiffness = np.full(np.prod(dims), modulus * pitch)
    solver = VoxelFEA(*dims, nu=0.35, compute_mode='CPU', cpu_threads=4, use_multigrid=False)
    try:
        solver.set_fixed(dofs)
        with limit_threads(limits=4):
            displacement = solver.solve(stiffness, force, tol=1e-8, max_cg=6000)
            internal = solver._apply_K(displacement[solver.used_dofs], stiffness[solver.active_elems])
        residual = np.zeros_like(force)
        residual[solver.used_dofs] = internal
        residual -= force
        reactions = residual.reshape(-1, 3)[fixed]
        force_error = np.linalg.norm(reactions.sum(axis=0) + force.reshape(-1, 3).sum(axis=0))
        moment = np.cross(nodes[fixed], reactions).sum(axis=0)
        moment += np.cross(nodes, force.reshape(-1, 3)).sum(axis=0)
        true_residual = np.linalg.norm(residual[solver.used_dofs][solver.free]) / np.linalg.norm(force)
        energy = 0.5 * displacement[solver.used_dofs] @ internal
        work = 0.5 * force @ displacement
        inertia = 0.01 * 0.01**3 / 12
        bending = 0.1**3 / (3 * modulus * inertia)
        shear = 0.1 / ((5 / 6) * (modulus / (2 * 1.35)) * 0.01**2)
        tip = -displacement.reshape(-1, 3)[loaded, 2].mean()
        report = dict(pitch_mm=pitch * 1000, converged=bool(solver.last_converged),
                      mean_tip_mm=float(tip * 1000), beam_with_shear_mm=(bending + shear) * 1000,
                      relative_beam_error=float(tip / (bending + shear) - 1),
                      true_relative_residual=float(true_residual), force_balance_error_N=float(force_error),
                      moment_balance_error_Nm=float(np.linalg.norm(moment)),
                      energy_work_error_J=float(abs(energy - work)))
        if not solver.last_converged or true_residual > 3e-7:
            raise RuntimeError(f'Solver did not converge: {report}')
        if force_error > 1e-5 or np.linalg.norm(moment) > 1e-6 or abs(energy - work) > 1e-9:
            raise RuntimeError(f'Equilibrium or energy check failed: {report}')
        return report
    finally:
        solver.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.solver_root.expanduser().resolve()
    if not (root / 'core/fea.py').is_file():
        parser.error('--solver-root must contain core/fea.py')
    if args.output.exists():
        parser.error('Choose a fresh output report')
    sys.path.insert(0, str(root))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from core.fea import VoxelFEA
    from core.inside_worker import node_coords
    reports = [run_case(VoxelFEA, node_coords, np, threadpool_limits, pitch) for pitch in (0.002, 0.001)]
    if abs(reports[-1]['relative_beam_error']) > 0.08:
        raise RuntimeError(f'Fine grid differs by more than 8% from the beam reference: {reports}')
    if abs(reports[-1]['relative_beam_error']) >= abs(reports[0]['relative_beam_error']):
        raise RuntimeError(f'Refinement did not improve beam agreement: {reports}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    core_hash = hashlib.sha256((root / 'core/fea.py').read_bytes()).hexdigest()
    args.output.write_text(json.dumps({'passed': True, 'solver_core_sha256': core_hash, 'cases': reports}, indent=2))
    print(json.dumps({'passed': True, 'cases': reports}))


if __name__ == '__main__':
    main()
