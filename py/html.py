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

def advance(state, text, acc, c):
    if state == HTMLParseState.Ok:
        if c == "<":
            state = HTMLParseState.InTag
        elif c == "&":
            state = HTMLParseState.InEntity
        else:
            text += c
    elif state == HTMLParseState.InTag:
        if c == ">":
            state = HTMLParseState.Ok
    elif state == HTMLParseState.InEntity:
        if c == ";":
            state = HTMLParseState.Ok
            text += entity(acc)
            acc = ""
        else:
            acc += c

    return state, text, acc

def lex(body):
    state = HTMLParseState.Ok
    acc = ""
    text = ""
    for c in body:
        state, text, acc = advance(state, text, acc, c)
    return text
