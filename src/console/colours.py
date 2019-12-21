# Defines some asciimatics colours
# Obtained from https://asciimatics.readthedocs.io/en/stable/io.html#colours
import random

# Colours
black = 0
red = 1
green = 2
yellow = 3
blue = 4
magenta = 5
cyan = 6
white = 7

def random_colour():
    return random.randint(0, 7)

# Attributes
bold = 1
normal = 2
reverse = 3
underline = 4