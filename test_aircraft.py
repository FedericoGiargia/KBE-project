#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 08:15:24 2025

Code to test the aircraft module, including a simple AVL analysis at cruise
conditions.

@author: aheidebrecht
"""

from parapy.gui import display
from aircraft import Aircraft

# Note: we're specifying cL "manually", but of course this could also
# be computed by the aircraft class based on user input, or computed
# by an Attribute in the Aircraft class (e.g.: c_L cruise based on aircraft
# mass and cruise condition)


ac = Aircraft(label="wing_Attempt",
              wing_location=0.42,
              wing_area=50,
              wing_aspect_ratio=4,
              wing_taper_ratio=0.8,
              wing_le_sweep=15,
              wing_twist=-10,
              wing_airfoil_name='23008',
              mach_cr=0.5,
              cl_cr=0.3,
              elevator_hinge=0.8
              )
display(ac)