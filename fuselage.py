#from OCC.utils.top import length
import os
from parapy.core import Base, Attribute, Input, Part
from parapy.geom import LoftedSolid, Rectangle, Vector, translate, GeomBase, FittedCurve, LoftedSurface
import pandas as pd
from fede import Frame
import matplotlib.pyplot as plt
from kbeutils.data import airfoils
class Fuselage(LoftedSolid): # remember, we want to use the parapy environment, NO RANDOM TUTORIALS
    # 1) erediti da Base
    fu_side= Input(200)
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
    @Part
    def middle_profile(self):
        return Rectangle(width=self.fu_side, length=self.fu_height,
                         position = translate(self.position.rotate90('y')), color="Black")
    @Part
    def initial_profile(self):
        return Rectangle(width=self.fu_side/10, length=self.fu_height / 10,
                         position = translate(self.position.rotate90('y'), Vector(-1, 0, 0), self.fu_distance / 10),
                         color="Black")

    @Part
    def final_profile(self):
        return Rectangle(
            width=self.fu_side,
            length=self.fu_height,
            position=translate(self.position.rotate90('y'), Vector(1,0,0), self.fu_distance),
            color="Black"
        )

    @Attribute
    def profiles(self):
        return [self.initial_profile,
                self.middle_profile,
                self.final_profile]



# 3) display solo se __main__
if __name__ == "__main__":
    fus = Fuselage()

    from parapy.gui import display
    display(fus)
