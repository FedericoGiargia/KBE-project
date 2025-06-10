from math import radians, tan
from kbeutils.geom import cst_airfoil_coordinates
from parapy.geom import LoftedSolid, translate, rotate, FittedCurve, GeomBase
from parapy.core import Input, Attribute, Part, child
from fede import Airfoil, Frame, LiftingSurface
class Winglet(GeomBase):
    """I will define both a loftedsolid, and the geometry for luis so some wings that move defined as the loft between 5 stations"""
    name: str = Input()
    airfoil_names: list[str] = Input(["NACA2411", "NACA2411"]) #we can add a list in case we want aerodynamic twist (not only geometric)
    airfoil_number: int = Input(20)
    winglet_c_root: float = Input(10)
    winglet_c_tip: float = Input(0.002)
    t_factor_root: float = Input(1.)
    t_factor_tip: float = Input(1.)
    semi_span: float = Input(5)
    winglet_sweep: float = Input(40)
    twist: float = Input(0)
    dihedral: float = Input(0)
    inst_angle: float = Input(0)
    colors: list[str] = Input(["red", "green", "blue", "yellow", "orange"])
    mesh_deflection: float = Input(1e-4)
    @Attribute
    def delta_chords(self):
        return (self.winglet_c_root - self.winglet_c_tip)/self.airfoil_number
    @Part
    def airfoil_profiles(self):
        return Airfoil(quantify = self.airfoil_number, #this is the part that we implement to add a "number " to it in case we want to change it
                     color=self.colors[child.index % len(self.colors)], #a way to assign a continuous pattern of colors
                     position = rotate(translate(self.position, 'x', -(self.semi_span * tan(radians(self.winglet_sweep))/self.airfoil_number)*child.index,
                                                 'y', -(self.semi_span / self.airfoil_number)*child.index, 'z',
                                                 (0.3*(self.semi_span / self.airfoil_number)*child.index)**4),
                                       'x', -(90/self.airfoil_number) * child.index, deg=True), #divides 360 based on how many and translates iteratively
                     airfoil_name=self.airfoil_names[child.index % len(self.airfoil_names)], #in this case we can define the names
                     chord=self.winglet_c_root - (self.delta_chords * child.index),
                     thickness_factor=self.t_factor_root,
                     mesh_deflection=self.mesh_deflection)
    @Part
    def lofted_winglet(self):
        return LoftedSolid(profiles = self.airfoil_profiles,
                           ruled = True,)


########## AVL ##########
'''
    @Part
    def lifting_component(self):
        return LiftingSurface(name=self.airfoil_names[0],
                                c_root=self.winglet_c_root,
                                c_tip=1,
                                sweep = self.winglet_sweep,
                                semi_span=self.semi_span,
                                position=self.position.rotate90('x'),
                                is_mirrored=False)

'''
#########################




if __name__ == "__main__":
        fus = Winglet()

        from parapy.gui import display

        display(fus)
