from parapy.geom import Cube, Solid
import os
from parapy.webgui import layout, mui, viewer
from parapy.webgui.app_bar import AppBar
from parapy.webgui.core import Component, NodeType, State, VState, get_assets_dir, get_asset_url
from parapy.webgui.core.actions import download_file
from parapy.exchange import STEPWriter

from fede.convAera import Aircraft



Aera =  Aircraft(label="aircraft",
                   fu_side=3.5,
                   fu_height = 5,
                   fu_distance = 50,
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
                   mesh_deflection=0.01)



# Everything below is GUI


class App(Component):
    def render(self) -> NodeType:
        return (
            layout.Split(orientation='vertical',
                         height='100%',
                         weights=[0, 1]
                         )[
                AppBar(title="ConvAera"
                       ),
                layout.Split(height='100%',
                             weights=[0, 0, 1]
                             )[
                    InputsPanel,
                    mui.Divider(orientation='vertical'),
                    viewer.Viewer(objects=Aera,
                         style={'backgroundColor': 'gray'}
                                  ),
                ]
            ]
        )

class InputsPanel(Component):
    value = State(Aera.wing_dihedral)

    marks = [
        {
            'value': -10,
            'label': '-10°',
        },
        {
            'value': 0,
            'label': '0°',
        },
        {
            'value': 5,
            'label': '5°',
        },
        {
            'value': 10,
            'label': '10°',
        },
        {
            'value': 20,
            'label': '20°',
        },
    ]




    def render(self) -> NodeType:
        return layout.Box(orientation='vertical',
                          gap='1em',
                          style={'padding': '1em'})[
            layout.SlotFloatField(Aera, 'fu_distance', label='Length Fuselage'),
            layout.SlotFloatField(Aera, 'booms_length', label='Length Booms'),
            layout.SlotFloatField(Aera, 'sweep', label='Sweep'),
            mui.TextField(value=Aera.rotor_radius, label='Rotor Radius'),
            mui.Typography("Wing Dihedral (°)"),
            mui.Slider(value=self.value,
                       onChange=self.handle_change,
                       marks=self.marks,
                       min=-10,
                       max=20,
                       valueLabelDisplay='auto',
                       label='Wing Dihedral'),
            mui.Button(onClick=self.on_click, variant="outlined")["Update wing dihedral"],
            mui.Button(variant='contained',
                       onClick=self.download_step)["Download .STEP file"]


        ],

    def handle_change(self, evt, new_value, *args) -> None:
        self.value = new_value
        #Aera.wing_dihedral = new_value # If this line is active the model will update as soon as the slider is moved


    def on_click(self, evt):
        new_value = self.value
        Aera.wing_dihedral = new_value

    def download_step(self, evt):

        #'''
        writer = STEPWriter([Aera.fuselage.middle_fus,
                             Aera.left_wing, Aera.right_wing,
                             Aera.h_tail_left, Aera.h_tail_right,
                             Aera.left_boom, Aera.right_boom,
                             Aera.left_forward_propeller.rotor, Aera.left_forward_propeller.prop_blades,
                             Aera.right_forward_propeller.rotor, Aera.right_forward_propeller.prop_blades,
                             Aera.left_rear_propeller.rotor, Aera.left_rear_propeller.prop_blades,
                             Aera.right_rear_propeller.rotor, Aera.right_rear_propeller.prop_blades,

                             Aera.pushing_propeller.rotor, Aera.pushing_propeller.prop_blades,
                             Aera.left_lifting_lg, Aera.right_lifting_lg,


                             ])
        #'''

        # This second option looks at all the tree and outputs the writable objects
        writer2 = STEPWriter(
            trees=[Aera],  # <-- give it the top-level Base
            schema="AP214IS",  # optional, you can choose another STEP schema here
            unit="MM",  # optional, default is millimeters
            color_mode=True,  # optional, include colors
            layer_mode=True,  # optional, include layer info
            name_mode=True,  # optional, include names
        )


        print("Prop is a", type(Aera.fuselage.middle_fus))
        assets_dir = get_assets_dir()
        filename = os.path.join(assets_dir, 'convAera_solid.step')

        writer2.write(filename)
        url = get_asset_url(filename)
        download_file(url)




if __name__ == "__main__":
    from parapy.webgui.core import display
    '''
    Displays the application defined previously (App)
    reload ensures that all the changes can be seen in the webpage without re-establishing connections
    assets_dir is where all the generated files will be stored
    '''
    display(App, reload=True, assets_dir="C:/Users/Usuario/PycharmProjects/KBEProject/Global_KBE/fede/assets_convAera")

