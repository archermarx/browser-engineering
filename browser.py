import socket
import ssl

def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end = "")

def load(url):
    body = url.request()
    show(body)

class URL:
    def __init__(self, url):
        # determine scheme - only http and https supported for now
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        # determine which port we're using
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        # separate host from path
        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
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


