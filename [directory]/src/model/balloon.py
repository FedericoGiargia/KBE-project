from parapy.core import Attribute, Base, Input, Part, child
from parapy.geom import (
    VX,
    VZ,
    XOY,
    Box,
    BSplineCurve,
    Cylinder,
    GeomBase,
    Orientation,
    Point,
    Position,
    RevolvedSolid,
    RevolvedSurface,
)

"""Demo model used to generate a hot air balloon"""


class Basket(GeomBase):
    width: float = Input(1.5)
    length: float = Input(1.5)
    box_height: float = Input(1.5)
    rack_height: float = Input(1)

    @Attribute
    def height(self) -> float:
        return self.box_height + self.rack_height

    @Attribute
    def frame_dim(self) -> float:
        return self.width / 10

    @Part
    def box(self) -> Box:
        return Box(
            self.width,
            self.length,
            self.box_height,
            position=self.position.translate("z", self.box_height / 2),
            centered=True,
            color=(200, 200, 100),
        )

    @Attribute
    def attachment_point(self) -> list[Point]:
        z = self.box_height + self.rack_height
        y = self.length / 2 - 0.1 - self.frame_dim
        return [
            Point(0.5, y, z),
            Point(0.5, -y, z),
            Point(-0.5, y, z),
            Point(-0.5, -y, z),
        ]

    @Attribute
    def attachment_point_basket(self) -> list[Point]:
        z = self.box_height
        y = self.length / 2 - self.frame_dim
        return [
            Point(0.6, y, z),
            Point(0.6, -y, z),
            Point(-0.6, y, z),
            Point(-0.6, -y, z),
        ]

    @Attribute
    def vectors(self) -> list[Point]:
        apb = self.attachment_point_basket
        ap = self.attachment_point
        return [ap[i] - apb[i] for i in range(4)]

    @Part
    def rack(self) -> Cylinder:
        return Cylinder(
            radius=self.frame_dim * 0.75,
            height=self.vectors[child.index].length,
            quantify=4,
            position=Position(
                location=self.position.location
                + self.attachment_point_basket[child.index].vector,
                orientation=Orientation(
                    x=self.vectors[child.index].in_plane_orthogonal(VX),
                    z=self.vectors[child.index],
                ),
            ),
            centered=False,
            color="gray",
        )

    @Part
    def connectors(self) -> Box:
        return Box(
            quantify=2,
            width=1.4,
            length=self.frame_dim * 1.5,
            height=0.15,
            centered=True,
            position=self.position.translate(
                "z",
                self.height,
                "y",
                (child.index * 2 - 1) * (self.length / 2 - self.frame_dim * 1.5),
            ),
            color="gray",
        )

    @Part
    def burner(self) -> Box:
        return Box(
            self.frame_dim * 2,
            self.length - self.frame_dim,
            0.2,
            centered=True,
            position=self.position.translate("z", self.height),
            color="gray",
        )


class HotAirBalloon(Base):
    opening_radius: float = Input(0.5)
    radius: float = Input(5)
    half_height: float = Input(3)
    tube_height: float = Input(0.5)
    height: float = Input(10)
    basket_width: float = Input(2)
    basket_length: float = Input(2)
    rope_length: float = Input(2)

    @Attribute
    def curve(self) -> BSplineCurve:
        return BSplineCurve(
            control_points=[
                Point(self.opening_radius, 0, 0),
                Point(self.opening_radius, 0, self.tube_height),
                Point(self.radius, 0, self.half_height),
                Point(self.radius, 0, self.height),
                Point(0, 0, self.height),
            ]
        )

    @Part
    def balloon(self) -> RevolvedSurface:
        return RevolvedSurface(basis_curve=self.curve, center=Point(), direction=VZ)

    @Part
    def basket(self) -> Basket:
        return Basket(
            width=self.basket_width,
            length=self.basket_length,
            position=XOY.translate("z", -child.height - self.rope_length),
        )

    @Attribute
    def volume(self) -> RevolvedSolid:
        return RevolvedSolid(self.curve, center=Point(), direction=VZ).volume

    @Attribute
    def weight(self) -> float:
        return self.volume * 0.25

    @Attribute
    def cost(self) -> float:
        return (
            self.balloon.area * 500 * (self.half_height / 5 + 1)
            + self.basket.box.volume * 2000
        )

    @Attribute
    def cost_revenue(self) -> list[float]:
        weight = self.weight
        cost = self.cost
        return [(cost * (1 + i / 8), weight * 500 * (i + 1)) for i in range(8)]


if __name__ == "__main__":
    from parapy.webgui.layout import display_model_viewer

    display_model_viewer(HotAirBalloon())
