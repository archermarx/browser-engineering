import tkinter
import tkinter.font

from html import Text, Tag

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
    def __init__(self, tokens, width):
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP + ADDRESSBAR_HEIGHT
        self.width = width
        self.center = False
        self.superscript = False
        self.pre = False
        self.size = 16
        self.weight = "normal"
        self.style = "roman"
        self.family = "Times"
        self.line = []
        self.display_list = []

        for tok in tokens:
            self.token(tok)

        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            if (self.pre):
                lines = tok.text.split("\n")
                for line in lines:
                    self.word(line)
                    self.flush()
            else:
                for word in tok.text.split():
                    self.word(word)

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br" or tok.tag == "/br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        elif tok.tag == 'h1 class="title"':
            self.center = True
        elif tok.tag == "/h1":
            self.flush()
            self.center = False
        elif tok.tag == "sup":
            self.size = int(self.size/2)
            self.superscript = True
        elif tok.tag == "/sup":
            self.size *= 2
            self.superscript = False
        elif tok.tag.startswith("pre"):
            self.pre = True
            self.family = "Courier New"
        elif tok.tag == "/pre":
            self.pre = False
            self.family = "Times"
            self.flush()

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
