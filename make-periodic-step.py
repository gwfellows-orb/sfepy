import gmsh
import sys
import numpy as np

gmsh.initialize()
gmsh.model.add("pve")

# STEP file path
gmsh.merge("test_model.step")

# Classify geometry and synchronize
gmsh.model.geo.synchronize()
gmsh.model.mesh.classifySurfaces(angle=40 * np.pi / 180)
gmsh.model.mesh.createGeometry()
gmsh.model.geo.synchronize()


# Find planar surfaces at min/max x/y/z
def get_surfaces_by_com(axis: int, target: float, tol=1e-5):
    """Find surfaces with center of mass on target plane (axis 0=x,1=y,2=z)"""
    matching = []
    for dim, tag in gmsh.model.getEntities(2):
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        if abs(com[axis] - target) < tol:
            matching.append(tag)
    return matching


# Get bounding box
xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(3, 1)

# Get opposite surfaces
x0_surfs = get_surfaces_by_com(0, xmin)
x1_surfs = get_surfaces_by_com(0, xmax)

y0_surfs = get_surfaces_by_com(1, ymin)
y1_surfs = get_surfaces_by_com(1, ymax)

z0_surfs = get_surfaces_by_com(2, zmin)
z1_surfs = get_surfaces_by_com(2, zmax)


# Define periodic boundary pairs with identity mapping (assumes matching geometry)
def set_periodic(slave_tags, master_tags, translation_vector):
    affine = [
        1,
        0,
        0,
        translation_vector[0],
        0,
        1,
        0,
        translation_vector[1],
        0,
        0,
        1,
        translation_vector[2],
    ]
    gmsh.model.mesh.setPeriodic(2, slave_tags, master_tags, affine)


set_periodic(x1_surfs, x0_surfs, [xmax - xmin, 0, 0])
set_periodic(y1_surfs, y0_surfs, [0, ymax - ymin, 0])
set_periodic(z1_surfs, z0_surfs, [0, 0, zmax - zmin])

# Optionally tag volume as physical
vols = gmsh.model.getEntities(3)
if vols:
    gmsh.model.addPhysicalGroup(3, [v[1] for v in vols], tag=1)

# Set msh version for SfePy compatibility
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

# Generate mesh and write
gmsh.model.mesh.generate(3)
gmsh.write("t18.msh")

# Launch GUI unless -nopopup
if "-nopopup" not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
