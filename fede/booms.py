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

from parapy.geom import LoftedSolid, LoftedSurface, Circle, Vector, translate
from parapy.core import Input, Attribute, Part, child, widgets
from .liftingSurface import LiftingSurface


class Booms(LoftedSolid):
    """Fuselage geometry, a loft through circles.

    Note the use of LoftedSolid as superclass. It means that every
    Fuselage instance defines a lofted geometry. A required input for LoftedSolid
    is a list of profiles, so either an @Attribute or a @Part sequence
    called "profiles" must be present in the body of the class. Use 'Display
    node' in the root node of the object tree to visualise the (yellow) loft
    in the GUI graphical viewer

    Required inputs
    ---------------
    radius: float
        Fuselage radius in m
    length: float
        Fuselage length in m
    sections: list[float], optional
        radii of equally-spaced fuselage sections, in percent of `radius`.
        Number of entries determines number of fuselage sections created.
        Default: ``[10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 5]``

    mesh deflection: float, optional
        tolerance used for visual geometry display. Of the geometry and all
        components. Default is 1e-4
    color: str, optional
        color (as word, hex code).
        (overridden from parent class, uses a ColorPicker widget)

    ... plus all other inputs for ``parapy.geomLoftedSolid`` class

    Examples
    --------

    """

    #: fuselage radius
    #: :type: float
    booms_radius: float = Input()
    #: fuselage sections (percentage of nominal radius, at evenly-spaced stations)
    #: :type: collections.Sequence[float]
    booms_sections: list[float] = Input([30, 30, 30, 30, 30])
    #: fuselage length (m)
    #: :type: float
    booms_length: float = Input()

    mesh_deflection: float = Input(1e-4)

    # we're adding a colorpicker widget to the color Input:
    color = Input('blue', widget=widgets.ColorPicker)
    # In the same way, you can define drop-down menus, file pickers, checkboxes...
    # have a look at the documentation of parapy.core.widgets for more details

    @Attribute
    def section_radius(self) -> list[float]:
        """Section radius multiplied by the radius distribution
        through the length. Note that the numbers are percentages.

        Returns:
            List[float]: section radii in percentage along fuselage length
        """
        return [i * self.booms_radius / 100. for i in self.booms_sections]

    @Attribute
    def section_length(self) -> float:
        """The section length is determined by dividing the fuselage
        length by the number of fuselage sections.

        Returns:
            float: length of each fuselage section
        """
        return self.booms_length / (len(self.booms_sections) - 1)

    # Required slot of the superclass LoftedSolid.
    # Originally, this is an Input slot, but any slot type is fine as long as it contains
    # an iterable of the profiles for the loft.
    @Part
    def profiles(self):
        return Circle(quantify=len(self.booms_sections), color="Black",
                      radius=self.section_radius[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(self.position.rotate90('y'),  # circles are in XY plane, thus need rotation
                                         Vector(1, 0, 0),
                                         child.index * self.section_length))

    """
    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def booms_lofted_ruled(self):
        return LoftedSolid(profiles=self.profiles,
                           color="green",
                           ruled=True,  # by default this is set to False
                           mesh_deflection=self.mesh_deflection,
                           hidden=not(__name__ == '__main__'))
"""
########## AVL ###############

    @Part
    def avl_boom(self):
        return LiftingSurface(name="boom_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.booms_length,
                              c_tip=self.booms_length,
                              semi_span=self.booms_radius ,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=translate(self.position,'x',-self.booms_radius/2),
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=False)

    @Part
    def avl_booms_vert(self):
        return LiftingSurface(name="boom_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.booms_length,
                              c_tip=self.booms_length,
                              semi_span=self.booms_radius,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=translate(self.position.rotate90('x'),'y', -self.booms_radius/2),
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=False,
                              )


    @Part
    def avl_boom_mirrored(self):
        return LiftingSurface(name="boom_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.booms_length,
                              c_tip=self.booms_length,
                              semi_span=self.booms_radius,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=translate(translate(self.position, 'x', self.booms_radius / 2)
                                                 ,'y',-self.position.point[1]*2),
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=False)

    @Part
    def avl_boom_vert_mirrored(self):
        return LiftingSurface(name="boom_avl",
                              airfoil_root_name="0000",
                              airfoil_tip_name="0000",
                              c_root=self.booms_length,
                              c_tip=self.booms_length,
                              semi_span=self.booms_radius,
                              sweep=0,
                              twist=0,
                              dihedral=0,
                              inst_angle=0,
                              position=translate(translate(self.position.rotate90('x'), 'y', -self.booms_radius / 2)
                                                 ,'z',self.position.point[1]*2),
                              mesh_deflection=self.mesh_deflection,
                              is_mirrored=False,
                              )


##############################



if __name__ == '__main__':
    from parapy.gui import display
    fus = Booms(label="booms", booms_radius=1, booms_length=15, mesh_deflection=0.0001)
    display(fus)