import socket
import ssl
import time
from typing import Dict, Tuple
import gzip

response_cache: Dict[str, Tuple[float, float, str]] = {}
class URL:
    
    def url_check(self, cond):
        if not cond:
            self.malformed = True

    def __init__(self, url, redirect_depth = 0):
        # store initial url to use a as a key for cache lookups
        self.url = url
        self.malformed = False

        # prevent infinite redirect chains
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
            self.url_check(self.scheme in ["http", "https", "file"])
        elif ":" in url:
            self.scheme, url = url.split(":", 1)
            self.url_check(self.scheme == "data")
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
            self.url_check("," in url)
            self.content_type, self.data = url.split(",", 1)
            if self.content_type == "":
                self.content_type = "text/plain;charset=US-ASCII"

        if self.malformed:
            self.url = "about:blank"
            return;

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
        if self.malformed:
            return "", None, None

        if self.scheme == "data":
            return self.data, None, None

        if self.scheme == "file":
            with open(self.path) as f:
                return f.read(), None, None

        current_time = time.time()
            
        if self.url in response_cache:
            # use cached response if page not too old
            content = response_cache[self.url]
            timestamp, max_age, content = response_cache[self.url]
            age = current_time - timestamp
            if (max_age < 0) or (age < max_age):
                return content, True, max_age
      
        #  Create socket
        self.socket = socket.socket(
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto = socket.IPPROTO_TCP,
        )

        try:
            self.socket.connect((self.host, self.port))
        except:
            return "Invalid URL", None, None
        
        # wrap socket with SSL encryption if using https
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            self.socket = ctx.wrap_socket(self.socket, server_hostname = self.host)

        # send HTTP GET request
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "User-Agent: archermarx\r\n"
        request += "Connection: close\r\n"
        request += "Accept-Encoding: gzip\r\n"
        request += "\r\n"
        self.socket.send(request.encode("utf8"))            
        
        response = self.socket.makefile("rb", newline = "\r\n")

        # Parse the response
        statusline = response.readline().decode("utf8")
        version, status, explanation = statusline.split(" ", 2)
        status = int(status)

        response_headers = {}
        while True:
            line = response.readline().decode("utf8")
            if line == "\r\n": 
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        max_age = -1.0
        cache = True

        if "cache-control" in response_headers:
            options = response_headers["cache-control"].split(",")
            for opt in options:
                opt = opt.strip()
                if opt == "no-store":
                    cache = False
                elif opt.startswith("max-age"):
                    _, val = opt.split("=", 1)
                    max_age = float(val)
                else:
                    # don't cache if other options provided
                    cache = False
            
        # don't bother caching pages with very short max ages
        if max_age < 1.0:
            cache = False

        # check for redirect
        if 300 <= status < 400 and self.redirect_depth < 10:
            location = response_headers["location"]
            if location.startswith("/"):
                location = self.scheme + "://" + self.host + location

            print(f"Redirecting to {location} (depth = {self.redirect_depth})")
            redirect = URL(location, self.redirect_depth + 1)
            # todo: cache redirects without caching whole page
            return redirect.request()

        self.content_type = response_headers["content-type"]

        chunked = False
        compressed = False

        if "transfer-encoding" in response_headers:
            transfer_encoding_opts = [s.strip() for s in response_headers["transfer-encoding"].split(",")]
            chunked = "chunked" in transfer_encoding_opts
            compressed = "gzip" in transfer_encoding_opts

        if "content-encoding" in response_headers:
            content_encoding_opts = [s.strip() for s in response_headers["content-encoding"].split(",")]
            compressed = "gzip" in content_encoding_opts

        def read_chunk(f):
            chunk = b""
            chunk_size = f.readline()
            chunk_size = int(chunk_size[:-2], 16)
            if chunk_size > 0:
                chunk += f.read(chunk_size)
                f.readline()
            return chunk

        # read content in chunks if requested
        if chunked:
            content = b""
            while True:
                chunk = read_chunk(response)
                if not chunk:
                    break
                content += chunk

        else:
            bytes_to_read = int(response_headers["content-length"])
            content = response.read(bytes_to_read)

        # decompress content if needed
        if compressed:
            content = gzip.decompress(content)

        content = content.decode("utf-8")

        # cache content
        if cache and (status == 200 or status == 404):
            response_cache[self.url] = (current_time, max_age, content)

        self.socket.close()

        return content, cache, max_age
