import socket
import ssl
from enum import Enum

HTMLParseState = Enum('HTMLParseState', [
    'Ok', "InTag", "InEntity"
])

def entity(acc):
    if acc == "lt":
        return "<"
    elif acc == "gt":
        return ">"

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

def load(url):
    body = url.request()
    show(body)

class URL:
    def __init__(self, url):
        # determine scheme - only http, https, and file supported for now
        # if no scheme header, file is assumed
        if "://" in url:
            self.scheme, url = url.split("://", 1)
        else:
            self.scheme, url = "file", url

        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "file":
            self.path = url
            self.host = ""
            self.port = 0
            return

        # separate host from path
        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url 

        # determine which port we're using
        if ":" in self.host:
            # custom port present
            self.host, port = url.split(":", 1)
            self.port = int(port)
        elif self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

    def request(self):
        # read file if needed
        if self.scheme == "file":
            with open(self.path) as f:
                s = f.read();
            return s
        
        # Create socket
        s = socket.socket(
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto = socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))

        # wrap socket with SSL encryption if using https
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname = self.host)

        # send HTTP get request
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))
        
        # Record the response
        response = s.makefile("r", encoding="utf8", newline = "\r\n")

        # Parse the response
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": 
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
            
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))


