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

def load(url):
    body = url.request()
    if url.content_type.startswith("text/html"):
        show(body)
    else:
        print(body)

class URL:
    def __init__(self, url, redirect_depth = 0):
        # prevent infinite redirect chains
        assert(redirect_depth < 5)
        self.redirect_depth = redirect_depth

        # set default content type
        self.content_type = "text/html"

        # determine scheme - only http, https, file, data, and view-source supported for now
        # if no scheme provided, file is assumed

        # check for view-source scheme
        if url.startswith("view-source:"):
            self.content_type = "text/plain;charset=utf8"
            url = url[12:]

        if "://" in url:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https", "file"]
        elif ":" in url:
            self.scheme, url = url.split(":", 1)
            assert self.scheme == "data"
        else:   
            self.scheme = "file"

        # handle file scheme
        if self.scheme == "file":
            self.path = url
            if "." in self.path:
                _, ext = self.path.split(".", 1)
                if ext != "html":
                    self.content_type = "text/plain;charset=utf8"
            return
        
        if self.scheme == "data":
            assert "," in url
            self.content_type, self.data = url.split(",", 1)
            if self.content_type == "":
                self.content_type = "text/plain;charset=US-ASCII"

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

        self.socket = None

    def request(self):
        if self.scheme == "data":
            return self.data

        if self.scheme == "file":
            with open(self.path) as f:
                return f.read()
        
        # Create socket
        if self.socket is None:
            self.socket = socket.socket(
                family = socket.AF_INET,
                type = socket.SOCK_STREAM,
                proto = socket.IPPROTO_TCP,
            )

            self.socket.connect((self.host, self.port))
            
            # wrap socket with SSL encryption if using https
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                self.socket = ctx.wrap_socket(self.socket, server_hostname = self.host)

        # send HTTP get request
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "User-Agent: archermarx\r\n"
        request += "Connection: Keep-Alive\r\n"
        request += "\r\n"
        self.socket.send(request.encode("utf8"))            
        
        # Record the response
        response = self.socket.makefile("r", encoding="utf8", newline = "\r\n")

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

        # check for redirect
        if 300 <= int(status) < 400:
            location = response_headers["location"]
            if location.startswith("/"):
                location = self.scheme + "://" + self.host + location

            print(f"Redirecting to {location} (depth = {self.redirect_depth})")
            redirect = URL(location, self.redirect_depth + 1)
            return redirect.request()

        self.content_type = response_headers["content-type"]
        content_length = int(response_headers["content-length"])
        content = response.read(content_length)

        return content

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))


