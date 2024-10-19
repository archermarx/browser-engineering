import tkinter
from url import URL
from html import show

WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width = WIDTH,
            height = HEIGHT,
        )
        self.canvas.pack()

    def load(self, url):
        body, _, _ = url.request()
        if url.content_type.startswith("text/html"):
            show(body)
        else:
            print(body)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = "http://example.org"
    else: 
        url = sys.argv[1]

    Browser().load(URL(url))
    tkinter.mainloop()
