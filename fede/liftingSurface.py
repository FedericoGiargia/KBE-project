from math import radians, tan
from kbeutils.geom import cst_airfoil_coordinates
from parapy.geom import LoftedSolid, translate, rotate, FittedCurve
from parapy.core import Input, Attribute, Part
from parapy.geom import GeomBase, ScaledCurve
from parapy.core import Input, Attribute, Part, DynamicType, child
from parapy.core.validate import AdaptedValidator
import kbeutils.avl as avl
from kbeutils.geom import Naca5AirfoilCurve, Naca4AirfoilCurve
from parapy.geom import GeomBase, LoftedShell, MirroredSurface, rotate
from fede import Airfoil, Frame
from fede.section import Section



class LiftingSurface(LoftedSolid):  # note use of loftedSolid as superclass

    name: str = Input()
    airfoil_root_name: str = Input("NACA2411")
    airfoil_tip_name: str = Input("NACA2411")

    c_root: float = Input()
    c_tip: float = Input()
    t_factor_root: float = Input(1.)
    t_factor_tip: float = Input(1.)

    semi_span: float = Input()
    sweep: float = Input(0)
    twist: float = Input(0)
    dihedral: float = Input(0)
    inst_angle: float = Input(0)

    mesh_deflection: float = Input(1e-4)
    is_mirrored: bool = Input()
    airfoil_name_avl: str = Input("2412")

    # Control surfaces
    control_name: str = Input(None)
    control_hinge_loc: float = Input(None)
    duplicate_sign: int = Input(1)



    # required slot for the superclass LoftedSolid
    # (usually an @Input, but we're turning it into an @Attribute)
    @Attribute
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]
    # Because the class inherits from `LoftedSolid`, it requires profiles to loft over, and expects
    # to find them as a slot called `profiles`. When instantiating a `LoftedSolid` object, the profiles would  normally,
    # be an `Input` slot, but we can also serve them as an `Attribute` -- as long as `self.profiles` is present.
    # try commenting this part out and see how it fails!

    @Part
    def frame(self):
        """to visualize the given lifting surface reference frame"""
        return Frame()

    """
    @Attribute
    def __str__(self):
        return (
            "this class creates a wing with a Loft. it is based on airfoil, chosen to be NACA, that you can't define now. "
            "it has a 3 dimension that is defined with the parameter semi_span. the position is  w.r.t fuselage")
"""
    @Attribute
    def tip_position(self):
        return (translate(rotate(self.root_airfoil.position, "y", radians(self.twist)),  # apply twist angle
                           "y", self.semi_span,
                           "x", self.semi_span * tan(radians(self.sweep)),
                            "z", self.semi_span * tan(radians(self.dihedral))))  # apply sweep

    @Part
    def root_airfoil(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root_name,
                       chord=self.c_root,
                       thickness_factor=self.t_factor_root,
                       position=rotate(self.position, 'y', self.inst_angle, deg=True),
                       mesh_deflection=self.mesh_deflection)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip_name,
                       chord=self.c_tip,
                       thickness_factor=self.t_factor_tip,
                       position=self.tip_position,  # apply sweep
                       mesh_deflection=self.mesh_deflection)

    @Attribute
    def aspect_ratio(self):
        return (self.half_span * 2) / self.c_root

    @Attribute
    def taper_ratio(self):
        return self.c_tip / self.c_root

    @Attribute
    def chords(self):
        root = self.c_root
        tip = self.c_tip
        return root, tip

    @Attribute
    def planform_area(self):
        return (self.half_span * 2) ** 2 / self.aspect_ratio

    @Attribute
    def half_span(self):
        return self.semi_span



    @Attribute
    def section_positions(self):
        root = self.position
        tip = self.tip_position
        return root, tip

    @Attribute
    def chord_root(self):
        return self.chords[0]

    @Attribute
    def mac(self):
        return 2 / 3 * self.chord_root * (1 + self.taper_ratio + self.taper_ratio ** 2) / (1 + self.taper_ratio)

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                        airfoil_name=self.airfoil_name_avl,
                        chord=self.chords[child.index],
                        position=self.section_positions[child.index],

                        control_name=self.control_name,
                        control_hinge_loc=self.control_hinge_loc,
                        duplicate_sign=self.duplicate_sign
                        )


    @Part
    def avl_surface(self):
        """Defines an AVL surface, based on the section camberlines"""
        return avl.Surface(name=self.name,
                            n_chordwise=12,
                            chord_spacing=avl.Spacing.cosine,
                            n_spanwise=20,
                            span_spacing=avl.Spacing.cosine,
                            y_duplicate=self.position.point[1] if self.is_mirrored else None,
                            sections=[section.avl_section
                                      for section in self.sections])




if __name__ == '__main__':
    from parapy.gui import display
    ls = LiftingSurface(label="lifting surface",
                        c_root=5,
                        c_tip=2.5,
                        semi_span=27,
                         mesh_deflection=1e-4)
    display(ls)