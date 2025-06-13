from kbeutils import avl
from parapy.gui import display
from parapy.core import Input, Part, Attribute, child
from fede.convAera import Aircraft


class ConvAnalysis(Aircraft):
     # This class includes all the additional parameters
     # for the AVL analyis of the ConvAera Drone.


    alpha_avl: float = Input(3) # Angle of attack for the AVL analysis
    cl_fixed_avl: float = Input(0.3) # Cl of the whole aircraft
    aileron_deflection_avl: float = Input(5) # Degrees

    case_settings: list[tuple[str, dict]] = Input([('fixed_aoa', {'alpha': 3}),
                                                    ])
    mach_list: list[float] = Input([]) # List of Mach numbers for analysis

    @Part
    def avl_configurations(self):
        """Multiple configurations for each Mach number that is provided."""
        return avl.Configuration(quantify=len(self.mach_list),
                                 name='M_' + str(child.index + 1),
                                 reference_area=self.right_wing_planform_area*2,
                                 reference_span=self.w_semi_span*2,
                                 reference_chord=self.right_wing.mac,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.mach_list[child.index])


    @Attribute(in_tree=True)
    def avl_surfaces(self):  # a list of all AVL surfaces in the aircraft:
        return self.find_children(lambda o: isinstance(o, avl.Surface))


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

    @Attribute
    def total_lift(self):
        """Total lift of the convAera drone for each of the given maneuvers"""
        return {result['Name']: result['Totals']['CLtot']
                for case_name, result in self.results.items()}


if __name__ == '__main__':

    cases = [('fixed_aoa', {'alpha': 3}),  # aircraft flown at constant angle of attack
             ('fixed_cl', {'alpha': avl.Parameter(name='alpha', value=0.3, setting='CL')}),
             # aircraft is flown at a given Cl. AVL will find the necessary angle of attack
             ('trimmed', {'alpha': 3,  # aircraft is trimmed (Cm=0) at an angle of attack of 3
                          # degrees using the elevator
                          'elevator': avl.Parameter(name='elevator', value=0.0, setting='Cm')
                          }
              ),
             ('roll', {
                 'alpha': 3,
                 'aileron': avl.Parameter(name='aileron',
                                          value=5.0,
                                          setting='aileron')
                      }
              )
             ]

    ca = ConvAnalysis(label="aircraft",
                               fu_side=3.5,
                               fu_height=5,
                               fu_distance=50,
                               airfoil_root_name="b29root",
                               airfoil_tip_name="b29tip",
                               w_c_root=9., w_c_tip=2.3,
                               t_factor_root=1, t_factor_tip=1,
                               w_semi_span=35.,
                               sweep=25, twist=-5, wing_dihedral=0,
                               wing_position_fraction_long=0.4, wing_position_fraction_vrt=0.6,
                               vt_long=0.8, vt_taper=0.4, booms_radius=0.5,
                               booms_length=60,
                               booms_sections=[100, 100, 100, 100, 100],
                               mesh_deflection=0.01,
                               mach_list=[0.5, 0.3, 0.2],
                               case_settings=cases
                               )


    display(ca)