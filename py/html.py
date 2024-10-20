from enum import Enum

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

HTMLParseState = Enum('HTMLParseState', [
    'InText', "InTag", "InEntity", "InComment",
])

class HTMLParser:
    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]

    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    def __init__(self, body):
        self.body = body
        self.unfinished = []
        self.out = []
        self.pos = 0

    def peek(self, n = 0):
        if self.pos + n >= len(self.body):
            return '\0'
        else:
            return self.body[self.pos + n]

    def advance(self, n = 1):
        self.pos += n
        return self.peek()

    def starts_comment(self):
        if self.peek() == '<' and self.peek(1) == '!' and \
           self.peek(2) == '-' and self.peek(3) == '-':
            return True
        return False

    def ends_comment(self):
        if self.peek() == '-' and self.peek(1) == '-' and self.peek(2) == '>':
            return True
        return False

    def parse(self):
        state = HTMLParseState.InText
        text = ""
        buf = ""
        comment_found = 0
        i = 0;
        c = self.peek()
        while c != '\0':
            if self.starts_comment():
                print("starts comment")
                c = self.advance(2)
                while c != '\0' and not self.ends_comment():
                    c = self.advance()
                if c == '\0':
                    break

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

            c = self.advance()

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
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"): return
        self.implicit_tags(tag)

        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] \
                 and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and \
                 tag not in ["/head"] + self.HEAD_TAGS:
                self.add_tag("/head")
            else:
                break

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
    space = "." * indent
    print(f"{space}{node}")
    for child in node.children:
        print_tree(child, indent + 1)

if __name__ == "__main__":
    import sys
    tokens = lex(sys.argv[1])
    print_tokens(tokens)

