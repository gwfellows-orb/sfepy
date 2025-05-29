# ------------------------------------------------------------------------------
#
#  Gmsh Python tutorial 18
#
#  Periodic meshes
#
# ------------------------------------------------------------------------------
# right now this one makes a cube that can be infinetly tiled (periodic coresponce tween paralell sides)
# Periodic meshing constraints can be imposed on surfaces and curves.


import gmsh
import math
import os
import sys

gmsh.initialize()
gmsh.model.add("t18")

# x translation constraint


def translation_matrix(x, y, z):
    return [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z, 0, 0, 0, 1]


"""
gmsh.model.mesh.setPeriodic(dim, tags, tagsMaster, affineTransform)

Set the meshes of the entities of dimension `dim' and tag `tags' as
periodic copies of the meshes of entities `tagsMaster', using the affine
transformation specified in `affineTransformation' (16 entries of a 4x4
matrix, by row). If used after meshing, generate the periodic node
correspondence information assuming the meshes of entities `tags'
effectively match the meshes of entities `tagsMaster' (useful for
structured and extruded meshes). Currently only available for @code{dim} ==
1 and @code{dim} == 2.

Types:
- `dim': integer
- `tags': vector of integers
- `tagsMaster': vector of integers
- `affineTransform': vector of doubles
"""


# gmsh.model.mesh.setPeriodic(2, [2], [1], translation)

# The periodicity transform is provided as a 4x4 affine transformation matrix,
# given by row.

# During mesh generation, the mesh on surface 2 will be created by copying
# the mesh from surface 1.

# Multiple periodicities can be imposed in the same way:
# gmsh.model.mesh.setPeriodic(
#     2, [6], [5], [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1]
# )
# gmsh.model.mesh.setPeriodic(
#     2, [4], [3], [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]
# )

# For more complicated cases, finding the corresponding surfaces by hand can
# be tedious, especially when geometries are created through solid
# modelling. Let's construct a slightly more complicated geometry.

# We start with a cube and some spheres:
# gmsh.model.occ.addBox(2, 0, 0, 1, 1, 1, 10)
# x = 2 - 0.3
# y = 0
# z = 0
# gmsh.model.occ.addSphere(x, y, z, 0.35, 11)
# gmsh.model.occ.addSphere(x + 1, y, z, 0.35, 12)
# gmsh.model.occ.addSphere(x, y + 1, z, 0.35, 13)
# gmsh.model.occ.addSphere(x, y, z + 1, 0.35, 14)
# gmsh.model.occ.addSphere(x + 1, y + 1, z, 0.35, 15)
# gmsh.model.occ.addSphere(x, y + 1, z + 1, 0.35, 16)
# gmsh.model.occ.addSphere(x + 1, y, z + 1, 0.35, 17)
# gmsh.model.occ.addSphere(x + 1, y + 1, z + 1, 0.35, 18)

gmsh.model.occ.importShapes("test_model.step")

# We first fragment all the volumes, which will leave parts of spheres
# protruding outside the cube:
# out, _ = gmsh.model.occ.cut([(3, 10)], [(3, i) for i in range(11, 19)])
gmsh.model.occ.synchronize()

# Ask OpenCASCADE to compute more accurate bounding boxes of entities using
# the STL mesh:
gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

eps = 1e-2

# -------------- this is a test
# p = gmsh.model.getEntitiesInBoundingBox(
#     -0.5 - eps,
#     -0.5 - eps + 0.25,
#     0 - eps,
#     0.1 + 2 * eps,
#     1 + 2 * eps,
#     0.2 + 2 * eps,
#     0,
# )
# gmsh.model.mesh.setSize(p, 0.05)
# -------------

region_lbn = (-0.5, -0.5, 0)
region_rtf = (0.5, 0.5, 0.2)

# First we get all surfaces on the left:
sxmin = gmsh.model.getEntitiesInBoundingBox(
    -0.5 - eps, -0.5 - eps, 0 - eps, 1 + 2 * eps, 1 + 2 * eps, 0.2 + 2 * eps, 2
)
print("sxmin: ", sxmin)

# )
# gmsh.model.occ.addBox(
#     -0.5 - eps, -0.5 - eps, 0 - eps, 2 * eps, 1 + 2 * eps, 0.2 + 2 * eps, 2
# )

# gmsh.model.occ.synchronize()

# gmsh.model.mesh.generate(3)
# gmsh.write("t18.vtk")

# # Launch the GUI to see the results:
# if "-nopopup" not in sys.argv:
#     gmsh.fltk.run()

# gmsh.finalize()
# print("------------")

for i in sxmin:
    # Then we get the bounding box of each left surface
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(i[0], i[1])
    # We translate the bounding box to the right and look for surfaces inside
    # it:
    gmsh.model.occ.synchronize()
    sxmax = gmsh.model.getEntitiesInBoundingBox(
        xmin - eps + 1,
        ymin - eps,
        zmin - eps,
        xmax + eps + 1,
        ymax + eps,
        zmax + eps,
        2,
    )
    print("smxax = ", sxmax)

    # For all the matches, we compare the corresponding bounding boxes...
    for j in sxmax:
        xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = gmsh.model.getBoundingBox(j[0], j[1])
        xmin2 -= 1
        xmax2 -= 1
        # ...and if they match, we apply the periodicity constraint
        if (
            abs(xmin2 - xmin) < eps
            and abs(xmax2 - xmax) < eps
            and abs(ymin2 - ymin) < eps
            and abs(ymax2 - ymax) < eps
            and abs(zmin2 - zmin) < eps
            and abs(zmax2 - zmax) < eps
        ):
            gmsh.model.mesh.setPeriodic(2, [j[1]], [i[1]], translation_matrix(1, 0, 0))
            print("adding X periodic constraint...")
# ----------

for i in sxmin:
    # Then we get the bounding box of each ___ surface
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(i[0], i[1])
    # We translate the bounding box to the front and look for surfaces inside
    # it:
    gmsh.model.occ.synchronize()
    symax = gmsh.model.getEntitiesInBoundingBox(
        xmin - eps,
        ymin - eps + 1,
        zmin - eps,
        xmax + eps,
        ymax + eps + 1,
        zmax + eps,
        2,
    )
    print("syxax = ", symax)

    # For all the matches, we compare the corresponding bounding boxes...
    for j in symax:
        xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = gmsh.model.getBoundingBox(j[0], j[1])
        ymin2 -= 1
        ymax2 -= 1
        # ...and if they match, we apply the periodicity constraint
        if (
            abs(xmin2 - xmin) < eps
            and abs(xmax2 - xmax) < eps
            and abs(ymin2 - ymin) < eps
            and abs(ymax2 - ymax) < eps
            and abs(zmin2 - zmin) < eps
            and abs(zmax2 - zmax) < eps
        ):
            gmsh.model.mesh.setPeriodic(2, [j[1]], [i[1]], translation_matrix(0, 1, 0))
            print("adding Y periodic constraint...")
# -------

for i in sxmin:
    # Then we get the bounding box of each ___ surface
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(i[0], i[1])
    # We translate the bounding box to the top and look for surfaces inside
    # it:
    gmsh.model.occ.synchronize()
    symax = gmsh.model.getEntitiesInBoundingBox(
        xmin - eps,
        ymin - eps,
        zmin - eps + 0.2,  # CHANGE TO VAR...
        xmax + eps,
        ymax + eps,
        zmax + eps + 0.2,  # CHANGE TO VAR...
        2,
    )
    print("syxax = ", symax)

    # For all the matches, we compare the corresponding bounding boxes...
    for j in symax:
        xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = gmsh.model.getBoundingBox(j[0], j[1])
        zmin2 -= 0.2  # CHANGE TO VAR...
        zmax2 -= 0.2  # CHANGE TO VAR...
        # ...and if they match, we apply the periodicity constraint
        if (
            abs(xmin2 - xmin) < eps
            and abs(xmax2 - xmax) < eps
            and abs(ymin2 - ymin) < eps
            and abs(ymax2 - ymax) < eps
            and abs(zmin2 - zmin) < eps
            and abs(zmax2 - zmax) < eps
        ):
            gmsh.model.mesh.setPeriodic(
                2, [j[1]], [i[1]], translation_matrix(0, 0, 0.2)  # VARIBALE.........
            )
            print("adding Z periodic constraint...")
# -------
"""
gmsh.model.mesh.generate(dim=3)

Generate a mesh of the current model, up to dimension `dim' (0, 1, 2 or 3).

Types:
- `dim': integer
"""
# --------------

# # Synchronize to register entities
# gmsh.model.occ.synchronize()

# # Get all OCC entities (dim = 3 for volumes, dim = -1 for all)
# all_entities = gmsh.model.occ.getEntities(-1)  # use -1 for all dimensions

# # Copy everything
# copies = gmsh.model.occ.copy(all_entities)

# # Translate the copies
# gmsh.model.occ.translate(copies, dx=1, dy=0, dz=0)

# gmsh.model.occ.synchronize()


# -----------------
gmsh.model.mesh.generate(3)
gmsh.write("t18.vtk")

# Launch the GUI to see the results:
if "-nopopup" not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
