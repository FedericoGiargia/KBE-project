# this is the first test to set the functionality of parapy, nothing crazy
# to be expected, created starting from the fuselage file that they gave us


from parapy.geom import LoftedSolid, LoftedSurface, Circle, Vector, translate, Rectangle
from parapy.core import Input, Attribute, Part, child, widgets


class Fuselage(LoftedSolid):
    """Fuselage geometry, a loft through circles. I used this since we define
    the latest circle as being smaller, we can create a sort of supervelocity
    imposed in the first and last part. convex geometry


    Note the use of LoftedSolid as superclass. It means that every
    Fuselage instance defines a lofted geometry. A required input for LoftedSolid
    is a list of profiles, so either an @Attribute or a @Part sequence
    called "profiles" must be present in the body of the class. Use 'Display
    node' in the root node of the object tree to visualise the (yellow) loft
    in the GUI graphical viewer

    we can consider changing this part to something different, maybe not starting
    from lofted solids but from something else. I think this would be the best way
    of defining it since we can create every shape that we want.
    ideally, transform this from lofted cylinder to general lofted surface
    or to something more complicated I guess.


    note: pass down is used to see that the radius is what is used to define the
    fuselage at all stations. maybe changing to something else for example a square shape
    will help more


    Required inputs
    ---------------
    reference_radius: float.  we give a reference that is used to compute the other dims

        Fuselage radius in m
    length: float
        Fuselage length in m
    sections: list[float], optional
        radii of equally-spaced fuselage sections, in percent of `radius`.
        Number of entries determines number of fuselage sections created.
        Default: ``[10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 5]``

    mesh deflection: float, optional
        tolerance used for visual geometry display. Of the geometry and all
        components. Default is 1e-4
    color: str, optional
        color (as word, hex code).
        (overridden from parent class, uses a ColorPicker widget)

    ... plus all other inputs for ``parapy.geomLoftedSolid`` class

    Examples
    --------
        >>> obj = Fuselage(pass_down="fu_radius, fu_sections, fu_length",
        ...                    color="Green",
        ...                    mesh_deflection=0.0001
        ...                    )
    """

    #: fuselage radius
    #: :type: float
    width: float = Input(880)
    #: fuselage sections (percentage of nominal radius, at evenly-spaced stations)
    #: :type: collections.Sequence[float]
    sections: list[float] = Input([10, 90, 100, 100, 100, 100, 100, 100, 95, 70, 5])
    #: fuselage length (m)
    #: :type: float
    length: float = Input()

    mesh_deflection: float = Input(1e-3)  #change to have more precision

    # we're adding a colorpicker widget to the color Input:
    color = Input('blue', widget=widgets.ColorPicker)

    # In the same way, you can define drop-down menus, file pickers, checkboxes...
    # have a look at the documentation of parapy.core.widgets for more details

    @Attribute
    def section_radius(self) -> list[float]:
        """Section radius multiplied by the radius distribution
        through the length. Note that the numbers are percentages.

        Returns:
            List[float]: section radii in percentage along fuselage length
        """
        return [i * self.width / 100. for i in self.sections]

    @Attribute
    def section_length(self) -> float:
        """The section length is determined by dividing the fuselage
        length by the number of fuselage sections.

        Returns:
            float: length of each fuselage section
        """
        return self.length / (len(self.sections) - 1)

    # Required slot of the superclass LoftedSolid.
    # Originally, this is an Input slot, but any slot type is fine as long as it contains
    # an iterable of the profiles for the loft.
    @Part
    def profiles(self):
        return Rectangle(
            width=self.section_radius[child.index] * 2,  # Larghezza = diametro equivalente
            length=self.section_radius[child.index] * 2,  # Lunghezza = diametro (usa 'length' invece di 'height')
            position=translate(
                self.position.rotate90('y'),  # Allineamento come per i cerchi
                Vector(1, 0, 0),
                child.index * self.section_length
            ),
            color="Black",
            #centered=True  # Se il quadrato deve essere centrato nella posizione
        )
    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def fuselage_lofted(self):
        return LoftedSolid(profiles=self.profiles,
                           color="red",
                           mesh_deflection=self.mesh_deflection,
                           hidden=not (__name__ == '__main__'))
        # the `hidden` argument determines whether the part appears in the tree
        # The expression hides the Part unless this module is run directly (i.e. during testing!)
        # In "normal" use, this module will be imported, and then it won't clutter the tree
        # with all the redundant alternative ways to define the geometry


"""
    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def fuselage_lofted_ruled(self):
        return LoftedSolid(profiles=self.profiles,
                           color="green",
                           ruled=True,  # by default this is set to False
                           mesh_deflection=self.mesh_deflection,
                           hidden=not(__name__ == '__main__'))

    @Part  # This part is redundant since LoftedSolid is the superclass (it already _is_ a `LoftedSolid`).
    def fuselage_lofted_surf(self):
        return LoftedSurface(profiles=self.profiles,
                           color="blue",
                           mesh_deflection=self.mesh_deflection,
                           hidden=not(__name__ == '__main__'))

"""
if __name__ == '__main__':
    from parapy.gui import display

    fus = Fuselage(label="fuselage", radius=0.2, sections=[25, 50, 75, 100, 100, 100, 95, 70, 10], length=0.88,
                   mesh_deflection=0.0001)
    display(fus)
