package main

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"io"
	"net"
	"os"
	"slices"
	"strconv"
	str "strings"
)

type Url struct {
	scheme, host, path, port, content_type string
}

func newUrlWithContentType(url string, content_type string) Url {
	scheme, url := split1(url, ":")
	doubleslash_schemes := []string{"http", "https", "file"}
	supported_schemes := []string{"http", "https", "file", "data", "view-source"}

	if !slices.Contains(supported_schemes, scheme) {
		panic(fmt.Errorf("unsupported scheme %s. Supported schemes are %v", scheme, supported_schemes))
	}

	// check for and remove "//" at beginning of http, file, etc
	if slices.Contains(doubleslash_schemes, scheme) {
		if str.HasPrefix(url, "//") {
			url = str.TrimPrefix(url, "//")
		} else {
			panic(fmt.Errorf("malformed uri: %s, expected leading //", url))
		}
	}

	if scheme == "file" {
		if getExt(url) != "html" {
			content_type = "text/ascii"
		}
		return Url{scheme: scheme, host: "", path: url, port: "0", content_type: content_type}
	}

	if scheme == "data" {
		content_type, content := split1(url, ",")
		return Url{scheme: scheme, host: "", path: content, port: "0", content_type: content_type}
	}

	if scheme == "view-source" {
		return newUrlWithContentType(url, "text/ascii")
	}

	host, path := split1(url, "/")
	if !str.HasPrefix(path, "/") {
		path = "/" + path
	}

	// check for port
	host, port := split1(host, ":")

	if len(port) == 0 {
		switch scheme {
		case "http":
			port = "80"
		case "https":
			port = "443"
		default:
			port = "80"
		}
	}

	return Url{scheme: scheme, host: host, path: path, port: port, content_type: content_type}
}

func newUrl(url string) Url {
	return newUrlWithContentType(url, "text/html")
}

func request(url Url) ([]byte, error) {

	if url.scheme == "file" {
		return os.ReadFile(url.path)
	}

	if url.scheme == "data" {
		return []byte(url.path), nil
	}

	address := url.host + ":" + url.port

	var conn net.Conn
	var err error
	if url.scheme == "https" {
		conn, err = tls.Dial("tcp", address, &tls.Config{})
	} else {
		conn, err = net.Dial("tcp", address)
	}

	if err != nil {
		panic(fmt.Errorf("cannot connect to host %s on port %s\n. Error: %v", url.host, url.port, err))
	}

	// send HTTP get request
	req := fmt.Sprintf("GET %s HTTP/1.1\r\n", url.path)
	req += fmt.Sprintf("Host: %s\r\n", url.host)
	req += "Connection: close\r\n"
	req += "User-Agent: archermarx-browser\r\n"
	req += "\r\n"
	fmt.Fprint(conn, req)

	// get status line and parse error code
	response_reader := bufio.NewReader(conn)
	status_line, _ := response_reader.ReadString('\n')
	status_line = str.TrimRight(status_line, "\r\n")
	parts := str.Split(status_line, " ")
	status_code, _ := strconv.Atoi(parts[1])

	if status_code >= 400 {
		panic(fmt.Errorf("bad request\n%s", req))
	}

	response_headers := make(map[string]string)
	for {
		line, _ := response_reader.ReadString('\n')
		if line == "\r\n" {
			break
		}
		line = str.TrimRight(line, "\r\n")
		key, val := split1(line, ":")
		response_headers[str.ToLower(key)] = str.Trim(val, " ")
	}

	if _, ok := response_headers["transfer-encoding"]; ok {
		panic("transfer-encoding not supported")
	}

	if _, ok := response_headers["content-encoding"]; ok {
		panic("content-enconding not supported")
	}

	return io.ReadAll(response_reader)
}
