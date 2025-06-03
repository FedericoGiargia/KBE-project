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
from math import radians, tan
from parapy.geom import GeomBase, translate, rotate, MirroredShape
from parapy.core import Input, Attribute, Part
from fede import LiftingSurface, Fuselage, Frame, file_found, Booms, Blade, Propeller, LiftingLandingGear, LandingGear, Winglet

"""important, this is a definition of all the components that we have in ConvAera:
- landing gear defined as a rotated LiftingSurface
- elevons defined as couple of rotated LiftingSurface, mirrored w.r.t. the centerline (assume symmetrical model)
- propellers defined as n* LiftingSurface, rotating around a cylinder, mirrored w.r.t the centerline
- wings defined as LiftingSurface, mirrored w.r.t. the centerline
- there is a vertical tailplane, defined as rotated LiftingSurface, but could also be substituted by rotated elevators
- fuselage defined as a LoftedSurface, given by squares
- landing gear front defined as Cylinder
- booms defined as LoftedSurface, consider changing with cylinders"""
maindir = os.path.dirname(__file__)


class Aircraft(GeomBase):

    fu_side: float = Input()
    fu_height : float = Input()
    #fu_sections: list[float] = Input([10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 5])
    fu_distance: float = Input(40)

    #charact of the booms
    booms_radius: float = Input()
    booms_sections: list[float] = Input([30, 30, 30, 30, 30])
    booms_length: float = Input(30)
    #: vertical position w.r.t. to wing  (% of wing span)
    boom_position_fraction_long: float = Input(0.8)


   # characterization of the propeller

    rotor_radius: float = Input(0.3)
    blade_count = Input(6)
    propeller_radius: float = Input(8)
    propeller_foil_root_name: str = Input("NACA2411")
    propeller_foil_tip_name: str = Input("NACA2411")
    propeller_c_root: float = Input(0.8)
    propeller_c_tip: float = Input(0.2)
    propeller_t_factor_root: float = Input(1.)
    propeller_t_factor_tip: float = Input(1.)
    propeller_twist: float = Input(0)
    mesh_deflection: float = Input(1e-4)

    #definition of the winglet

    winglet_c_tip: float = Input(0.002)


    #definition of the landing gear
    lg_foil_root_name: str = Input("NACA2411")
    lg_foil_tip_name: str = Input("NACA2411")
    lg_c_root: float = Input(3)
    lg_c_tip: float = Input(3)
    lg_t_factor_root: float = Input(1.)
    lg_t_factor_tip: float = Input(1.)
    lg_twist: float = Input(0)
    lg_semi_span: float = Input(5)
    box_height = 30

    leg_radius: float = Input(0.2)
    leg_height: float = Input(5)
    rubber_radius: float = Input(0.4)


    # airfoils default to pre-defined B29 airfoils
    airfoil_root_name: str = Input("NACA2411")
    airfoil_tip_name: str = Input("NACA2411")
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




    #: longitudinal position of the vertical tail, as % of fus length
    vt_long: float = Input(0.8)
    vt_taper: float = Input(0.4)

    mesh_deflection: float = Input(1e-4)

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
    def wing_tip_position(self):
        return (translate(rotate(self.wing_position, "y", radians(self.twist)),  # apply twist angle
                          "y", self.w_semi_span,
                          "x", self.w_semi_span * tan(radians(self.sweep)),
                          "z", self.w_semi_span * tan(radians(self.wing_dihedral))))  # apply sweep
    @Attribute
    def lifting_lg_position(self):
        translate_lg = translate(self.position( 'x', self.booms_length - self.lg_c_root, 'y', self.boom_position_fraction_long * self.w_semi_span,
                                'z', self.wing_position_fraction_vrt * - self.fu_side - self.booms_radius
                                ),
                     # dihedral applied by rotation of position
                      )
        return rotate(rotate(rotate(translate_lg, 'y', radians(180)), 'x', radians(90)), 'y', radians(180))

    @Attribute
    def left_lg_position(self):
        translate_lg = translate(self.position( 'y',
                                               self.boom_position_fraction_long * self.w_semi_span,
                                               'z', self.wing_position_fraction_vrt * - self.fu_side - self.booms_radius
                                               ),
                                 # dihedral applied by rotation of position
                                 )
        return rotate(translate_lg, 'y', radians(180))

    @Attribute
    def rotor_height(self):
        return 0.2 * self.propeller_c_root  # consider replacing with something done with the thickness
    @Attribute
    def pusher_propeller_position(self):
        "very good example on what NOT to do!! this changes the RF"
        #  rotation =  rotate(self.position, 'y', radians(90))
        # return(translate(rotation, 'x', self.fu_distance)
        rotation =  rotate(self.position, 'y', radians(90))
        return translate(rotation, 'z', self.fu_distance*7/8 + self.rotor_radius/2)

    @Attribute
    def right_forward_propeller_position(self): #moved with the same rule as the booms, absolute RF, consider implementing relative
        return translate(self.position( 'y', self.boom_position_fraction_long * self.w_semi_span,
                                'z', self.wing_position_fraction_vrt * - self.fu_side + self.booms_radius + self.rotor_height/2
                                ),
                     # dihedral applied by rotation of position
                      )

    @Attribute
    def left_forward_propeller_position(self):  # moved with the same rule as the booms, absolute RF, consider implementing relative
        return translate(self.position('y', - self.boom_position_fraction_long * self.w_semi_span,
                                       'z',  self.wing_position_fraction_vrt * - self.fu_side + self.booms_radius + self.rotor_height/2
                                       ),
                         # dihedral applied by rotation of position
                         )

    @Attribute
    def right_rear_propeller_position(
            self):  # moved with the same rule as the booms, absolute RF, consider implementing relative
        return translate(self.position('x', self.booms_length, 'y', self.boom_position_fraction_long * self.w_semi_span,
                                       'z',  self.wing_position_fraction_vrt * - self.fu_side + self.booms_radius + self.rotor_height/2
                                       ),
                           # dihedral applied by rotation of position
                         )

    @Attribute
    def left_rear_propeller_position(
            self):  # moved with the same rule as the booms, absolute RF, consider implementing relative
        return translate(self.position('x', self.booms_length, 'y', - self.boom_position_fraction_long * self.w_semi_span,
                                       'z',  self.wing_position_fraction_vrt * - self.fu_side + self.booms_radius + self.rotor_height/2
                                       ),
                 # dihedral applied by rotation of position
                         )

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
            sweep = self.sweep,
            semi_span=self.w_semi_span,
            inst_angle = self.wing_inst_angle,
            position=self.wing_position,
            dihedral = self.wing_dihedral,
            mesh_deflection=self.mesh_deflection)

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
            airfoil_root_name="b29root",
            airfoil_tip_name="b29tip",
            t_factor_root=0.9 * self.t_factor_root,
            t_factor_tip=0.9 * self.t_factor_tip,
            semi_span=self.w_semi_span / 3,
            sweep=45,
            twist=0,
            position=self.v_tail_position,
            mesh_deflection=self.mesh_deflection
        )
    @Part
    def left_boom(self):
        return Booms(booms_radius=self.booms_radius,
                     booms_length=self.booms_length,
                     booms_sections = self.booms_sections,
                     position = self.boom_position,
                     mesh_deflection=0.0001)
    @Part
    def right_forward_propeller(self):
        return Propeller(rotor_radius = self.rotor_radius,
                         position = self.right_forward_propeller_position, #this part is the one that changes
    blade_count = self.blade_count,
    propeller_radius = self.propeller_radius,
    propeller_foil_root_name = self.propeller_foil_root_name,
    propeller_foil_tip_name = self.propeller_foil_tip_name,
    propeller_c_root = self.propeller_c_root,
    propeller_c_tip = self.propeller_c_tip,
    propeller_t_factor_root = self.propeller_t_factor_root,
    propeller_t_factor_tip = self.propeller_t_factor_tip,
    propeller_twist = self.propeller_twist,
    mesh_deflection = self.mesh_deflection
                         )
    @Part
    def pushing_propeller(self):
        return Propeller(rotor_radius=self.rotor_radius,
                         position=self.pusher_propeller_position,  # this part is the one that changes
                         blade_count=self.blade_count,
                         propeller_radius=self.propeller_radius,
                         propeller_foil_root_name=self.propeller_foil_root_name,
                         propeller_foil_tip_name=self.propeller_foil_tip_name,
                         propeller_c_root=self.propeller_c_root,
                         propeller_c_tip=self.propeller_c_tip,
                         propeller_t_factor_root=self.propeller_t_factor_root,
                         propeller_t_factor_tip=self.propeller_t_factor_tip,
                         propeller_twist=self.propeller_twist,
                         mesh_deflection=self.mesh_deflection
                         )
    @Part
    def left_forward_propeller(self):
        return Propeller(rotor_radius=self.rotor_radius,
                         position=self.left_forward_propeller_position,  # this part is the one that changes
                         blade_count=self.blade_count,
                         propeller_radius=self.propeller_radius,
                         propeller_foil_root_name=self.propeller_foil_root_name,
                         propeller_foil_tip_name=self.propeller_foil_tip_name,
                         propeller_c_root=self.propeller_c_root,
                         propeller_c_tip=self.propeller_c_tip,
                         propeller_t_factor_root=self.propeller_t_factor_root,
                         propeller_t_factor_tip=self.propeller_t_factor_tip,
                         propeller_twist=self.propeller_twist,
                         mesh_deflection=self.mesh_deflection
                         )

    @Part
    def right_rear_propeller(self):
        return Propeller(rotor_radius=self.rotor_radius,
                         position=self.right_rear_propeller_position,  # this part is the one that changes
                         blade_count=self.blade_count,
                         propeller_radius=self.propeller_radius,
                         propeller_foil_root_name=self.propeller_foil_root_name,
                         propeller_foil_tip_name=self.propeller_foil_tip_name,
                         propeller_c_root=self.propeller_c_root,
                         propeller_c_tip=self.propeller_c_tip,
                         propeller_t_factor_root=self.propeller_t_factor_root,
                         propeller_t_factor_tip=self.propeller_t_factor_tip,
                         propeller_twist=self.propeller_twist,
                         mesh_deflection=self.mesh_deflection
                         )

    @Part
    def left_rear_propeller(self):
        return Propeller(rotor_radius=self.rotor_radius,
                         position=self.left_rear_propeller_position,  # this part is the one that changes
                         blade_count=self.blade_count,
                         propeller_radius=self.propeller_radius,
                         propeller_foil_root_name=self.propeller_foil_root_name,
                         propeller_foil_tip_name=self.propeller_foil_tip_name,
                         propeller_c_root=self.propeller_c_root,
                         propeller_c_tip=self.propeller_c_tip,
                         propeller_t_factor_root=self.propeller_t_factor_root,
                         propeller_t_factor_tip=self.propeller_t_factor_tip,
                         propeller_twist=self.propeller_twist,
                         mesh_deflection=self.mesh_deflection
                         )

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
            airfoil_root_name="b29root",
            airfoil_tip_name="b29tip",
            t_factor_root=0.9 * self.t_factor_root,
            t_factor_tip=0.9 * self.t_factor_tip,
            semi_span=self.w_semi_span / 2.5,
            sweep=self.sweep + 10,
            twist=0,
            position=self.h_tail_position,
            mesh_deflection=self.mesh_deflection
        )

    @Part
    def h_tail_left(self):
        return MirroredShape(shape_in=self.h_tail_right,
                             reference_point=self.position,
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=self.mesh_deflection)

    @Part
    def right_lifting_lg(self):
        return LiftingLandingGear(lg_foil_root_name = self.lg_foil_root_name,
                                  position=translate(self.lifting_lg_position, 'z', -self.boom_position_fraction_long*self.w_semi_span*2),
    lg_foil_tip_name = self.lg_foil_tip_name,
    lg_c_root = self.lg_c_root,
    lg_c_tip = self.lg_c_tip,
    lg_t_factor_root = self.lg_t_factor_root,
    lg_t_factor_tip = self.lg_t_factor_tip,
    lg_twist = self.lg_twist,
    mesh_deflection = self.mesh_deflection,
    lg_semi_span  = self.lg_semi_span)
    @Part
    def left_lifting_lg(self):
        return LiftingLandingGear(lg_foil_root_name = self.lg_foil_root_name,
                                  position=self.lifting_lg_position,
    lg_foil_tip_name = self.lg_foil_tip_name,
    lg_c_root = self.lg_c_root,
    lg_c_tip = self.lg_c_tip,
    lg_t_factor_root = self.lg_t_factor_root,
    lg_t_factor_tip = self.lg_t_factor_tip,
    lg_twist = self.lg_twist,
    mesh_deflection = self.mesh_deflection,
    lg_semi_span  = self.lg_semi_span)
    @Part
    def left_lg(self):
        return LandingGear(leg_radius = self.leg_radius,
                           position=self.left_lg_position,
        leg_height = self.leg_height,
        rubber_radius = self.rubber_radius)
    @Part
    def right_lg(self):
        return LandingGear(leg_radius = self.leg_radius,
                           position=translate(self.left_lg_position, 'y', -self.boom_position_fraction_long*self.w_semi_span*2),
        leg_height = self.leg_height,
        rubber_radius = self.rubber_radius)
    @Part
    def right_winglet(self):
        return Winglet(winglet_c_root = self.w_c_tip,
                       winglet_c_tip = self.winglet_c_tip,
                       winglet_sweep =self.sweep,
                       twist = self.twist,
                       position = rotate(translate(self.wing_tip_position, 'x', self.w_c_tip), 'z', radians(180)))






if __name__ == '__main__':
    from parapy.gui import display
    ac = Aircraft(label="aircraft",
                   fu_side=3.5,
                   #fu_sections=[10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 10],
                   fu_height = 5,
                  fu_distance = 40,
                   airfoil_root_name="b29root",
                   airfoil_tip_name="b29tip",
                   w_c_root=9., w_c_tip=2.3,
                   t_factor_root=1, t_factor_tip=1,
                   w_semi_span=35.,
                   sweep=25, twist=-5, wing_dihedral=0,
                   wing_position_fraction_long=0.4, wing_position_fraction_vrt=0.6,
                   vt_long=0.8, vt_taper=0.4, booms_radius=0.5,
                     booms_length=60,
                     booms_sections = [100, 100, 100, 100, 100],
                     mesh_deflection=0.0001)
    display(ac)