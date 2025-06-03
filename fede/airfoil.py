
import os
from parapy.core import Base, Attribute, Input, Part
from parapy.geom import LoftedSolid, Rectangle, Vector, translate, GeomBase, FittedCurve, LoftedSurface
import pandas as pd
import matplotlib.pyplot as plt
from kbeutils.data import airfoils

class Airfoil(FittedCurve):
    chord: float = Input(350.)
    airfoil_name:str = Input("NACA2411") #in theory this automatically does it
    thickness_factor: float = Input(1.)
    mesh_deflection: float = Input(1e-4)
    cst_poly_order: int = Input(4)
    airfoil_dir = Input(airfoils.__path__[0])
    @Attribute
    def points(self):
        point_lst = [self.position.translate("x", x * self.chord,   # the x points are scaled according to the airfoil chord length
                                             "z", z * self.chord).location  # the z points are scaled according to the chord
                     for x, z in zip(self.coords_list[0], self.coords_list[1])]
        return point_lst
    @Attribute
    def coords_list(self):
            """List of points defining the airfoil shape, read from a file in the airfoils folder of kbeutils.
            If you want to check out all the possible airfoils, left click + Ctrl on the airfoils folder at import. """
            with open(os.path.join(self.airfoil_dir, self.airfoil_name + ".dat"), 'r') as f:
                point_x_lst = []
                point_z_lst = []
                skip = 0
                for line in f:
                    try:
                        x, z = line.split(maxsplit=1)
                        point_x_lst.append(float(x))
                        point_z_lst.append(float(z) * self.thickness_factor)
                    except ValueError:
                        if not skip:  # Skip the first line if it is a header
                            skip = 1
                            continue
                        else:  # Next time a line is not readable, stop reading (it is usually a comment or source link)
                            break
            return [point_x_lst, point_z_lst]


if __name__ == "__main__":
    fus = Airfoil()

    from parapy.gui import display

    display(fus)

