from enum import Enum

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

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
    else:
        return ""

def emit(out, t, buf):
    if buf: out.append(t(buf))
    return ""

def lex(body):
    state = HTMLParseState.InText
    out = []
    text = ""
    buf = ""
    for c in body:
        if state == HTMLParseState.InText:
            if c == "<":
                state = HTMLParseState.InTag
                out.append(Text(text))
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
                out.append(Tag(buf))
                buf = ""
            else:
                buf += c

    if state == HTMLParseState.InText and text:
        out.append(Text(text))

    return out

def print_tokens(tokens):
    for t in tokens:
        if isinstance(t, Text):
            print(f"text: {t.text}")
        else:
            print(f"tag: {t.tag}")

if __name__ == "__main__":
    import sys
    tokens = lex(sys.argv[1])
    print_tokens(tokens)

