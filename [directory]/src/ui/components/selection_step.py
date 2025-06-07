from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from parapy.webgui import mui, plotly, viewer
from parapy.webgui.core import Component, State
from parapy.webgui.core.websocket.dispatchers import register_post_patch_action
from parapy.webgui.layout import FullParent, Margin, MarginBottom, Split
from ui.components.property_table import PropertyTable
from ui.store import STORE

if TYPE_CHECKING:
    from parapy.webgui.core.node import DiffStruct, NodeType
    from parapy.webgui.core.types import Event


class SelectionStep(Component):
    selected: Optional[int] = State(None)
    is_evaluating: bool = State(False)

    # Static columns used for a datagrid
    cols = [
        {"field": "id", "headerName": "ID", "width": 90},
        {
            "field": "height",
            "headerName": "Height",
            "description": "The height of the balloon excluding basket",
            "type": "number",
        },
        {
            "field": "radius",
            "headerName": "Radius",
            "description": "The maximum radius of the balloon",
            "type": "number",
        },
        {
            "field": "volume",
            "headerName": "Volume",
            "description": "Volume of the balloon",
            "type": "number",
        },
        {
            "field": "weight",
            "headerName": "Max weight",
            "description": "The maximum weight to be carried",
            "type": "number",
        },
        {
            "field": "cost",
            "headerName": "Cost",
            "description": "The cost of the balloon",
            "type": "money",
        },
    ]

    def datagrid_data(self):
        return [
            {
                "id": idx,
                "height": model.height,
                "radius": model.radius,
                "volume": model.volume,
                "weight": model.weight,
                "cost": model.cost,
            }
            for idx, model in enumerate(STORE.models)
        ]

    def create_data(self) -> None:
        STORE.create_models()
        self.is_evaluating = False

    def mount_node(self) -> DiffStruct:
        if not STORE.models:
            # We instruct the WebGUI to run a function after this Component
            # has been loaded. We do this so that the loading of the page is
            # not slowed down by this 'slow' function
            register_post_patch_action(self.create_data)
        return super().mount_node()

    def design_space_plot(self) -> NodeType:
        models = STORE.models
        selected = STORE.selected
        data = [
            {
                "x": [balloon.cost / 1000 for balloon in models],
                "y": [balloon.weight for balloon in models],
                "mode": "markers",
                "type": "scatter",
                "marker": {
                    "color": ["red" if b is selected else "blue" for b in models],
                    "size": [16 if b is selected else 8 for b in models],
                },
            }
        ]

        layout = {
            "xaxis": {"title": "Balloon cost [x1,000 $] ", "fixedrange": True},
            "yaxis": {"title": "Max weight [kg]", "fixedrange": True},
            "margin": {"t": 0},
        }
        config = {"displayModeBar": False, "responsive": True}

        return plotly.Plot(
            data=data,
            layout=layout,
            onClick=self.set_selected_from_plot,
            config=config,
            style={"height": "100%", "width": "100%"},
        )

    def set_selected(self, idx: int) -> None:
        self.set_state("selected", idx)
        STORE.selected = STORE.models[idx]

    def set_selected_from_plot(self, evt: Event) -> None:
        pts = evt["points"]
        if not pts:
            return
        idx = pts[0]["pointIndex"]
        self.set_selected(idx)

    def design_space_title(self) -> NodeType:
        return Split(v_align="center", weights=[1, 0, 0])[
            mui.Typography(variant="h5")["Design space"],
            mui.Tooltip(title="Reconfigure population")[
                mui.IconButton(
                    onClick=lambda evt: setattr(STORE, "step", STORE.step - 1)
                )[mui.Icon["arrow_back"]]
            ],
            mui.Tooltip(title="Regenerate population")[
                mui.IconButton(onClick=lambda evt: STORE.create_models())[
                    mui.Icon["cached_icon"]
                ]
            ],
        ]

    def design_space_datagrid(self) -> NodeType:
        selected = self.selected
        return FullParent[
            mui.DataGrid(
                columns=self.cols,
                rows=self.datagrid_data(),
                density="compact",
                rowSelectionModel=[selected],
                onRowSelectionModelChange=lambda v, evt: v and self.set_selected(v[0]),
            )
        ]

    def design_space(self) -> NodeType:
        return FullParent[
            mui.Paper[
                Margin[
                    Split(
                        orientation="vertical",
                        weights=[0, 1, 1],
                        height="100%",
                    )[
                        self.design_space_title(),
                        self.design_space_plot(),
                        self.design_space_datagrid(),
                    ]
                ]
            ]
        ]

    def select_design(self, *args: Any) -> None:
        STORE.final_design = STORE.selected
        STORE.step += 1

    def selected_data(self) -> NodeType:
        return [
            mui.Typography["Properties"],
            PropertyTable(model=STORE.selected),
            mui.Button(
                onClick=self.select_design,
                variant="contained",
                style={"alignSelf": "end", "marginTop": "auto"},
                endIcon=mui.Icon("send_icon"),
            )["Confirm design"],
        ]

    def inspector(self) -> NodeType:
        selected = STORE.selected
        return FullParent[
            mui.Paper[
                Margin[
                    Split(
                        orientation="vertical",
                        height="100%",
                        weights=[0, 1, 1],
                    )[
                        mui.Typography(variant="h5")["Selected design"],
                        viewer.Viewer(
                            objects=selected or [],
                            tessellation_config={"mesh_deflection": 0.01},
                        ),
                        self.selected_data()
                        if selected
                        else mui.Typography["Select a model to inspect its properties"],
                    ]
                ]
            ]
        ]

    def render(self) -> NodeType:
        return FullParent[
            mui.Container(maxWidth="xl")[
                MarginBottom("2em")[
                    Split(gap="2em", height="100%")[
                        self.design_space(),
                        self.inspector(),
                    ]
                ]
            ]
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(SelectionStep, reload=True)
