import errors as e

vert = u'┃'
hort = u'━'
corns = [u'┏', u'┓', u'┗ ', u'┛']


# Use this class for useful drawing tools
class Drawtool():
    # Screen can be passed on init or via set_screen() method
    def __init__(self, screen=None):
        if screen:
            self.screen = screen

    # Write `text` to the screen at `(x, y)`.
    # For an explanation of the arguments, check this link:
    # https://asciimatics.readthedocs.io/en/stable/asciimatics.html#asciimatics.screen.Canvas.print_at
    def write(self, x, y, text, colour=7, attr=0, bg=0, transparent=False):
        self.screen.print_at(text, x, y, colour, attr, bg, transparent)

    # Draw a box at `(x, y)` `w` wide and `h` high. Used for drawing borders.
    def box(self, x, y, w_, h_):
        w = w_ - 1
        h = h_ - 1
        self.write(x, y, corns[0])
        self.write(x + w, y, corns[1])
        self.write(x, y + h, corns[2])
        self.write(x + w, y + h, corns[3])

        # vertical lines
        for x_ord in [x, x + w]:
            for i in range(y + 1, y + h):
                self.write(x_ord, i, vert)

        # horizontal lines
        for y_ord in [y, y + h]:
            for i in range(x + 1, x + w):
                self.write(i, y_ord, hort)

    def set_screen(self, s):
        self.screen = s
        return self


class Region:
    def __init__(self, border=True):
        self.has_border = border

    # Draw the border for this region. Will do this automatically if border=True is specified
    def border(self, s, orig, size):
        d = Drawtool(s)
        d.box(*orig, *size)

    # Render the region. region.draw() must be manually defined
    def render(self, s, orig, size):
        if self.has_border:
            self.border(s, orig, size)
            self.draw(s, (x + 1 for x in orig), (x - 2 for x in size))
        else:
            self.draw(s, orig, size)


class Window:
    def __init__(self, name, divs_x, divs_y):
        self.name = name
        self.divs = (divs_x, divs_y)
        self.regions = []

    # Add a region to the window in the `x`th column division and `y`th row division
    # 0 <= x < divs_x, and 0 <= y < divs_y
    def add_region(self, region, x, y, *, rowspan=1, colspan=1):
        # First, error checks. We have to make sure the given origin and dimensions is within the boundries
        if not (0 <= x < self.divs[0] and 0 <= y < self.divs[1]):
            raise e.RegionOutOfBoundsError(
                f"In {self.name} Window region was created at ({x}, {y}) while divisions are ({self.divs[0]}, {self.divs[1]})")
            return

        if not (0 < x + rowspan <= self.divs[0] and 0 < y + colspan <= self.divs[1]):
            raise e.RegionSpanOutOfBoundsError(
                f"In {self.name} Window region was created with span ({rowspan}, {colspan}) while divisions are ({self.divs[0]}, {self.divs[1]})")
            return

        # Give the region an instance of the window if it is needed
        region.window = self

        # Add the region to the windows region directory
        self.regions.append({
            "region": region,
            "div": (x, y),
            "span": (rowspan, colspan)
        })

    # Render all the regions defined in the window
    def render(self, s):
        for rd in self.regions:
            # Calculate its size dimension and origion position
            div_size = (s.width // self.divs[0], s.height // self.divs[1])

            size = (div_size[0] * rd['span'][0], div_size[1] * rd['span'][1])
            orig = (div_size[0] * rd['div'][0], div_size[1] * rd['div'][1])

            # Render the region!
            rd['region'].render(s, orig, size)

        # update the screen!
        s.refresh()
