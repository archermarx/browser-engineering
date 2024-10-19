import tkinter
from url import URL
from html import lex
import platform

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
SCROLL_SPEED = 2
HSTEP, VSTEP = 13, 18
SCROLLBAR_WIDTH = 14
SCROLLBAR_OFFSET = 5

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
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.resize)
        self.detect_platform()

    def resize(self, e):
        self.canvas.width = e.width
        self.canvas.height = e.height
        self.layout()
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

    def layout(self):
        self.display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        self.max_scroll = 0

        screen_width = self.canvas.width - HSTEP - SCROLLBAR_WIDTH - SCROLLBAR_OFFSET

        for c in self.text:
            cursor_x += HSTEP
            if cursor_x >= screen_width or c == '\n':
                cursor_y += VSTEP
                cursor_x = HSTEP

            self.display_list.append((cursor_x, cursor_y, c))
            self.max_scroll = max(cursor_y + VSTEP - self.canvas.height, self.max_scroll)

    def draw_scrollbar(self):
        halfwidth = 0.5 * SCROLLBAR_WIDTH
        scrollbar_x = self.canvas.width - halfwidth - SCROLLBAR_OFFSET
        scrollbar_y = 0
        self.canvas.create_rectangle(
            scrollbar_x - halfwidth, scrollbar_y,
            scrollbar_x + halfwidth, self.canvas.height,
            fill = "darkgray", outline = "darkgray"
        )

        scroll_height = self.canvas.height / self.max_scroll * self.canvas.height
        scroll_pos = self.scroll / self.max_scroll * (self.canvas.height - scroll_height)

        self.canvas.create_rectangle(
            scrollbar_x - halfwidth, scroll_pos,
            scrollbar_x + halfwidth, scroll_pos + scroll_height,
            fill = "lightgray", outline = "lightgray"
        )

    def draw(self):
        self.scroll = min(max(0, self.scroll), self.max_scroll)
        self.canvas.delete("all")

        self.draw_scrollbar()

        for (x, y, c) in self.display_list: 
            if y > self.scroll + self.canvas.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def load(self, url):
        self.text, _, _ = url.request()
        if url.content_type.startswith("text/html"):
            self.text = lex(self.text)

        self.layout()
        self.draw()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else: 
        url = "http://example.org"

    Browser().load(URL(url))
    tkinter.mainloop()
