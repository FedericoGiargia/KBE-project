from parapy.geom import Cube

from parapy.webgui import layout, mui, viewer
from parapy.webgui.app_bar import AppBar
from parapy.webgui.core import Component, NodeType, State, VState

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


        ],

    def handle_change(self, evt, new_value, *args) -> None:
        self.value = new_value
        Aera.wing_dihedral = new_value


if __name__ == "__main__":
    from parapy.webgui.core import display
    display(App, reload=True)
