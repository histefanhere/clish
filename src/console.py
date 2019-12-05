from asciimatics.screen import ManagedScreen


@ManagedScreen
def color_print(text=None, clr=None, screen=None):
    screen.refresh()
    screen.print_at(text, 0, 0)
