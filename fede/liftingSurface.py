#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 ParaPy Holding B.V.
#
# This file is subject to the terms and conditions defined in
# the license agreement that you have received with this source code
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from math import radians, tan
from kbeutils.geom import cst_airfoil_coordinates
from parapy.geom import LoftedSolid, translate, rotate, FittedCurve
from parapy.core import Input, Attribute, Part
from fede import Airfoil, Frame

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

if __name__ == '__main__':
    from parapy.gui import display
    ls = LiftingSurface(label="lifting surface",
                        c_root=5,
                        c_tip=2.5,
                        semi_span=27,
                         mesh_deflection=1e-4)
    display(ls)