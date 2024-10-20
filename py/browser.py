import tkinter
import tkinter.font
import platform
import os
from constants import *
from url import URL
from html import HTMLParser, print_tree
from layout import paint_tree, DocumentLayout 

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

    def display_rect(self):
        screen_width = self.canvas.width - SCROLLBAR_WIDTH - SCROLLBAR_OFFSET
        x1 = 0
        y1 = ADDRESSBAR_HEIGHT
        x2 = screen_width
        y2 = HEIGHT 
        return x1, y1, x2, y2

    def update_layout(self):
        self.document = DocumentLayout(self.nodes, *(self.display_rect()))
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

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

        for cmd in self.display_list:
            self.max_scroll = max(
                cmd.bottom + self.bottom_margin - self.canvas.height,
                self.max_scroll
            )

        for cmd in self.display_list: 
            if cmd.top > self.scroll + self.canvas.height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)

        self.draw_scrollbar()
        self.draw_addressbar()


    def load(self, path):
        url = URL(path)
        self.current_url = url.url
        body, _, _ = url.request()

        if url.content_type.startswith("text/html"):
            self.nodes = HTMLParser(body).parse()
        else:
            self.nodes = Text(body)

        self.update_layout()
        self.draw()

        #print_tree(self.nodes)
        print_tree(self.document)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else: 
        url = "http://example.org"

    Browser().load(url)
    tkinter.mainloop()
