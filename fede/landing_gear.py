from fede import Airfoil, Frame, LiftingSurface
import kbeutils.avl as avl
from fede.section import Section
from math import radians, tan
from parapy.geom import *
from parapy.core import *
class LiftingLandingGear(GeomBase):
    lg_foil_root_name: str = Input("NACA2411")
    lg_foil_tip_name: str = Input("NACA2411")
    lg_c_root: float = Input(2)
    lg_c_tip: float = Input(2)
    lg_t_factor_root: float = Input(1.)
    lg_t_factor_tip: float = Input(1.)
    lg_twist: float = Input(0)
    mesh_deflection: float = Input(1e-4)
    lg_semi_span : float = Input(2)
    box_height = 30
    lg_dihedral: float = Input(0)

    @Attribute
    def tip_positioning(self):
        return (
            translate(rotate(self.lg_root_airfoil.position, "y", radians(self.lg_twist)),  # apply twist angle
                      "y", self.lg_semi_span, ))  # not affected by sweep or other stuff

    @Attribute  # creation of the propeller starting from the profiles
    def profiles(self):
        """careful!!! this can't have any name, needs to have exactly the name profiles becuase of how LoftedSolid is built"""
        return [self.lg_root_airfoil, self.lg_tip_airfoil]
    @Part
    def frame(self):
        return Frame()

    @Part
    def lg_root_airfoil(self):
        return Airfoil(airfoil_name=self.lg_foil_root_name,  # taken from fede/airfoil, needs to be initialized
                       chord=self.lg_c_root,
                       thickness_factor=self.lg_t_factor_root,
                       position=rotate(self.position, 'y', 0, deg=True),
                       mesh_deflection=self.mesh_deflection)

    @Part
    def lg_tip_airfoil(self):
        return Airfoil(airfoil_name=self.lg_foil_tip_name,  # taken from fede/airfoil, needs to be initialized
                       chord=self.lg_c_tip,
                       thickness_factor=self.lg_t_factor_tip,
                       position=self.tip_positioning,
                       mesh_deflection=self.mesh_deflection)

    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def lg_lofted_ruled(self):
        return LoftedSolid(profiles=self.profiles,
                           color="green",
                           ruled=True,  # by default this is set to False
                           mesh_deflection=self.mesh_deflection,
                           hidden= True)


    # Originally Part but now attribute so it is not in the final STEP export
    @Attribute
    def cutting_box(self):
        return Box(height=self.box_height,
                 length = self.box_height,
                 width= self.box_height,
                   position = translate(self.position,'x', self.lg_c_root/3, 'z', -self.lg_semi_span),  # check in the class Box definition the effect of setting centered to False
                   color="green", hidden = True)

    @Part
    def fixed_lg(self):
        """Splits solids through their intersection. Returns a list of solids"""
        return SubtractedSolid(shape_in=self.lg_lofted_ruled, tool=self.cutting_box)  # False by default
    @Part
    def elevator(self):
        return SubtractedSolid(shape_in = self.lg_lofted_ruled, tool = self.fixed_lg, color = 'green')


########## AVL ##########

    @Part
    def lifting_component(self):
        return LiftingSurface(name=self.lg_foil_root_name,
                                c_root=self.lg_c_root,
                                c_tip=self.lg_c_tip,
                                sweep = 0,
                                semi_span=self.lg_semi_span,
                                position=self.lg_root_airfoil.position,
                                dihedral = self.lg_dihedral,
                                is_mirrored=False)


#########################


class LandingGear(GeomBase):
    leg_radius : float = Input(0.2)
    leg_height : float = Input(5)
    rubber_radius : float = Input(0.4)
    @Attribute
    def rubber_height(self):
        return 1.1*self.rubber_radius
    @Attribute
    def rubber_position(self):
        return translate(self.position('z', self.leg_height))
    @Part
    def leg(self):
        return Cylinder(radius = self.leg_radius,
                        height = self.leg_height)
    @Part
    def rubber(self):
        return Cylinder(radius = self.rubber_radius,
                        position = self.rubber_position,
                        height = self.rubber_height)

if __name__ == "__main__":
    fus = LiftingLandingGear()

    from parapy.gui import display

    display(fus)

