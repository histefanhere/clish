from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError
import sys

from canvas import Window, Region, Drawtool

dtools = Drawtool()

main_window = Window("Main", 4, 1)


class Test_Region(Region):
    def __init__(self, name):
        super().__init__(name, border=True, show_name=True)

    def draw(self, s, orig, size):
        dtools.write(*orig, "Hello world!")


main_window.add_region(Test_Region("First Region"), 0, 0)
main_window.add_region(Test_Region("Second Region"), 1, 0, rowspan=3)


def demo(s):
    s.clear()

    # Update the screen instance for drawing tools
    dtools.set_screen(s)

    main_window.render(s)

    msg = ""
    s.refresh()
    while True:
        if s.has_resized():
            raise ResizeScreenError("yes")

        event = s.get_event()
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
