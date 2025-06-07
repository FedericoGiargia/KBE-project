from __future__ import annotations

from typing import TYPE_CHECKING

from model.balloon import HotAirBalloon
from parapy.webgui import plotly
from parapy.webgui.core import Component, Prop

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class CostGraph(Component):
    model: HotAirBalloon = Prop()

    def render(self) -> NodeType:
        money_data = self.model.cost_revenue
        return plotly.Plot(
            data=[
                {
                    "x": [2022 + i for i in range(8)],
                    "y": [d[0] for d in money_data],
                    "type": "bar",
                    "text": [f"{round(d[0]/1000)}k$" for d in money_data],
                    "name": "Cost [$]",
                },
                {
                    "x": [2022 + i for i in range(8)],
                    "y": [d[1] for d in money_data],
                    "type": "bar",
                    "text": [f"{round(d[1]/1000)}k$" for d in money_data],
                    "name": "Revenue [$]",
                },
            ],
            layout={
                "title": "Cost/Revenue over time",
                "xaxis": {
                    "tickangle": -45,
                    "fixedrange": True,
                },
                "yaxis": {"fixedrange": True},
                "barmode": "group",
            },
            config={"displayModeBar": False},
        )


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(CostGraph(model=HotAirBalloon()), reload=True)
