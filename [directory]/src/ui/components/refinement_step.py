from __future__ import annotations

from typing import TYPE_CHECKING

from parapy.webgui import mui, plotly, viewer
from parapy.webgui.core import Component, State
from parapy.webgui.layout import Box, Margin, SlotFloatField
from ui.components.cost_graph import CostGraph
from ui.store import STORE

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class RefinementStep(Component):
    inspect_open: bool = State(False)

    def configuration_panel(self) -> NodeType:
        model = STORE.final_design
        options = [
            SlotFloatField(model, "height", label="Height [m]"),
            SlotFloatField(model, "radius", label="Radius [m]"),
            SlotFloatField(model, "opening_radius", label="Opening radius [m]"),
            SlotFloatField(model, "half_height", label="Shape height [m]"),
            SlotFloatField(model, "tube_height", label="Tube height [m]"),
            SlotFloatField(model, "basket_width", label="Basket width [m]"),
            SlotFloatField(model, "basket_length", label="Basket length [m]"),
            SlotFloatField(model, "rope_length", label="Rope length"),
        ]
        return mui.Accordion(
            defaultExpanded=True,
            disableGutters=True,
            style={"position": "absolute", "top": "3em", "left": "3em"},
        )[
            mui.AccordionSummary(expandIcon=mui.Icon("expand_more_icon"))[
                mui.Typography["Balloon configuration"]
            ],
            mui.AccordionDetails[Box(orientation="vertical", gap="1em")[options]],
        ]

    def plots(self) -> NodeType:
        model = STORE.final_design

        contour_points = [model.curve.point(i / 9) for i in range(10)]

        return [
            plotly.Plot(
                data=[
                    {
                        "x": [p.x for p in contour_points],
                        "y": [p.z for p in contour_points],
                        "mode": "lines+markers",
                        "line": {"shape": "spline"},
                        "type": "scatter",
                    }
                ],
                layout={
                    "title": "Balloon profile",
                    "xaxis": {"title": "Radius [m]", "fixedrange": True},
                    "yaxis": {"title": "Height [m]", "fixedrange": True},
                },
                config={"displayModeBar": False},
            ),
            CostGraph(model=STORE.final_design),
        ]

    def inspection_panel(self) -> NodeType:
        return mui.Backdrop(
            open=self.inspect_open,
            onClick=lambda evt: self.set_state("inspect_open", False),
        )[
            mui.Paper(className="inspection-container")[
                Margin[
                    Box(orientation="vertical")[
                        Box[
                            mui.Typography(variant="h4")["Balloon performance"],
                            mui.IconButton(
                                style={"marginLeft": "auto"},
                                onClick=lambda evt: self.set_state(
                                    "inspect_open", False
                                ),
                            )[mui.Icon("close_icon")],
                        ],
                        Box[
                            self.plots()
                            if self.inspect_open
                            else mui.CircularProgress()
                        ],
                    ]
                ]
            ]
        ]

    def render(self) -> NodeType:
        return Box(height="100%", style={"position": "relative"})[
            viewer.Viewer(
                objects=STORE.final_design,
                tessellation_config={"mesh_deflection": 0.01},
            ),
            self.configuration_panel(),
            self.inspection_panel(),
            mui.Tooltip(title="Back to design selection")[
                mui.Fab(
                    style={
                        "position": "absolute",
                        "left": "3em",
                        "bottom": "3em",
                    },
                    color="primary",
                    onClick=lambda evt: setattr(STORE, "step", STORE.step - 1),
                )[mui.Icon("arrow_back_icon")]
            ],
            mui.Tooltip(title="Inspect performance")[
                mui.Fab(
                    style={
                        "position": "absolute",
                        "right": "3em",
                        "bottom": "9em",
                    },
                    color="secondary",
                    onClick=lambda evt: self.set_state("inspect_open", True),
                )[
                    mui.Icon["equalizer_icon"],
                ]
            ],
            mui.Tooltip(title="Submit design")[
                mui.Fab(
                    style={
                        "position": "absolute",
                        "right": "3em",
                        "bottom": "3em",
                    },
                    color="primary",
                    onClick=lambda evt: setattr(STORE, "step", STORE.step + 1),
                )[mui.Icon("send_icon")]
            ],
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(RefinementStep, reload=True)
