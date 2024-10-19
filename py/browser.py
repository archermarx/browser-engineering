import tkinter
from url import URL
from html import lex
import platform

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
SCROLL_SPEED = 2
HSTEP, VSTEP = 13, 18

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP or c == '\n':
            cursor_y += VSTEP
            cursor_x = HSTEP

        display_list.append((cursor_x, cursor_y, c))

    return display_list

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width = WIDTH,
            height = HEIGHT,
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.scrollwheel)

        self.detect_platform()

    def detect_platform(self):
        os = platform.system()
        MAC_SCROLL_DELTA = -1
        WINDOWS_SCROLL_DELTA = 120
        self.scroll_speed = 2

        if os == "Darwin":
            self.scroll_speed = self.scroll_speed / MAC_SCROLL_DELTA
        elif os == "Windows":
            self.scroll_speed = self.scroll_speed / WINDOWS_SCROLL_DELTA



    def scrollup(self, e):
        self.scroll = self.scroll - SCROLL_STEP
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollwheel(self, e):
        self.scroll += self.scroll_speed * e.delta 
        self.draw()

    def draw(self):
        self.scroll = max(0, self.scroll)
        self.canvas.delete("all")
        for (x, y, c) in self.display_list: 
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def load(self, url):
        body, _, _ = url.request()
        if url.content_type.startswith("text/html"):
            text = lex(body)
        else:
            text = body

        self.display_list = layout(text)
        self.draw()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else: 
        url = "http://example.org"

    Browser().load(URL(url))
    tkinter.mainloop()
