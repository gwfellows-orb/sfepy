import gmsh
import sys


def stl_to_vtk(stl_filename, vtk_filename):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)  # Show messages

    # Add a new model
    gmsh.model.add("model_from_stl")

    # Import the STL file as a geometry
    gmsh.merge(stl_filename)

    # Get all entities, we expect surfaces from STL import
    surfaces = gmsh.model.getEntities(dim=2)
    if not surfaces:
        print("No surfaces found in STL.")
        gmsh.finalize()
        sys.exit(1)

    # Create a volume from the surface loop
    surface_loop = [s[1] for s in surfaces]

    # Create surface loop
    loop_tag = gmsh.model.geo.addSurfaceLoop(surface_loop)

    # Create volume from the surface loop
    vol_tag = gmsh.model.geo.addVolume([loop_tag])

    # Synchronize the CAD kernel with the Gmsh model
    gmsh.model.geo.synchronize()

    # Set mesh size parameters (optional)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.5)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 1.0)

    # Generate 3D mesh (tetrahedral)
    gmsh.model.mesh.generate(3)

    # Write the mesh to a VTK file
    gmsh.write(vtk_filename)

    print(f"Mesh written to {vtk_filename}")

    gmsh.finalize()


if __name__ == "__main__":
    stl_file = "RVE-test.stl"  # Your STL file path here
    vtk_file = "RVE-test-solid.vtk"  # Output VTK file path
    stl_to_vtk(stl_file, vtk_file)
