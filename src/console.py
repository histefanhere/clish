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
        dtools.print(*orig, "#")


class topMenu(Region):
    def __init__(self):
        super().__init__("top region", border=True)

    def draw(self, s, orig, size, selected):
        dtools.print(*orig, "\t".join(interfaces), colour=colours.green)


class Entry_Region(Region):
    def __init__(self):
        super().__init__("Entry", show_name=True)
        self.msg = ""

    def draw(self, s, orig, size, selected):
        if self.msg == "":
            dtools.print(*orig, "Type your message here")
        else:
            dtools.print(*orig, " " * size[0])
            dtools.print(*orig, self.msg)

    def key(self, s, key_code, selected):
        if selected:
            # Standard keyboard characters + numbers + symbols
            if 32 <= key_code <= 126:
                key = str(chr(key_code))
                self.msg += key

                self.window.render(s, self)

            elif key_code == -300:
                if len(self.msg) > 0:
                    self.msg = self.msg[:-1]
                    self.window.render(s, self)


class Debug_Region(Region):
    def __init__(self):
        super().__init__("Debug", show_name=True)

        self.key_code = 0

    def draw(self, s, orig, size, selected):
        dtools.print(*orig, f"Key code: {self.key_code}")

    def key(self, s, key_code, selected):
        self.key_code = key_code
        self.window.render(s, self)

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
    main_window.add_region(Debug_Region(), 1, 1)
    main_window.add_region(Entry_Region(), 1, 2)
    main_window.add_region(Test_Region(), 2, 1, colspan=2)

    main_window.render(s)

    msg = ""
    s.refresh()
    while True:
        if s.has_resized():
            raise ResizeScreenError("yes")

        event = s.get_event()
        if event:
            main_window.parse_event(s, event)
            s.refresh()


while True:
    try:
        Screen.wrapper(demo)
        sys.exit(0)
    except ResizeScreenError as e:
        pass
