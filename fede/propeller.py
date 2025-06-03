from math import radians, tan
from kbeutils.geom import cst_airfoil_coordinates
from parapy.geom import *
from parapy.core import *
from fede import Airfoil, Frame, Blade

class Rotor(Solid):
    rotor_radius : float = Input(1)


class Propeller(GeomBase):

    rotor_radius : float = Input(4)
    blade_count = Input(8)
    propeller_radius: float = Input(10)
    propeller_foil_root_name: str = Input("NACA2411")
    propeller_foil_tip_name: str = Input("NACA2411")
    propeller_c_root: float = Input(1)
    propeller_c_tip: float = Input(0.5)
    propeller_t_factor_root: float = Input(1.)
    propeller_t_factor_tip: float = Input(1.)
    propeller_twist: float = Input(0)
    mesh_deflection: float = Input(1e-4)
    colors: list[str] = Input(["red", "green", "blue", "yellow", "orange"])

    @Attribute
    def rotor_height(self):
        return 0.2 * self.propeller_c_root  # consider replacing with something done with the thickness


    @Part
    def rotor(self):
            return Cylinder(radius=self.rotor_radius,
                            position=translate(self.position, 'z', -self.rotor_height/2),
                            height=self.rotor_height)
    @Part
    def frame(self):
        """to visualize the given lifting surface reference frame"""
        return Frame()
    @Part
    def prop_blades(self):
        return Blade(quantify = self.blade_count, #this is the part that we implement to add a "number " to it in case we want to change it
                     color=self.colors[child.index % len(self.colors)], #a way to assign a continuous pattern of colors
                     position = rotate(self.position, 'z', (360/self.blade_count) * child.index, deg=True), #divides 360 based on how many and translates iteratively
                     propeller_radius = self.propeller_radius,
        propeller_foil_root_name = self.propeller_foil_root_name,
        propeller_foil_tip_name =  self.propeller_foil_tip_name,
        propeller_c_root = self.propeller_c_root,
        propeller_c_tip = self.propeller_c_tip,
        propeller_t_factor_root = self.propeller_t_factor_root,
        propeller_t_factor_tip = self.propeller_t_factor_tip,
        propeller_twist = self.propeller_twist,
        mesh_deflection = self.mesh_deflection,
        )

if __name__ == "__main__":
        fus = Propeller()
        from parapy.gui import display

        display(fus)
