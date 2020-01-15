ARROW_LEFT = -203
ARROW_UP = -204
ARROW_RIGHT = -205
ARROW_DOWN = -206

BACKSPACE = -300

def is_character(key_code):
    """ keyboard characters + numbers + symbols """
    return 32 <= key_code <= 126