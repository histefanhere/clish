from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError
import sys
from time import sleep, time

from constants import colours, keys
from canvas import Region, Window, Drawtool
from chats import Chat

dtools = Drawtool()

# interfaces = ["Discord", "Messenger"]
interfaces = {}


class topMenu(Region):
    def __init__(self):
        super().__init__("top region", border=True, selectable=False)

    def draw(self, s, orig, size, selected):
        dtools.print(*orig, "I am the top menu! Huzzah!")
        # dtools.print(*orig, "\t".join(interfaces), colour=colours.green)


class Entry_Region(Region):
    def __init__(self):
        super().__init__("Entry", show_name=True, ping_period=0.5)
        self.msg = ""
        self.eol_colour = 0
        self.cursor_pos = 0

    def draw(self, s, orig, size, selected):
        if self.msg == "":
            dtools.print(*orig, "Type your message here")
        else:
            dtools.print(*orig, " " * size[0])
            dtools.print(*orig, self.msg)
        if selected:
            dtools.highlight(orig[0] + self.cursor_pos, orig[1], 1, 1, bg=self.eol_colour)

    def key(self, s, key_code, selected):
        if selected:
            # Standard keyboard characters + numbers + symbols
            if keys.is_character(key_code):
                key = str(chr(key_code))
                self.msg += key
                self.cursor_pos += 1
                self.window.render(s, self)

            # Backspace
            elif key_code == keys.BACKSPACE:
                if len(self.msg) > 0:
                    self.msg = self.msg[:-1]
                    self.cursor_pos -= 1
                    self.window.render(s, self)

    def ping(self, s):
        self.eol_colour = (self.eol_colour + 7) % 14
        self.window.render(s, self)


class Debug_Region(Region):
    def __init__(self):
        super().__init__("Debug", show_name=True, ping_period=1, selectable=False)

        self.key_code = 0
        self.i = 0

    def draw(self, s, orig, size, selected):
        dtools.print(*orig, f"KEY CODE OF KEY PRESSED: {self.key_code}")
        dtools.print(orig[0], orig[1]+1, f"SECONDS: {self.i}")
        dtools.print(orig[0], orig[1]+2, f"SCREEN SIZE: {s.dimensions}")

    def key(self, s, key_code, selected):
        self.key_code = key_code
        self.window.render(s, self)

    def ping(self, s):
        self.i += 1
        self.window.render(s, self)

class List_Region(Region):
    def __init__(self):
        super().__init__("Interfaces", show_name=True)

        self.path = []
        self.cursor = 0

    def draw(self, s, orig, size, selected):
        # get the available options in the current path
        options = interfaces
        for dir_ in self.path:
            options = options[dir_]

        if len(self.path) == 0:
            dtools.print(*orig, "Home")
        else:
            # Prints the first and last thing here. Kinda weird, but saves us from re-writing the if statement.
            dtools.print(*orig, self.path[-1])
            dtools.print(orig[0], orig[1]+len(options)+2, "< Back")
        dtools.print(orig[0], orig[1]+1, "-"*size[0])

        for i, option in enumerate(options):
            string = option
            if not isinstance(options[option], Chat):
                string += " >"
            bg = colours.black
            if i == self.cursor:
                bg = colours.magenta
            dtools.print(orig[0], orig[1]+i+2, string, bg=bg)
    
    def key(self, s, key_code, selected):
        # get the available options in the current path
        options = interfaces
        for dir_ in self.path:
            options = options[dir_]

        if key_code in (keys.ARROW_DOWN, keys.ARROW_UP):
            direction = {keys.ARROW_DOWN: 1, keys.ARROW_UP: -1}[key_code]
            self.cursor = (self.cursor + direction) % len(options)

            self.window.render(s, self)
        
        elif key_code == keys.ARROW_RIGHT:
            self.path.append(list(options)[self.cursor])

            self.window.render(s, self)
        
        
            

interfaces['Discord'] = {
    "Direct Messages": {
        "coolguy": Chat()
    },
    "Servers": {
        "sidcobot": Chat()
    }
}
interfaces['Facebook'] = {
    "Direct Messages": {
        "josh123": Chat()
    },
    "Group Chats": {
        "amino propeino": Chat()
    }
}

def demo(s):
    s.clear()

    # Update the screen instance for drawing tools
    dtools.set_screen(s)

    # The window needs to re-calculate all the row and column dimensions
    main_window.set_screen(s)
    main_window.configure_row(0, height=3)
    main_window.configure_row(3, height=3)
    main_window.configure_column(1, weight=2)

    # Render the window onto the screen
    main_window.render(s)

    while True:
        if s.has_resized():
            raise ResizeScreenError("yes")

        event = s.get_event()
        if event:
            main_window.parse_event(s, event)
            s.refresh()

        # This will ping all the windows regions if needed, used for constantly refreshing regions
        main_window.ping(s)

# Create window here to allow data persistency
main_window = Window("CLISH", 3, 4)
main_window.add_region(topMenu(), 0, 0, colspan=3)
main_window.add_region(List_Region(), 0, 1, rowspan=3)
main_window.add_region(Region("region2"), 1, 1, rowspan=2)
main_window.add_region(Entry_Region(), 1, 3)
main_window.selected = 3
main_window.add_region(Region("region3"), 2, 1)
main_window.add_region(Debug_Region(), 2, 2, rowspan=2)

while True:
    try:
        Screen.wrapper(demo)
        sys.exit(0)
    except ResizeScreenError as e:
        pass
