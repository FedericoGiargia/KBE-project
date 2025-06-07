from __future__ import annotations

from typing import TYPE_CHECKING

from model.balloon import HotAirBalloon
from parapy.webgui import mui
from parapy.webgui.core import Component, Prop

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class PropertyTable(Component):
    model: HotAirBalloon = Prop()

    def render(self) -> NodeType:
        model = self.model
        return mui.TableContainer[
            mui.Table(size="small")[
                mui.TableRow[
                    mui.TableCell["Height"],
                    mui.TableCell(align="right")[round(model.height, ndigits=2)],
                    mui.TableCell["[m]"],
                ],
                mui.TableRow[
                    mui.TableCell["Radius"],
                    mui.TableCell(align="right")[round(model.radius, ndigits=2)],
                    mui.TableCell["[m]"],
                ],
                mui.TableRow[
                    mui.TableCell["Shape"],
                    mui.TableCell(align="right")[round(model.half_height, ndigits=2)],
                    mui.TableCell["[m]"],
                ],
                mui.TableRow[
                    mui.TableCell(style={"borderBottomWidth": "2px"})["Volume"],
                    mui.TableCell(style={"borderBottomWidth": "2px"}, align="right")[
                        round(model.volume, ndigits=2)
                    ],
                    mui.TableCell(style={"borderBottomWidth": "2px"})["[m]"],
                ],
                mui.TableRow[
                    mui.TableCell["Weight "],
                    mui.TableCell(align="right")[round(model.weight, ndigits=2)],
                    mui.TableCell["[kg]"],
                ],
                mui.TableRow[
                    mui.TableCell["Cost"],
                    mui.TableCell(align="right")[round(model.cost, ndigits=2)],
                    mui.TableCell["[$]"],
                ],
            ]
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(PropertyTable(model=HotAirBalloon()), reload=True)
