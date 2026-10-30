"""Make RSDFT inputs that displace CO2 along its symmetry modes.

The reference structure is the optimized molecule along z (C-O 1.1645 A)
in a 10.6 A cubic cell. Each mode keeps the center of mass fixed:

* nu1 (symmetric stretch): O atoms move by +u and -u along z.
* nu3 (antisymmetric stretch): both O atoms move by +u along z, C by -r u.
* nu2 (bend): both O atoms move by +u along x, C by -r u.

Here r = 2 m_O / m_C and u is in bohr.

Usage: python make_harmonic_inputs.py <rsdft.in> <output_dir>
"""
import shutil
import sys
from pathlib import Path

A_BOHR = 10.6 / 0.529177210903  # cell length (bohr)
M_O, M_C = 15.999, 12.011
R = 2 * M_O / M_C
Z_O = 0.609861  # fractional z of O1 in the optimized structure (O2 at 1 - Z_O)

HEADER = """data_CO2
_symmetry_space_group_name_H-M   'P 1'
_cell_length_a   10.60000000
_cell_length_b   10.60000000
_cell_length_c   10.60000000
_cell_angle_alpha   90.00000000
_cell_angle_beta   90.00000000
_cell_angle_gamma   90.00000000
_symmetry_Int_Tables_number   1
loop_
 _symmetry_equiv_pos_site_id
 _symmetry_equiv_pos_as_xyz
  1  'x, y, z'
loop_
 _atom_site_type_symbol
 _atom_site_label
 _atom_site_symmetry_multiplicity
 _atom_site_fract_x
 _atom_site_fract_y
 _atom_site_fract_z
 _atom_site_occupancy
"""

# (mode, displacement u in bohr); nu2 and nu3 are symmetric in u, so only u > 0
POINTS = [("ref", 0.0)] + [("nu1", u) for u in (-0.06, -0.04, -0.02, 0.02, 0.04, 0.06)] \
    + [(m, u) for m in ("nu2", "nu3") for u in (0.02, 0.04, 0.06)]


def positions(mode, u):
    """Fractional coordinates of C, O1, O2."""
    pos = [[0.5, 0.5, 0.5], [0.5, 0.5, Z_O], [0.5, 0.5, 1 - Z_O]]
    f = u / A_BOHR
    if mode == "nu1":
        pos[1][2] += f
        pos[2][2] -= f
    elif mode in ("nu2", "nu3"):
        k = 0 if mode == "nu2" else 2
        pos[0][k] -= R * f
        pos[1][k] += f
        pos[2][k] += f
    return pos


def main():
    rsdft_in, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    for mode, u in POINTS:
        d = outdir / f"{mode}_{u:+.2f}"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(rsdft_in, d / "rsdft.in")
        lines = [f"  {el}  {lab}  1  {x:.10f}  {y:.10f}  {z:.10f}  1"
                 for (el, lab), (x, y, z) in zip((("C", "C1"), ("O", "O1"), ("O", "O2")), positions(mode, u))]
        (d / "rsdft.atom").write_text(HEADER + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
