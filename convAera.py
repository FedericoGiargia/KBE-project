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

import os
from math import radians, sqrt
from parapy.geom import GeomBase, translate, rotate, MirroredShape
from parapy.core import Input, Attribute, Part, attribute
from fede import LiftingSurface, Fuselage, Frame, file_found, Booms
from kbeutils import avl


maindir = os.path.dirname(__file__)

def calc_span(area, aspect_ratio):
    return sqrt(area * aspect_ratio)


class Aircraft(GeomBase):

    fu_side: float = Input()
    fu_height : float = Input()
    #fu_sections: list[float] = Input([10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 5])
    fu_distance: float = Input()

    #charact of the booms
    booms_radius: float = Input()
    booms_sections: list[float] = Input([30, 30, 30, 30, 30])
    booms_length: float = Input()

    # airfoils default to pre-defined B29 airfoils
    airfoil_root_name: str = Input("naca2411")
    airfoil_tip_name: str = Input("naca2411")
    w_c_root: float = Input()
    w_c_tip: float = Input()

    #: to reduce/increase the thickness of the airfoil from the .dat file
    t_factor_root: float = Input(1)
    t_factor_tip: float = Input(1)
    # Default: Uses airfoils as provided, no change to thickness

    w_semi_span: float = Input()
    sweep: float = Input(0)
    twist: float = Input(0)
    wing_dihedral: float = Input(0)
    wing_inst_angle: float = Input(0)

    #: longitudinal position w.r.t. fuselage length. (% of fus length)
    wing_position_fraction_long: float = Input(0.4)

    #: vertical position w.r.t. to fus  (% of fus radius)
    wing_position_fraction_vrt: float = Input(0.8)

    #: vertical position w.r.t. to wing  (% of wing span)
    boom_position_fraction_long: float = Input(0.5)


    #: longitudinal position of the vertical tail, as % of fus length
    vt_long: float = Input(0.8)
    vt_taper: float = Input(0.4)

    mesh_deflection: float = Input(1e-4)

    #: Inputs for AVL
    cl_cr: float = Input()  # cruise lift coefficient
    mach_cr: float = Input()  # Cruise Mach number (used for AVL analysis)


    #: Additional inputs required
    span: float = Input()

    @Part
    def frame(self):
        """This helps visualise the wing local reference frame"""
        return Frame(pos=self.position)
    """
    @Attribute
    def fuselage_position(self):
        return rotate(self.position, 'y', radians(90))
        """
    @Attribute

    def right_wing_planform_area(self):
        return (self.w_semi_span*2) ** 2 / self.right_wing.aspect_ratio


    @Attribute
    def boom_position(self):
        return translate(self.position( 'y', self.boom_position_fraction_long * self.w_semi_span,
                                'z', self.wing_position_fraction_vrt * - self.fu_side
                                ),
                      'x', radians(self.wing_dihedral) # dihedral applied by rotation of position
                      )

    @Attribute
    def wing_position(self):
        return rotate(translate(# longitudinal and vertical translation of position w.r.t. fuselage
                                self.position,
                                'x', self.wing_position_fraction_long * self.fu_distance,
                                'z', self.wing_position_fraction_vrt * - self.fu_side
                                ),
                      'x', radians(self.wing_dihedral) # dihedral applied by rotation of position
                      )

    @Attribute
    def v_tail_position(self):
        return rotate(translate
                            (self.position,
                             "x", self.vt_long * self.fu_distance,
                             "z", self.fu_side * 0.7),
                            "x",
                      radians(90)
                      )

    @Attribute
    def h_tail_position(self):
        return rotate(translate
               (self.position, "x",
                self.fu_distance - self.w_c_root),
               "x", radians(self.wing_dihedral + 5)
                      )


    @Part
    def fuselage(self):
        return Fuselage(
            fu_side=self.fu_side,
            fu_height=self.fu_height,
            fu_distance=self.fu_distance,
            color="Green",
            mesh_deflection=self.mesh_deflection

        )

    @Part
    def right_wing(self):
        return LiftingSurface(
            pass_down="airfoil_root_name, airfoil_tip_name,"
                      "t_factor_root, t_factor_tip,"
                      "sweep, twist",
            c_root=self.w_c_root,
            c_tip=self.w_c_tip,
            semi_span=self.w_semi_span,
            inst_angle = self.wing_inst_angle,
            position=self.wing_position,
            mesh_deflection=self.mesh_deflection,
            airfoil_name_avl="2411",
            name="right_wing",
            is_mirrored=True)

    @Part
    def left_wing(self):
        return MirroredShape(shape_in=self.right_wing,
                             reference_point=self.position,
                             # Two vectors and a point to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=self.mesh_deflection)

    @Part
    def vert_tail(self):
        return LiftingSurface(
            c_root=self.w_c_root,
            c_tip=self.w_c_root * self.vt_taper,
            airfoil_root_name="naca0015",
            airfoil_tip_name="naca0015",
            t_factor_root=0.9 * self.t_factor_root,
            t_factor_tip=0.9 * self.t_factor_tip,
            semi_span=self.w_semi_span / 3,
            sweep=45,
            is_mirrored=False,
            twist=0,
            position=self.v_tail_position,
            mesh_deflection=self.mesh_deflection,
            airfoil_name_avl="0015",
            name="vert_tail"
        )
    @Part
    def left_boom(self):
        return Booms(booms_radius=self.booms_radius,
                     booms_length=self.booms_length,
                     booms_sections = self.booms_sections,
                     position = self.boom_position,
                     mesh_deflection=0.0001)
    @Part
    def right_boom(self):
        return MirroredShape(shape_in=self.left_boom,
                             reference_point=self.position,
                             # Two vectors and a point to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=self.mesh_deflection)

    @Part
    def h_tail_right(self):
        return LiftingSurface(
            c_root=self.w_c_root / 1.5,
            c_tip=self.w_c_tip / 2,
            airfoil_root_name="naca2411",
            airfoil_tip_name="naca2411",
            t_factor_root=0.9 * self.t_factor_root,
            t_factor_tip=0.9 * self.t_factor_tip,
            semi_span=self.w_semi_span / 2.5,
            sweep=self.sweep + 10,
            twist=0,
            position=self.h_tail_position,
            mesh_deflection=self.mesh_deflection,
            airfoil_name_avl="2411",
            name="h_tail_right",
            is_mirrored=True
        )

    @Part
    def h_tail_left(self):
        return MirroredShape(shape_in=self.h_tail_right,
                             reference_point=self.position,
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=self.mesh_deflection
                             )


    ### AVL ###

    @Attribute(in_tree=True)
    def avl_surfaces(self):  # a list of all AVL surfaces in the aircraft:
        return self.find_children(lambda o: isinstance(o, avl.Surface))
        # This automatically scans the product tree and collects all
        # instances of the avl.Surface class.
        # (if you don't know what `lambda` is doing there: that's a somewhat
        # more advanced feature of functional programming, but it's not
        # required knowledge for this course. Just use it as provided above,
        # and you'll be fine. Feel free to check out the
        # Python documentation about it, though, if you're curious.)

        # Otherwise, you can of course also manually specify the surfaces you
        # want to include, like this:
        # return [self.wing.avl_surface, self.tail.avl_surface]
        # (but make sure you forget no surface that needs to be included in the
        # model!)

    @Part
    def avl_configuration(self):
        """Configurations are made separately for each Mach number that is provided."""
        return avl.Configuration(name='cruise analysis',
                                 reference_area=self.right_wing_planform_area*2,
                                 reference_span=self.w_semi_span*2,
                                 reference_chord=self.right_wing.mac,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.mach_cr)


    @Attribute
    def avl_settings(self):
        """
        Format for AVL inputs:
            dict(<parameter to define>: <value>)
            value can be defined either by a number or with `avl.Parameter`:
            avl.Parameter(name=<var to adjust>,
                          setting=<var for which to achieve a given value>
                          value=<value to achieve>)
        These need to be defined either in Input or in a separate Attribute, in
        order to allow ParaPy to trace dependencies (defining this dictionary
        in an argument for avl.Interface() or avl.Case fails for that reason)
        """
        return {'alpha': avl.Parameter(name='alpha',
                                       setting='CL',
                                       value=self.cl_cr)}

    @Part
    def avl_case(self):
        """avl case definition using the avl_settings dictionary defined above"""
        return avl.Case(name='fixed_cl',  # name _must_ correspond to type of case
                        settings=self.avl_settings)

    @Part
    def avl_analysis(self):
        return avl.Interface(configuration=self.avl_configuration,
                             # note: AVL always expects a list of cases!
                             cases=[self.avl_case])

    @Attribute
    def l_over_d(self):
        """process AVL results and compute L/D"""
        # Since AVL always receives a list of cases, but produces a dictionary of
        # results (using the name supplied to avl.Case as key)
        # each result is itself a nested dictionary, containing a lot of
        # information so it's a good idea to extract the relevant numbers
        # as @Attributes
        return {result['Name']: result['Totals']['CLtot'] / result['Totals']['CDtot']
                for case_name, result in self.avl_analysis.results.items()}
        # The above is a bit more complicated than needed since there's only
        # a single case name etc., but addressing it "by name" means we'd need
        # to update the definition above every time we change something in the
        # analysis.






if __name__ == '__main__':
    from parapy.gui import display
    ac = Aircraft(label="aircraft",
                   fu_side=3,
                   #fu_sections=[10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 10],
                   fu_height = 5.65,
                   fu_distance = 50,
                   airfoil_root_name="naca2411",
                   airfoil_tip_name="naca2411",
                   w_c_root=6., w_c_tip=2.3,
                   t_factor_root=1, t_factor_tip=1,
                   w_semi_span=27.,
                   sweep=20, twist=-5, wing_dihedral=3,
                   wing_position_fraction_long=0.4, wing_position_fraction_vrt=0.8,
                   vt_long=0.8, vt_taper=0.4, booms_radius=1,
                   booms_length=70,
                   booms_sections = [30, 30, 30, 30, 30],
                   mesh_deflection=0.0001,
                   mach_cr=0.4,
                   cl_cr=0.4)


    display(ac)


