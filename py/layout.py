import tkinter
import tkinter.font

from html import Text, Element

from constants import *

FONTS = {}

def get_font(family, size, weight, style):
    key = (family, size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            family = family,
            size = size, weight = weight, slant = style
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

class Layout:
    def __init__(self, tree, width):
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP + ADDRESSBAR_HEIGHT
        self.width = width
        self.center = False
        self.superscript = False
        self.pre = False
        self.smallcaps = False
        self.size = 16
        self.weight = "normal"
        self.style = "roman"
        self.family = "Times"
        self.line = []
        self.display_list = []

        self.recurse(tree)
        self.flush()

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()
        elif tag == "h1":
            self.center = True
        elif tag == "pre":
            self.pre = True
            self.family = "Courier New"

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "h1":
            self.flush()
            self.center = False
        elif tag == "pre":
            self.pre = False
            self.family = "Times"
            self.flush()

    def recurse(self, tree):
        if isinstance(tree, Text):
            if (self.pre):
                lines = tree.text.split("\n")
                for line in lines:
                    self.word(line)
                    self.flush()
            else:
                for word in tree.text.split():
                    self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    def word(self, word):
        font = get_font(self.family, self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > self.width - HSTEP:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        if self.center:
            x_offset = (self.width - self.cursor_x)/2
        else:
            x_offset = 0

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x + x_offset, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []
