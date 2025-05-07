#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 08:15:24 2025

Code which extends the aircraft module and adds the ability to run multiple
Analyses with AVL.

@author: aheidebrecht
"""
from kbeutils import avl
from parapy.gui import display
from parapy.core import Input, Part, Attribute, child

# Note how this works, even though the file containing the Aircraft class is
# called `assembly.py`? The secret is in the `__init__.py` file in the aircraft
# module
from aircraft import Aircraft


class AircraftWithAnalysis(Aircraft):
    # This class inherits from Aircraft and adds two parts
    # Not that they don't replace the existing AVL components that the Aircraft
    # class already has, but instead adds new ones.
    # So the single-point analysis at cruise conditions will still work ─ but
    # this extended class implements some of the same functionality in a
    # different way.

    case_settings: list[tuple[str, dict]] = Input()

    mach_list: list[float] = Input([]) # List of Mach numbers for analysis

    @Part
    def avl_configurations(self):
        """Multiple configurations for each Mach number that is provided."""
        return avl.Configuration(quantify=len(self.mach_list),
                                 name='M_' + str(child.index + 1),
                                 reference_area=self.wing   .planform_area,
                                 reference_span=self.wing.span,
                                 reference_chord=self.wing.mac,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.mach_list[child.index])


    @Part
    def avl_analyses(self):
        """There needs to be an analysis module for each configuration, which
        are defined by the number of analyzed Mach numbers, hence the need
        to use `quantify` here. Each analysis object has its own list of
        cases, too. In this case, they're all the same in this case. If we
        wanted, we could also provide different `case_settings` for each."""
        return AvlAnalysis(quantify=len(self.mach_list),
                           configuration=self.avl_configurations[child.index],
                           case_settings=self.case_settings,
                           label='Mach='+str(self.mach_list[child.index]))


class AvlAnalysis(avl.Interface):
    """ This classs handles the AVL analysis.
    Since it inherits from AVL, it already comes with most of the prerequisites
    included. All it needs is the configuration and the case settings.
    """

    configuration: avl.Configuration = Input()
    case_settings = Input()

    @Part
    def cases(self):
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])

    # the full set of results is accessible at self.results (inherited from avl.Interface, and visible as an attribute
    # to the root object, in the tree). The Attribute below just extracts some of them to make them easier to digest.
    @Attribute
    def l_over_d(self):
        """lift/drag ratio from AVL analysis. This is a dictionary of the L/D
        that results from each of the analyses, and not just a single value
        as provided by the aircraft class"""
        return {result['Name']: result['Totals']['CLtot'] / result['Totals']['CDtot']
                for case_name, result in self.results.items()}


if __name__ == '__main__':

    cases = [('fixed_aoa', {'alpha': 3}),  # aircraft flown at constant angle of attack
             ('fixed_cl', {'alpha': avl.Parameter(name='alpha', value=0.3, setting='CL')}),
             # aircraft is flown at a given Cl. AVL will find the necessary angle of attack
             ('trimmed', {'alpha': 3,  # aircraft is trimmed (Cm=0) at an angle of attack of 3
                          # degrees using the elevator
                          'elevator': avl.Parameter(name='elevator',
                                                    value=0.0,
                                                    setting='Cm')
                          }
              )
             ]

    aca = AircraftWithAnalysis(label="fast primi plane",
                                    fu_length=16,
                                    fu_slenderness=12,
                                    wing_location=0.42,
                                    wing_area=50,
                                    wing_aspect_ratio=2.5,
                                    wing_taper_ratio=0.2,
                                    wing_le_sweep=46,
                                    wing_twist=-5,
                                    wing_airfoil_name='35008',
                                    elevator_hinge=0.8,
                                    tail_area=8,
                                    tail_aspect_ratio=2,
                                    tail_taper_ratio=0.2,
                                    tail_airfoil_name='0012',
                                    rudder_hinge=0.6,
                                    mach_cr=0.5,
                                    cl_cr=0.3,
                                    mach_list=[0.11, 0.4, 0.8],
                                    case_settings=cases)  # the 3 cases above are configured to be processed by AVL on demand


    display(aca)