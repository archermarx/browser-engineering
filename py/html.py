from enum import Enum

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]

class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)

class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent
    
    def __repr__(self):
        return "<" + self.tag + ">"

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []
        self.out = []

    def parse(self):
        state = HTMLParseState.InText
        text = ""
        buf = ""
        for c in self.body:
            if state == HTMLParseState.InText:
                if c == "<":
                    state = HTMLParseState.InTag
                    self.add_text(text)
                    text = ""
                elif c == "&":
                    state = HTMLParseState.InEntity
                else:
                    text += c

            elif state == HTMLParseState.InEntity:
                if c == ";":
                    state = HTMLParseState.InText
                    text += entity(buf)
                    buf = ""
                else:
                    buf += c
                    
            elif state == HTMLParseState.InTag:
                if c == ">":
                    state = HTMLParseState.InText
                    self.add_tag(buf)
                    buf = ""
                else:
                    buf += c

        if state == HTMLParseState.InText and text:
            self.add_text(text)

        return self.finish()

    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""

        return tag, attributes

    def add_text(self, text):
        if text.isspace() or not text: return
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"): return
        if tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        elif tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

HTMLParseState = Enum('HTMLParseState', [
    'InText', "InTag", "InEntity"
])

def entity(buf):
    if buf == "lt":
        return "<"
    elif buf == "gt":
        return ">"
    elif buf == "amp":
        return "&"
    elif buf == "ndash":
        return "-"
    elif buf == "copy":
        return "©"
    elif buf == "quot":
        return '"'
    elif buf == "shy":
        return "\N{soft hyphen}"
    else:
        return ""

def print_tree(node, indent = 0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)

if __name__ == "__main__":
    import sys
    tokens = lex(sys.argv[1])
    print_tokens(tokens)

