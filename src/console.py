from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError
import sys
from time import sleep

from constants import colours
from canvas import Region, Window, Drawtool

dtools = Drawtool()

interfaces = ["Discord", "Messenger"]

class Test_Region(Region):
    def __init__(self):
        super().__init__("region", border=True)

    def draw(self, s, orig, size, selected):
        dtools.write(*orig, "#")


class topMenu(Region):
    def __init__(self):
        super().__init__("top region", border=True)

    def draw(self, s, orig, size, selected):
        dtools.write(*orig, "\t".join(interfaces), colour=colours.green)

def demo(s):
    s.clear()

    # Update the screen instance for drawing tools
    dtools.set_screen(s)

    main_window = Window(s, "CLISH", 3, 3)

    main_window.configure_row(0, height=3)
    main_window.configure_row(2, height=3)
    main_window.configure_column(1, weight=2)
    main_window.add_region(topMenu(), 0, 0, rowspan=3)
    main_window.add_region(Test_Region(), 0, 1, colspan=2)
    main_window.add_region(Test_Region(), 1, 1)
    main_window.add_region(Test_Region(), 2, 1, colspan=2)
    main_window.add_region(Test_Region(), 1, 2)

    main_window.render(s)

    msg = ""
    s.refresh()
    while True:
        if s.has_resized():
            raise ResizeScreenError("yes")

        event = s.get_event()
        if event:
            main_window.parse_event(s, event)

        if isinstance(event, KeyboardEvent):
            dtools.write(0, 0, str(s.dimensions))
            key_code = event.key_code
            # key = str(chr(event.key_code))
            # msg += key
            if 32 <= key_code <= 126:
                key = str(chr(event.key_code))
                msg += key
            else:
                # button pressed isn't a character - e.g. Ctrl, Alt, Enter, Backspace, etc.
                pass
            dtools.write(1, s.height - 2, msg)

            s.refresh()


while True:
    try:
        Screen.wrapper(demo)
        sys.exit(0)
    except ResizeScreenError as e:
        pass
