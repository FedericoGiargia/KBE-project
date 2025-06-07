from random import random

from model.balloon import HotAirBalloon
from parapy.core import Base, Input, MutableSequence, Part

DEFAULT_STEP = 0
DEFAULT_POPULATION_SIZE = 100
DEFAULT_HEIGHT = [8, 12]
DEFAULT_RADIUS = [4, 6]
DEFAULT_SHAPE = [1, 4]
DEFAULT_COLOR = "red"


class Store(Base):
    # Initialization/ configuration
    pop_size: int = Input(DEFAULT_POPULATION_SIZE)
    height: list[float] = Input(DEFAULT_HEIGHT)
    radius: list[float] = Input(DEFAULT_RADIUS)
    shape: list[float] = Input(DEFAULT_SHAPE)
    color: str = Input(DEFAULT_COLOR)

    # App state
    step: int = Input(DEFAULT_STEP)
    selected: HotAirBalloon = Input(None)
    final_design: HotAirBalloon = Input(None)

    @Part
    def models(self) -> MutableSequence:
        return MutableSequence(type=HotAirBalloon, quantify=0)

    def create_models(self) -> None:
        r1 = self.radius[0]
        r2 = self.radius[1] - r1
        h1 = self.height[0]
        h2 = self.height[1] - h1
        s1 = self.shape[0]
        s2 = self.shape[1] - s1
        for _ in range(self.pop_size):
            self.models.append(
                HotAirBalloon(
                    radius=random() * r2 + r1,
                    height=random() * h2 + h1,
                    half_height=random() * s2 + s1,
                    color=self.color,
                )
            )

    def reset(self, hard: bool = True) -> None:
        if hard:
            self.pop_size = DEFAULT_POPULATION_SIZE
            self.height = DEFAULT_HEIGHT
            self.radius = DEFAULT_RADIUS
            self.shape = DEFAULT_SHAPE
            self.color = DEFAULT_COLOR

        self.step = DEFAULT_STEP
        self.selected = None
        self.final_design = None
        [self.models.pop() for _ in range(len(self.models))]


STORE = Store()
