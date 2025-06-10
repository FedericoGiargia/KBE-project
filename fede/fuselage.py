#from OCC.utils.top import length
import os
from parapy.core import *
from math import radians, sin, cos
from parapy.geom import *
import pandas as pd
from setuptools.command.rotate import rotate

from fede import Frame
from .liftingSurface import LiftingSurface
import matplotlib.pyplot as plt
from kbeutils.data import airfoils
class Fuselage(GeomBase): # remember, we want to use the parapy environment, NO RANDOM TUTORIALS
    # 1) erediti da Base
    fu_side= Input(400)
    fu_height = Input(200)
    fu_distance = Input(1000)
    mesh_deflection = Input(1e-3)
    """
    @Attribute
    def __str__(self):
        return ("this class creates a fuselage with a Loft. it is based on rectangles, that you define with side and height. "
                "it has a 3 dimension that is defined with the parameter distance. the position is central  w.r.t frame")
"""

    @Part
    def frame(self):
        """to visualize the given lifting surface reference frame"""
        return Frame()
    @Attribute
    def profiles(self):
        return [self.initial_profile,
                self.middle_profile,
                self.final_profile]
    @Attribute
    def back_profile(self):
        return [self.back_initial_profile, self.back_middle_profile, self.back_final_profile]

    @Part
    def middle_profile(self):
        return Rectangle(width=self.fu_side/1.3, length=self.fu_height/1.3,
                         position = translate(self.position.rotate90('y'), Vector(-1, 0, 0), self.fu_distance/25), color = "Black")
    @Part
    def initial_profile(self):
        return Rectangle(width=self.fu_side/10, length=self.fu_height / 10,
                         position = translate(self.position.rotate90('y'), Vector(-1, 0, 0), self.fu_distance / 14),
                         color="Black")

    @Part
    def final_profile(self):
        return Rectangle(
            width=self.fu_side,
            length=self.fu_height,
            color="Black",  position = translate(self.position.rotate90('y'))
        )

    @Part
    def back_initial_profile(self):
        return (Rectangle(width=self.fu_side , length=self.fu_height,
                         position=translate(self.position.rotate90('y'), Vector(1, 0, 0), self.fu_distance*3/4),
                         color="Black"))
    @Part
    def back_middle_profile(self):
        return (Rectangle(width=self.fu_side / 2.5, length=self.fu_height/ 2.5,
                         position=translate(self.position.rotate90('y'), Vector(1, 0, 0), self. fu_distance*3/4 + self.fu_distance / 16),
                         color="Black"))
    @Part
    def back_final_profile(self):
        return Rectangle(width=self.fu_side / 10, length=self.fu_height/10,
                         position=translate(self.position.rotate90('y'), Vector(1, 0, 0),  self. fu_distance*3/4 + self.fu_distance / 8),
                         color="Black")
    @Part
    def front_lofted_fus(self):
        return LoftedSolid(profiles = self.profiles, color = "Green", transparency = 0.7)
    @Part
    def middle_fus(self):
        return Box(width = self.fu_side, height = self.fu_height, length = self.fu_distance*3/4, color = "Red", transparency = 0.6, position = translate(self.position.rotate90('-z').rotate90('y'), '-x', self.fu_side/2, 'z', -self.fu_height/2))

    @Part
    def back_lofted_fus(self):
        return LoftedSolid(profiles = self.back_profile, color = "Red")

    "add way to size the battery, remember!!! it is inside the methods"
    @Part
    def brain(self):
        return Box(width = self.fu_side/6, height = self.fu_height/6, length = self.fu_height/6,
                   position =translate(self.position.rotate90('-z').rotate90('y'), '-x', 0, 'z', 0, 'y', -self.fu_distance/20))

    @Part
    def battery(self):
        return Box(width = self.fu_side/3, height = self.fu_height/3, length = self.fu_distance/3, color = "Black", position = translate(self.position.rotate90('-z').rotate90('y'), '-x', -self.fu_side/2 +self.fu_side/3, 'z', -self.fu_height/6, 'y', self.fu_distance/8))


############## AVL ############

    @Part
    def avl_fuselage(self):
        return LiftingSurface(name="fuselage_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.fu_distance,
                              c_tip=self.fu_distance,
                              semi_span=self.fu_height / 2,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=self.position,
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=True)

    @Part
    def avl_fuselage_vert(self):
        return LiftingSurface(name="fuselage_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.fu_distance,
                              c_tip=self.fu_distance,
                              semi_span=self.fu_side,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=translate(self.position.rotate90('x'),'y',-self.fu_side/2),
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=False,
                              )



################################


###############################

# 3) display solo se __main__
if __name__ == "__main__":
    fus = Fuselage()

    from parapy.gui import display
    display(fus)
