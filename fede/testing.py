from parapy.geom import (ORIGIN, XOY, Vector, Plane, Box, Cylinder,
                         PartitionedSolid, ModifiedShape)

# basic input shapes
box = Box(2, 2, 2, centered=True)
cyl = Cylinder(0.5, 3, centered=True, position=XOY.rotate('z', 45, deg=True))

# partition box and cylinders into a shape with 4 solids (keep_tool!)
prt1 = PartitionedSolid(box, cyl, keep_tool=True)

# partition previous shape with another inner box into 7 solids
inner_box = Box(0.25, 0.25, 3, centered=True)
prt2 = PartitionedSolid(prt1, inner_box)

# let's split the previous shape with diagonal planes (use case: structure
# meshing), but keep the inner beam intact. For this purpose, temporarily
# remove the beam from the topology.
pln1 = Plane(ORIGIN, Vector(1, 1))
pln2 = Plane(ORIGIN, Vector(1, -1))
temp = ModifiedShape(prt2, remove=prt2.generated(inner_box))
prt3 = PartitionedSolid(temp, (pln1, pln2))

# replace original solids with their modified (split) counterparts
pairs = [(s, prt3.modified(s)) for s in temp.solids]
final = ModifiedShape(prt2, replace=pairs)

if __name__ == '__main__':
    from parapy.gui import display
    display(final)