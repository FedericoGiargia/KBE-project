from parapy.geom import Cube, Solid
import os
from parapy.webgui import layout, mui, viewer
from parapy.webgui.app_bar import AppBar
from parapy.webgui.core import Component, NodeType, State, VState, get_assets_dir, get_asset_url, display
from parapy.webgui.core.actions import download_file
from parapy.exchange import STEPWriter
from parapy.geom import GeomBase
from parapy.webgui.data_tree import DataTree

from fede.convAera import Aircraft
from fede.convAVL import ConvAnalysis


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
                             weights=[0, 0, 0, 1, 0, 0]
                             )[
                    InputsPanel,
                    mui.Divider(orientation='vertical'),

                    mui.Paper(sx={'p': 2, 'width': '300px', 'overflow': 'auto', 'maxHeight': '100%'})[
                        DataTree(
                            items=ITEMS,
                            controls=CONTROLS,
                            menuItems=MENU_ITEMS,
                            groups=GROUPS,
                        )
                    ],
                    viewer.Viewer(objects=Aera,
                                  style={'backgroundColor': 'gray'}
                                  ),
                    mui.Divider(orientation='vertical'),
                    viewer.Viewer(objects=Aera, style={'backgroundColor': 'gray'})

                ]
            ]
        )

# Tree view builder

def build_data_items(obj: GeomBase, visited=None):
    if visited is None:
        visited = set()
    obj_id = id(obj)
    # Prevent infinite loops
    if obj_id in visited:
        # Fallback label when .label is None
        base_label = getattr(obj, 'label', None) or obj.__class__.__name__
        return {'id': str(obj_id), 'label': f"{base_label} (cycle)"}

    visited.add(obj_id)
    # Determine label, fallback to class name if None
    base_label = getattr(obj, 'label', None) or obj.__class__.__name__
    item = {'id': str(obj_id), 'label': base_label}

    # Use children property (parapy Base.children)
    children = []
    for child in getattr(obj, 'children', []):
        if isinstance(child, GeomBase):
            children.append(child)

    if children:
        # Recursively build child entries
        item['children'] = [build_data_items(child, visited) for child in children]
    return item

# Prepare tree data
ITEMS = [build_data_items(Aera)]
# Optionally define these dicts for per-item controls/menus/groups
CONTROLS = {}
MENU_ITEMS = {}
GROUPS = {}





class InputsPanel(Component):
    value = State(Aera.wing_dihedral) # Initial value for a variable configuration
    download_start = State(False) # State of download for the popup
    download_finish = State(False)


    # These are the values for the slider dots
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
                       onClick=self.download_step)["Download .STEP file"],
            mui.Dialog(open=self.download_start)[
                mui.DialogTitle['Downloading'],
                mui.DialogContent[
                    mui.DialogContentText['Writing parts to STEP file.']
                ]
            ],
            mui.Dialog(open=self.download_finish)[
                mui.DialogTitle['Finished Downloading'],
                mui.DialogContent[
                    mui.DialogContentText[f'All the parts have been written to the step file and downloaded to: {get_assets_dir()}']
                ],
                mui.DialogActions[
                    mui.Button(onClick=self.handle_close)['OK']
                ]
            ],
            viewer.Viewer(
                id="myViewer",
                objects=Aera,  # your Aircraft instance
                style={"backgroundColor": "gray"},
            )


        ]




    def handle_change(self, evt, new_value, *args) -> None:
        self.value = new_value
        #Aera.wing_dihedral = new_value # If this line is active the model will update as soon as the slider is moved


    def on_click(self, evt):
        new_value = self.value
        Aera.wing_dihedral = new_value

    def download_step(self, evt):

        '''
        Reads the tree from Aera, writes all the parts into a STEP file and then downloads
        to assets folder.
        '''
        self.download_start = True
        print("downloading")

        Aera.mesh_deflection = 0.0001

        # This second option looks at all the tree and outputs the writable objects
        writer = STEPWriter(
            trees=[Aera],  # <-- give it the top-level Base
            schema="AP214IS",  # optional, you can choose another STEP schema here
            unit="MM",  # optional, default is millimeters
            color_mode=False,  # optional, include colors
            layer_mode=True,  # optional, include layer info
            name_mode=True,  # optional, include names
        )

        print("Prop is a", type(Aera.fuselage.middle_fus))
        assets_dir = get_assets_dir()
        filename = os.path.join(assets_dir, 'convAera_solid.step')

        writer.write(filename)
        url = get_asset_url(filename)
        download_file(url)
        Aera.mesh_deflection = 0.01
        self.download_start = False
        self.download_finish = True
        print("Download complete")


    def handle_close(self, evt):
        self.download_finish = False




if __name__ == "__main__":
    from parapy.webgui.core import display
    '''
    Displays the application defined previously (App)
    reload ensures that all the changes can be seen in the webpage without re-establishing connections
    assets_dir is where all the generated files will be stored
    '''
    display(App, reload=True, assets_dir="C:/Users/Usuario/PycharmProjects/KBEProject/Global_KBE/fede/assets_convAera")

