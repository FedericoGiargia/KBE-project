import os
from kbeutils.data import airfoils
from parapy.core.validate import AdaptedValidator


file_found = AdaptedValidator(lambda name: os.path.isfile(os.path.join(airfoils.__path__[0],
                                                                       name + ".dat")))
# This adapted validator checks if the file exists in the airfoils folder of kbeutils, avoiding
# crashes when the file is not found because of a wrong input.