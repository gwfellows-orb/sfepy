import gmsh
import sys
import numpy as np

gmsh.initialize()
gmsh.model.add("pve")
gmsh.merge("test_model.step")

gmsh.model.occ.synchronize()

# Get bounding box
xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(3, 1)


# Helper: get surfaces near a coordinate plane
def get_surfaces_by_com(axis: int, target: float, tol=1e-5):
    matching = []
    for dim, tag in gmsh.model.getEntities(2):
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        if abs(com[axis] - target) < tol:
            matching.append(tag)
    return matching


# Find surfaces on opposing faces
x0_surfs = get_surfaces_by_com(0, xmin)
x1_surfs = get_surfaces_by_com(0, xmax)
y0_surfs = get_surfaces_by_com(1, ymin)
y1_surfs = get_surfaces_by_com(1, ymax)
z0_surfs = get_surfaces_by_com(2, zmin)
z1_surfs = get_surfaces_by_com(2, zmax)

gmsh.model.occ.synchronize()


# Surface matching utility: match surfaces by bounding box centroid distance
def match_surface_pairs(surfs_a, surfs_b):
    def center(tag):
        return gmsh.model.occ.getCenterOfMass(2, tag)

    pairs = []
    used = set()
    for a in surfs_a:
        ca = np.array(center(a))
        best = None
        best_dist = 1e9
        for b in surfs_b:
            if b in used:
                continue
            cb = np.array(center(b))
            dist = np.linalg.norm(ca - cb)
            if dist < best_dist:
                best = b
                best_dist = dist
        if best is not None:
            pairs.append((a, best))
            used.add(best)
    return pairs


def set_periodic_pairs(pairs, translation):
    affine = [
        1,
        0,
        0,
        translation[0],
        0,
        1,
        0,
        translation[1],
        0,
        0,
        1,
        translation[2],
        0,
        0,
        0,
        1,
    ]
    for slave, master in pairs:
        gmsh.model.mesh.setPeriodic(2, [slave], [master], affine)


# Apply periodicity for each axis
set_periodic_pairs(match_surface_pairs(x1_surfs, x0_surfs), [xmax - xmin, 0, 0])
set_periodic_pairs(match_surface_pairs(y1_surfs, y0_surfs), [0, ymax - ymin, 0])
set_periodic_pairs(match_surface_pairs(z1_surfs, z0_surfs), [0, 0, zmax - zmin])

# Finalize mesh and export
gmsh.model.occ.synchronize()
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.model.mesh.generate(3)
gmsh.write("t18.msh")

if "-nopopup" not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
