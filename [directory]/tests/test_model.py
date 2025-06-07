import pytest
from model.balloon import HotAirBalloon

def test_balloon_volume():
    balloon = HotAirBalloon()

    assert balloon.volume == pytest.approx(381.8226640972622)
    balloon.height = 12
    assert balloon.volume == pytest.approx(470.7370494173471)