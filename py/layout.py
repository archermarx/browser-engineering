import tkinter
import tkinter.font

from html import Text, Element
from draw import DrawText, DrawRect

from constants import *

FONTS = {}

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

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

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())
    for child in layout_object.children:
        paint_tree(child, display_list)

class DocumentLayout:
    def __init__(self, node, x1, y1, x2, y2):
        self.node = node
        self.parent = None
        self.previous = None
        self.children = []
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def layout(self):
        child = BlockLayout([self.node], self, None)
        self.children.append(child)

        self.width = self.x2 - self.x1 - 2 * HSTEP
        self.x = HSTEP + self.x1
        self.y = VSTEP + self.y1
        child.layout()
        self.height = child.height

    def paint(self):
        return []

    def __repr__(self):
        return "DocumentLayout()"

class BlockLayout:
    def __init__(self, nodes, parent, previous):
        self.nodes = nodes
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.display_list = []

        # specific styles
        self.family = "Times"
        self.pre = False

    def layout_mode(self):
        if isinstance(self.nodes[0], Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.nodes[0].children]):
            return "block"
        elif self.nodes[0].children:
            return "inline"
        else:
            return "block"
        
    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for node in self.nodes:
                in_sequence = False
                children = []
                buf = []
                for child in node.children:
                    # handle anonymous blocks -- exercise 5-5
                    # group children into lists of text-like elements and individual others
                    # add the lists of elements to block layouts together instead of
                    # individually in their own layouts
                    if isinstance(child, Element) and child.tag in BLOCK_ELEMENTS:
                        # container-like element
                        if in_sequence:
                            children.append(buf)
                            buf = []
                            in_sequence = False
                        children.append([child])
                    else:
                        # text-like element or just text
                        in_sequence = True
                        buf.append(child)

                if buf: children.append(buf)

                # loop over each sequence of children, lay them out together
                for child_list in children:
                    for child in child_list:
                        if isinstance(child, Element):
                            tag, attrs = child.tag, child.attributes
                            if tag == "head": continue # don't include head in layout
                            if tag == "nav" and "id" in attrs and attrs["id"] == '"toc"':
                                # lay out table of contents -- add text right before it in a special container
                                toc_node = Element("nav", attributes = {"id": '"toc_text"'}, parent = None)
                                toc_text = Text("Table of Contents", parent = toc_node)
                                toc_node.children.append(toc_text)

                                next = BlockLayout([toc_node], self, previous)                        
                                self.children.append(next)
                                previous = next

                                next.children.append(BlockLayout([toc_text], next, None))

                    next = BlockLayout(child_list, self, previous)
                    self.children.append(next)
                    previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.line = []
            for node in self.nodes:
                self.recurse(node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([
                child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def paint(self):
        cmds = []
        for node in self.nodes:
            if isinstance(node, Element):
                tag = node.tag
                attrs = node.attributes

                if tag == "pre" :
                    x2, y2 = self.x + self.width, self.y + self.height
                    rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
                    cmds.append(rect)

                if tag == "nav":
                    if "class" in attrs and attrs["class"] == '"links"':
                        # links bar
                        x2, y2 = self.x + self.width, self.y + self.height
                        rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
                        cmds.append(rect)

                    if "id" in attrs and attrs["id"] == '"toc_text"':
                        # table of contents
                        x2, y2 = self.x + self.width, self.y + self.height
                        rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
                        cmds.append(rect)

            if self.layout_mode() == "inline":
                for x, y, word, font in self.display_list:
                    cmds.append(DrawText(x, y, word, font))
        return cmds

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
        elif tag == "pre":
            self.pre = False
            self.family = "Times"
            self.flush()

    def recurse(self, tree):
        if isinstance(tree, Text):
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
        if self.cursor_x + w > self.width:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        self.cursor_x = 0
        self.line = []
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

    def __repr__(self):
        return "BlockLayout[{}](x={}, y={}, width={}, height={}, node={})".format(
            self.layout_mode(), self.x, self.y, self.width, self.height, self.node)
