from parapy.geom import Cube, Solid
import os
import glob
from parapy.webgui import layout, mui, viewer
from parapy.webgui.app_bar import AppBar
from parapy.webgui.core import Component, NodeType, State, VState, get_assets_dir, get_asset_url, display
from parapy.webgui.core.actions import download_file
from parapy.exchange import STEPWriter
from parapy.geom import GeomBase
from parapy.webgui.data_tree import DataTree
from wand.image import Image

from fede.convAera import Aircraft
from fede.convAVL import ConvAnalysis, AvlAnalysis
from fede.reporter import ReportConfig, create_pdf_report


# Instantiate Objects
Aera =  ConvAnalysis(label="aircraft",
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
                   mesh_deflection=0.01,
                   mach_list=[0.1])





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
                             weights=[2, 0, 3]
                             )[
                    layout.Split(orientation= 'vertical',
                                 height='100%',
                                 weights=[1, 0])[
                        layout.Split(height='100%',
                                     weights=[1, 0, 1])[
                            InputsPanelGeom,
                            mui.Divider(orientation='vertical'),
                            InputsPanelAVL

                        ],
                        mui.Box()[
                            ReportGenerator
                        ]

                    ],
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
CONTROLS = {}
MENU_ITEMS = {}
GROUPS = {}




class InputsPanelGeom(Component):
    value = State(Aera.wing_dihedral) # Initial value for a variable configuration
    download_start = State(False) # State of download for the popup
    download_finish = State(False)


    # These are the values for the slider dots
    marks = [
        {'value': -10, 'label': '-10°'},
        {'value': 0, 'label': '0°'},
        {'value': 5, 'label': '5°'},
        {'value': 10, 'label': '10°'},
        {'value': 20, 'label': '20°'},
    ]




    def render(self) -> NodeType:
        return layout.Box(orientation='vertical',
                          gap='1em',
                          style={'padding': '1em'})[
            layout.SlotFloatField(Aera, 'fu_distance', label='Length Fuselage'),
            layout.SlotFloatField(Aera, 'booms_length', label='Length Booms'),
            layout.SlotFloatField(Aera, 'sweep', label='Sweep'),
            mui.TextField(value=Aera.rotor_radius, label='Rotor Radius'),
            mui.Typography('Wing Dihedral (°)'),
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







class InputsPanelAVL(Component):

    process_start = State(False)
    process_running = State(False)
    process_finish = State(False)

    results = State(None) # Actual storage of the AVL analysis results
    results_items = State([]) # For the tree view
    l_over_d = State(None)

    def render(self) -> NodeType:
        return layout.Box(orientation='vertical',
                          gap='1em',
                          style={'padding': '1em'})[

            mui.Button(onClick=self.on_click_avl, variant="outlined")["Run AVL"],
            mui.Dialog(open=self.process_start)[
                mui.DialogTitle['AVL analysis done'],
                mui.DialogContent[
                    mui.DialogContentText['The AVL analysis has finished running. You can continue working']
                ],
                mui.DialogActions[
                    mui.Button(onClick=self.handle_close)['OK']
                ]
            ],


            mui.Typography("AVL Results"),
            mui.Paper(sx={'p': 2, 'maxHeight': '300px', 'overflow': 'auto'})[
                DataTree(
                    items=self.results_items,
                    controls={},
                    menuItems={},
                    groups={},
                )
            ],
            mui.TextField(value=self.l_over_d, label='L/D'),
            mui.Button(onClick=lambda evt: self.print_avl_results(), variant="outlined")["Print results in console"],
            layout.Split(orientation='horizontal')[
                mui.Button(onClick=self.show_geom_avl, variant="outlined")["Show geometry AVL"],
                mui.Button(onClick=self.save_geom_plot, variant="contained")["Save geometry AVL"]
            ],
            layout.Split(orientation='horizontal')[
                mui.Button(onClick=self.show_tref_avl, variant="outlined")["Show Trefftz plots"],
                mui.Button(onClick=self.save_tref_plot, variant="contained")["Save Trefftz plots"]
            ],
            viewer.Viewer(
                id="myViewer",
                objects=Aera,  # your Aircraft instance
                style={"backgroundColor": "gray"},
            )


        ]






    def handle_close(self, evt):
        self.process_finish = False
        self.process_start = False

    def on_click_avl(self, evt):
        #self.process_start = True
        att = Aera.avl_analyses[0]
        print("started")
        self.results = att.results
        self.l_over_d = round(att.l_over_d['fixed_aoa'],2)
        print((self.results.keys()))
        self.process_running = False
        self.results_items = self.build_results_items(self.results, name="results")

    def print_avl_results(self):
        """
        Pretty-print self.results, but when a value is a list longer than max_items
        show only the first max_items entries plus “...” and total count.
        """
        self.print_dict_tree(self.results, name="results")

    def show_geom_avl(self, evt):
        Aera.avl_analyses[0].show_geometry()

    def save_geom_plot(self, evt):

        Aera.avl_analyses[0].save_geometry_plot()

        ps_files = glob.glob(os.path.join(os.getcwd(), "*.ps"))


        assets = get_assets_dir()
        os.makedirs(assets, exist_ok=True)

        saved_jpegs = []
        for ps in ps_files:
            base = os.path.splitext(os.path.basename(ps))[0]
            jpeg_path = os.path.join(assets, base + ".jpeg")

            # Check if a file with the same name already exists
            if os.path.isfile(jpeg_path):
                os.remove(jpeg_path)

            # load + pad
            with Image(filename=ps, resolution=300) as img:


                # compute a margin
                w, h = img.width, img.height
                margin_factor = 0.1  # 20% of size
                mx = int(w * margin_factor)
                my = int(h * margin_factor)
                new_w = w + 2 * mx
                new_h = h + 2 * my

                with Image(width=new_w, height=new_h, background='white') as canvas:
                    canvas.composite(img, left=mx, top=my)
                    canvas.format = 'jpeg'
                    canvas.save(filename=jpeg_path)

            # remove the PS
            os.remove(ps)
            saved_jpegs.append(jpeg_path)


    def show_tref_avl(self, evt):
        Aera.avl_analyses[0].show_trefftz_plot()

    def save_tref_plot(self, evt):
        Aera.avl_analyses[0].save_trefftz_plot()
        ps_files = glob.glob(os.path.join(os.getcwd(), "*.ps"))



        # 3) prepare assets_dir
        assets = get_assets_dir()
        os.makedirs(assets, exist_ok=True)

        saved_jpegs = []
        for ps in ps_files:
            base = os.path.splitext(os.path.basename(ps))[0]
            jpeg_path = os.path.join(assets, base + ".jpeg")

            # Check if a file with the same name already exists
            if os.path.isfile(jpeg_path):
                os.remove(jpeg_path)


            # 4) load + pad
            with Image(filename=ps, resolution=300) as img:
                img.rotate(90)  # clockwise

                w, h = img.width, img.height


                with Image(width=w, height=h, background='white') as canvas:
                    canvas.composite(img)
                    canvas.format = 'jpeg'
                    canvas.save(filename=jpeg_path)


            os.remove(ps)
            saved_jpegs.append(jpeg_path)



    def print_dict_tree(self, d: dict, name: str = None, indent: int = 0):
        """Recursively print the structure of a nested dict,
        showing each dict’s name (if given) plus its children.

        - dicts show up as folders (with a trailing slash)
        - lists show up with their length
        - scalars show up with their type
        """
        # indent prefix
        prefix = "    " * indent

        # print this dict’s own name if provided
        if name is not None:
            print(f"{prefix}{name}/")
            indent += 1

        # now walk the contents
        for key, val in d.items():
            prefix = "    " * indent
            if isinstance(val, dict):
                # recurse, passing the key as the next dict's name
                self.print_dict_tree(val, name=str(key), indent=indent)
            elif isinstance(val, list):
                print(f"{prefix}{key}  [list of {len(val)}]")
            else:
                print(f"{prefix}{key}  [{type(val).__name__}]")

    def build_results_items(self, data, name=None, path=""):
        """
        Walk `data` (dict/list/scalar) and build a list of DataTree nodes.
        If `name` is given, we wrap everything under a single root node.
        """
        if name is not None:
            # wrap top-level under a single “results/” node
            root_id = path or name
            root = {"id": root_id, "label": f"{name}/", "children": []}
            for k, v in data.items():
                root["children"].append(self._build_node(v, key=str(k), parent_path=root_id))
            return [root]
        else:
            # unnamed top-level: list each key at root
            items = []
            for k, v in data.items():
                items.append(self._build_node(v, key=str(k), parent_path=path))
            return items

    def _build_node(self, val, key: str, parent_path: str):
        """
        Recursive helper:
        - dict   → node with children
        - list   → node with children per index
        - scalar → leaf node showing the actual value
        """
        node_id = f"{parent_path}/{key}"
        node = {"id": node_id}

        if isinstance(val, dict):
            node["label"] = f"{key}/"
            node["children"] = [
                self._build_node(v, key=str(k), parent_path=node_id)
                for k, v in val.items()
            ]

        elif isinstance(val, list):
            node["label"] = f"{key} [list of {len(val)}]"
            # make each list‐entry its own expandable node
            node["children"] = [
                self._build_node(item, key=str(i), parent_path=node_id)
                for i, item in enumerate(val)
            ]

        else:
            # leaf: show the actual value
            node["label"] = f"{key}: {val!r}"

        return node



class ReportGenerator(Component):




    def render(self) -> NodeType:
        return layout.Box(orientation='vertical',
                          gap='1em',
                          style={'padding': '1em'})[
            mui.Button(onClick=self.generate_report,
                       variant="contained"
                       )["Generate report"],

        ]

    def generate_report(self, evt):
        print("hello")

        # Check if the files are available for the report generation

        if not os.path.isfile(os.path.join('assets_convAera', 'm_1_geometry.jpg')):
            print("m_1_geometry.jpg not found in assets_convAera. Making plots.")
            self.save_geom_plot(evt)

        if not os.path.isfile(os.path.join('assets_convAera', 'm_1_geometry.jpg')):
            print("m_1_geometry.jpg not found in assets_convAera. Making plots")
            self.save_tref_plot(evt)

        if not os.path.isfile(os.path.join('assets_convAera', 'm_1_geometry.jpg')):
            print("m_1_geometry.jpg not found in assets_convAera. Computing results")
            Aera.avl_analyses[0].l_over_d()




    def save_geom_plot(self, evt):

        Aera.avl_analyses[0].save_geometry_plot()

        ps_files = glob.glob(os.path.join(os.getcwd(), "*.ps"))
        assets = get_assets_dir()
        os.makedirs(assets, exist_ok=True)

        saved_jpegs = []
        for ps in ps_files:
            base = os.path.splitext(os.path.basename(ps))[0]
            jpeg_path = os.path.join(assets, base + ".jpeg")

            if os.path.isfile(jpeg_path):
                os.remove(jpeg_path)

            with Image(filename=ps, resolution=300) as img:

                w, h = img.width, img.height
                margin_factor = 0.1  # 20% of size
                mx = int(w * margin_factor)
                my = int(h * margin_factor)
                new_w = w + 2 * mx
                new_h = h + 2 * my

                with Image(width=new_w, height=new_h, background='white') as canvas:
                    canvas.composite(img, left=mx, top=my)
                    canvas.format = 'jpeg'
                    canvas.save(filename=jpeg_path)

            os.remove(ps)
            saved_jpegs.append(jpeg_path)



    def save_tref_plot(self, evt):
        Aera.avl_analyses[0].save_trefftz_plot()
        ps_files = glob.glob(os.path.join(os.getcwd(), "*.ps"))

        assets = get_assets_dir()
        os.makedirs(assets, exist_ok=True)

        saved_jpegs = []
        for ps in ps_files:
            base = os.path.splitext(os.path.basename(ps))[0]
            jpeg_path = os.path.join(assets, base + ".jpeg")

            # Check if a file with the same name already exists
            if os.path.isfile(jpeg_path):
                os.remove(jpeg_path)

            with Image(filename=ps, resolution=300) as img:
                img.rotate(90)  # clockwise

                w, h = img.width, img.height

                with Image(width=w, height=h, background='white') as canvas:
                    canvas.composite(img)
                    canvas.format = 'jpeg'
                    canvas.save(filename=jpeg_path)

            os.remove(ps)
            saved_jpegs.append(jpeg_path)

    # File not found → do something




if __name__ == "__main__":
    from parapy.webgui.core import display
    '''
    Displays the application defined previously (App)
    reload ensures that all the changes can be seen in the webpage without re-establishing connections
    assets_dir is where all the generated files will be stored
    '''
    display(App, reload=True, assets_dir="C:/Users/Usuario/PycharmProjects/KBEProject/Global_KBE/fede/assets_convAera")

