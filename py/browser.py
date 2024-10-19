import tkinter
import tkinter.font
from url import URL
from html import lex, Text, Tag, print_tokens
import platform
import os

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
SCROLL_SPEED = 2
HSTEP, VSTEP = 13, 18
ADDRESSBAR_HEIGHT = 1.25 * VSTEP
SCROLLBAR_WIDTH = HSTEP
SCROLLBAR_OFFSET = 5

class Layout:
    def __init__(self, tokens, width):
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP + ADDRESSBAR_HEIGHT
        self.width = width
        self.size = 16
        self.weight = "normal"
        self.style = "roman"
        self.display_list = []

        for tok in tokens:
            self.token(tok)

    def token(self, tok):
        if isinstance(tok, Text):
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

    def word(self, word):
        font = tkinter.font.Font(
            size=self.size,
            weight=self.weight,
            slant=self.style,
        )
        w = font.measure(word)
        h = font.metrics("linespace") * 1.25
        if self.cursor_x + w > self.width - HSTEP:
            self.cursor_y += h
            self.cursor_x = HSTEP
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(" ")


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width = WIDTH,
            height = HEIGHT,
        )
        self.canvas.width = WIDTH
        self.canvas.height = HEIGHT
        self.canvas.pack(fill = tkinter.BOTH, expand = 1)
        self.scroll = 0
        self.max_scroll = 0
        self.bottom_margin = 5*VSTEP
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.resize)
        self.detect_platform()
        self.current_url = "about:blank"

    def update_layout(self):
        screen_width = self.canvas.width - HSTEP - SCROLLBAR_WIDTH - SCROLLBAR_OFFSET
        self.display_list = Layout(self.tokens, screen_width).display_list

    def resize(self, e):
        self.canvas.width = e.width
        self.canvas.height = e.height
        self.update_layout()
        self.draw()

    def detect_platform(self):
        os = platform.system()
        MAC_SCROLL_DELTA = -1
        WINDOWS_SCROLL_DELTA = 120
        self.scroll_speed = 2

        if os == "Darwin":
            self.scroll_speed = self.scroll_speed / MAC_SCROLL_DELTA
            self.window.bind("<MouseWheel>", self.scrollwheel)
        elif os == "Windows":
            self.scroll_speed = self.scroll_speed / WINDOWS_SCROLL_DELTA
            self.window.bind("<MouseWheel>", self.scrollwheel)
        elif os == "Linux":
            self.scroll_speed = 1
            self.window.bind("<Button-4>", self.scrollup)
            self.window.bind("<Button-5>", self.scrolldown)

    def scrollup(self, e):
        self.scroll = self.scroll - SCROLL_STEP
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollwheel(self, e):
        self.scroll += self.scroll_speed * e.delta 
        self.draw()

    def draw_addressbar(self):
        self.canvas.create_rectangle(
            0, 0, self.canvas.width, ADDRESSBAR_HEIGHT, fill = "white"
        )
        self.canvas.create_text(HSTEP, VSTEP/4, text = self.current_url, anchor = "nw")
        

    def draw_scrollbar(self):
        halfwidth = 0.5 * SCROLLBAR_WIDTH
        scrollbar_x = self.canvas.width - halfwidth - SCROLLBAR_OFFSET
        scrollbar_y = ADDRESSBAR_HEIGHT

        screen_height = self.canvas.height - ADDRESSBAR_HEIGHT
        scroll_height = screen_height / self.max_scroll * screen_height
        scroll_pos = scrollbar_y + self.scroll / self.max_scroll * (screen_height - scroll_height)

        self.canvas.create_rectangle(
            scrollbar_x - halfwidth, scrollbar_y,
            scrollbar_x + halfwidth, self.canvas.height,
            fill = "darkgray", outline = "darkgray"
        )

        self.canvas.create_rectangle(
            scrollbar_x - halfwidth, scroll_pos,
            scrollbar_x + halfwidth, scroll_pos + scroll_height,
            fill = "lightgray", outline = "lightgray"
        )

    def draw(self):
        self.scroll = min(max(0, self.scroll), self.max_scroll)
        self.canvas.delete("all")

        self.max_scroll = VSTEP

        for (x, y, word, font) in self.display_list:
            self.max_scroll = max(y + self.bottom_margin - self.canvas.height, self.max_scroll)

        for (x, y, word, font) in self.display_list: 
            if y > self.scroll + self.canvas.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(
                x, y - self.scroll, 
                text=word, font = font, anchor = "nw"
            )

        self.draw_scrollbar()
        self.draw_addressbar()

    def load(self, path):
        url = URL(path)
        self.current_url = url.url
        text, _, _ = url.request()
        if url.content_type.startswith("text/html"):
            self.tokens = lex(text)
        else:
            self.tokens = [Text(text)]

        self.update_layout()
        self.draw()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else: 
        url = "http://example.org"

    Browser().load(url)
    tkinter.mainloop()
