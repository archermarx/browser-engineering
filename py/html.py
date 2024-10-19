from enum import Enum

HTMLParseState = Enum('HTMLParseState', [
    'Ok', "InTag", "InEntity"
])

def entity(acc):
    if acc == "lt":
        return "<"
    elif acc == "gt":
        return ">"
    elif acc == "amp":
        return "&"
    elif acc == "ndash":
        return "-"
    elif acc == "copy":
        return "©"
    elif acc == "quot":
        return '"'
    else:
        return ""

def advance(state, acc, c):
    if state == HTMLParseState.Ok:
        if c == "<":
            state = HTMLParseState.InTag
        elif c == "&":
            state = HTMLParseState.InEntity
        else:
            print(c, end = "")
    elif state == HTMLParseState.InTag:
        if c == ">":
            state = HTMLParseState.Ok
    elif state == HTMLParseState.InEntity:
        if c == ";":
            state = HTMLParseState.Ok
            print(entity(acc), end = "")
            acc = ""
        else:
            acc += c

    return state, acc
def show(body):
    state = HTMLParseState.Ok
    acc = ""
    for c in body:
        state, acc = advance(state, acc, c)
