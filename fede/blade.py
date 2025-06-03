from math import radians, tan
from kbeutils.geom import cst_airfoil_coordinates
from parapy.geom import *
from parapy.core import *
from fede import Airfoil, Frame
"""propeller class. important, we need to select the airfoil at the root and tip, so we can use the
directory from the airfoil. in this case, we define a part that is the airfoil, and it gets chosen directly
from the airfoil path

the new part is finding the """


class Blade(LoftedSolid):  # note use of loftedSolid as superclass
    identifying_number = Input(0) #Identifying number, it is used for the numbering of the blades
    propeller_radius :float= Input(10)
    propeller_foil_root_name: str = Input("NACA2411")
    propeller_foil_tip_name: str = Input("NACA2411")
    propeller_c_root: float = Input(5)
    propeller_c_tip: float = Input(2)
    propeller_t_factor_root: float = Input(1.)
    propeller_t_factor_tip: float = Input(1.)
    propeller_twist: float = Input(0)
    mesh_deflection: float = Input(1e-4)

    @Attribute
    def label(self):
        return f"Blade #{self.identifying_number + 1}"  # this label is very useful, when I create the propeller using this, it will allow me to select them """

    @Attribute #creation of the propeller starting from the profiles
    def profiles(self):
        """careful!!! this can't have any name, needs to have exactly the name profiles becuase of how LoftedSolid is built"""
        return [self.prop_root_airfoil, self.prop_tip_airfoil]
    @Attribute
    def tip_positioning(self):
        return (translate(rotate(self.prop_root_airfoil.position, "y", radians(self.propeller_twist)),  # apply twist angle
                           "y", self.propeller_radius,)) #not affected by sweep or other stuff

    @Part
    def frame(self):
        """to visualize the given lifting surface reference frame"""
        return Frame()
    @Part
    def prop_root_airfoil(self):
        return Airfoil(airfoil_name=self.propeller_foil_root_name, #taken from fede/airfoil, needs to be initialized
                       chord=self.propeller_c_root,
                       thickness_factor=self.propeller_t_factor_root,
                       position=rotate(self.position, 'y', 0, deg=True),
                       mesh_deflection=self.mesh_deflection)
    @Part
    def prop_tip_airfoil(self):
        return Airfoil(airfoil_name=self.propeller_foil_tip_name, #taken from fede/airfoil, needs to be initialized
                       chord=self.propeller_c_tip,
                       thickness_factor=self.propeller_t_factor_tip,
                       position=self.tip_positioning,
                       mesh_deflection=self.mesh_deflection)


    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def blade_lofted_ruled(self):
        return LoftedSolid(profiles=self.profiles,
                           color="green",
                           ruled=True,  # by default this is set to False
                           mesh_deflection=self.mesh_deflection,
                           hidden=not (__name__ == '__main__'))

""""now that we identified the blade, we can create the propeller by rotating the correct amount of blades"""


if __name__ == "__main__":
    fus = Blade()

    from parapy.gui import display

    display(fus)
