from asciimatics.event import KeyboardEvent
import time

from constants import errors as e
from constants import colours

vert = u'┃'
hort = u'━'
corns = [u'┏', u'┓', u'┗ ', u'┛']
inters = [u'┫', u'┻', u'┳', u'┣']

# Use this class for useful drawing tools
class Drawtool():
    # Screen can be passed on init or via set_screen() method
    def __init__(self, screen=None):
        if screen:
            self.screen = screen

    # Write `text` to the screen at `(x, y)`.
    # For an explanation of the arguments, check this link:
    # https://asciimatics.readthedocs.io/en/stable/asciimatics.html#asciimatics.screen.Canvas.print_at
    def print(self, x, y, text, colour=7, attr=0, bg=0, transparent=False):
        self.screen.print_at(text, x, y, colour, attr, bg, transparent)

    # Draw a box at `(x, y)` `w` wide and `h` high. Used for drawing borders.
    def box(self, x, y, w_, h_, **kwargs):
        w = w_ - 1
        h = h_ - 1
        self.print(x, y, corns[0], **kwargs)
        self.print(x + w, y, corns[1], **kwargs)
        self.print(x, y + h, corns[2], **kwargs)
        self.print(x + w, y + h, corns[3], **kwargs)

        # vertical lines
        for x_ord in [x, x + w]:
            for i in range(y + 1, y + h):
                self.print(x_ord, i, vert, **kwargs)

        # horizontal lines
        for y_ord in [y, y + h]:
            for i in range(x + 1, x + w):
                self.print(i, y_ord, hort, **kwargs)

    def highlight(self, x, y, w, h, **kwargs):
        self.screen.highlight(x, y, w, h, **kwargs)

    def set_screen(self, s):
        self.screen = s
        return self


class Region:
    def __init__(self, name, border=True, show_name=False, ping_period=None):
        self.name = name
        self.has_border = border
        self.show_name = show_name
        self.ping_period = ping_period

    # Draw the border for this region. Will do this automatically if border=True is specified
    def border(self, s, orig, size, **kwargs):
        d = Drawtool(s)
        d.box(*orig, *size, **kwargs)
        if self.show_name:
            # Render the name of the region in the border
            Drawtool(s).print(orig[0]+2, orig[1], f"{inters[0]}{self.name}{inters[3]}")

    # Render the region. region.draw() must be manually defined
    def render(self, s, orig, size, selected):
        if self.has_border:
            self.border(s, orig, size, colour=colours.white if selected else colours.cyan)
            self.draw(s, tuple(x + 1 for x in orig), tuple(x - 2 for x in size), selected)
        else:
            self.draw(s, orig, size, selected)

    def draw(self, *args, **kwargs):
        raise e.AbstractMethodNotImplementedError(f"Region does not have a draw() method specified")

    # Should be manually defined if this is desired
    def key(self, s, key_code, selected):
        pass

    def ping(self, s):
        pass

class Window:
    def __init__(self, s, name, divs_x, divs_y):
        self.s = s
        self.width = s.width
        self.height = s.height
        self.name = name
        self.divs = (divs_x, divs_y)
        self.regions = []
        # The first region to be added to the window is the selected one
        self.selected = 0

        # Widths/heights of the columns\rows, respectivley.
        self.columns = list([{"type":"auto", "value": s.width // self.divs[0]} for x in range(divs_x)])
        self.rows = list([{"type":"auto", "value": s.height // self.divs[1]} for x in range(divs_y)])

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
            "span": (rowspan, colspan),
            "selected": True if len(self.regions) == 0 else False,
        })
        if region.ping_period:
            self.regions[-1]['ping_period'] = region.ping_period
            self.regions[-1]['last_ping'] = time.time()

        # Return self for easy chaining
        return self

    # Render all the regions defined in the window
    # Or just a specific region if `region` is specified
    def render(self, s, region=None):
        def calc_and_render(rd):
            # Calculate its size dimension and origin position
            # div_size = (s.width // self.divs[0], s.height // self.divs[1])

            # size = (div_size[0] * rd['span'][0], div_size[1] * rd['span'][1])
            # orig = (div_size[0] * rd['div'][0], div_size[1] * rd['div'][1])

            # yikes.
            size = (
                sum(map(lambda n: self.columns[n]['value'], range(rd['div'][0], rd['div'][0] + rd['span'][0]))),
                sum(map(lambda n: self.rows[n]['value'], range(rd['div'][1], rd['div'][1] + rd['span'][1])))
            )
            orig = (
                sum(map(lambda n: self.columns[n]['value'], range(0, rd['div'][0]))),
                sum(map(lambda n: self.rows[n]['value'], range(0, rd['div'][1])))
            )

            # Render the region!
            rd['region'].render(s, orig, size, rd['selected'])

        if region:
            rd = region
            if isinstance(region, Region):
                for r in self.regions:
                    if r['region'] == region:
                        rd = r
                        break
                else:
                    raise Exception("Region not found")

            calc_and_render(rd)

            s.refresh()
            return

        for rd in self.regions:
            calc_and_render(rd)

        # update the screen!
        s.refresh()

    def parse_event(self, s, event):
        if isinstance(event, KeyboardEvent):
            key_code = event.key_code

            for rd in self.regions:
                rd['region'].key(s, key_code, rd['selected'])

            # -301 is TAB, -302 is SHIFT + TAB
            if key_code in (-301, -302):
                # We need to re-render the currently selected region, and the next
                self.regions[self.selected]['selected'] = False
                self.render(s, self.regions[self.selected])

                diff = 1
                if key_code == -302:
                    diff = -1
                self.selected = (self.selected + diff) % len(self.regions)

                self.regions[self.selected]['selected'] = True
                self.render(s, self.regions[self.selected])

                s.refresh()

    # Set the height of a row to a certain height
    def configure_row(self, n, *, height=None, weight=None):
        if not (0 <= n < len(self.rows)):
            raise errors.OutOfBoundsError(f"Attempted to configure row {n}, which is out of the range 0 to {len(self.rows)-1}")
            return

        if height:
            self.rows[n] = {
                "type": "fixed",
                "value": height
            }
        elif weight:
            self.rows[n] = {
                "type": "heavy",
                "weight": weight
            }

        # Get amount of auto rows
        def is_auto(t):
            if t['type'] == "auto":
                return 1
            else:
                return 0
        # amount = sum(map(is_auto, self.rows))
        amount = len([x for x in self.rows if x['type'] == 'auto'])
        amount += sum(map(lambda x: x['weight'], [x for x in self.rows if x['type'] == "heavy"]))

        auto_height = self.height - sum([x['value'] for x in self.rows if x['type'] == "fixed"])
        self.auto_height = auto_height
        # Convert rows. if a row is auto, set its hight to a factor of the remaining space
        new_rows = []
        for row in self.rows:
            if is_auto(row):
                new_rows.append({
                    "type": "auto",
                    "value": auto_height // amount
                })
            elif row['type'] == 'heavy':
                new_rows.append({
                    "type": "heavy",
                    "weight": row['weight'],
                    "value": auto_height // amount * row['weight']
                })
            else:
                new_rows.append(row)
        self.rows = new_rows

        # Return self for easy chaining
        return self


    # Set the width of a column to a certain width
    def configure_column(self, n, *, width=None, weight=None):
        if not (0 <= n < len(self.columns)):
            raise errors.OutOfBoundsError(f"Attempted to configure row {n}, which is out of the range 0 to {len(self.columns)-1}")
            return

        if width:
            self.columns[n] = {
                "type": "fixed",
                "value": width
            }
        elif weight:
            self.columns[n] = {
                "type": "heavy",
                "weight": weight
            }

        # Get amount of auto rows
        def is_auto(t):
            if t['type'] == "auto":
                return 1
            else:
                return 0
        # amount = sum(map(is_auto, self.rows))
        amount = len([x for x in self.columns if x['type'] == 'auto'])
        amount += sum(map(lambda x: x['weight'], [x for x in self.columns if x['type'] == "heavy"]))

        auto_width = self.width - sum([x['value'] for x in self.columns if x['type'] == "fixed"])
        # Convert rows. if a row is auto, set its hight to a factor of the remaining space
        new_columns = []
        for column in self.columns:
            if column['type'] == 'auto':
                new_columns.append({
                    "type": "auto",
                    "value": auto_width // amount
                })
            elif column['type'] == 'heavy':
                new_columns.append({
                    "type": "heavy",
                    "weight": column['weight'],
                    "value": auto_width // amount * column['weight']
                })
            else:
                new_columns.append(column)
        self.columns = new_columns

        # Return self for easy chaining
        return self

    def ping(self, s):
        for rd in self.regions:
            if 'ping_period' in rd:
                if rd['last_ping'] + rd['ping_period'] < time.time():
                    rd['last_ping'] = time.time()
                    rd['region'].ping(s)

