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
	scheme, host, path, port string
}

func split1(s string, dlm string) (string, string) {
	ind := str.Index(s, dlm)
	if ind == -1 {
		return s, ""
	}
	return s[:ind], s[ind+len(dlm):]
}

func newUrl(url string) Url {
	scheme, url := split1(url, ":")
	doubleslash_schemes := []string{"http", "https", "file"}
	supported_schemes := []string{"http", "https", "file", "data"}

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
		return Url{scheme: scheme, host: "", path: url, port: "0"}
	}

	if scheme == "data" {
		content_type, content := split1(url, ",")
		return Url{scheme: scheme, host: content_type, path: content, port: "0"}
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

	return Url{scheme: scheme, host: host, path: path, port: port}
}

type HtmlParseState int

const (
	None HtmlParseState = iota
	InTag
	InEntity
)

func getEntity(acc string) string {
	switch acc {
	case "amp":
		return "&"
	case "lt":
		return "<"
	case "gt":
		return ">"
	case "copy":
		return "©"
	case "ndash":
		return "-"
	}
	return "&" + acc + ";"
}

func show(body string) {
	state := InTag
	acc := ""
	for _, c := range body {
		switch state {
		case None:
			if c == '<' {
				state = InTag
			} else if c == '&' {
				state = InEntity
				acc = ""
			} else {
				fmt.Printf("%c", c)
			}
		case InTag:
			if c == '>' {
				state = None
			}
		case InEntity:
			if c == ';' {
				state = None
				fmt.Printf("%s", getEntity(acc))
			} else {
				acc += string(c)
			}
		}
	}
}

func request(url Url) ([]byte, error) {

	fmt.Printf("%+v\n", url)

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

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {
	var input string
	if len(os.Args) == 1 {
		input = "http://example.com"
	} else {
		input = os.Args[1]
	}

	url := newUrl(input)

	if len(os.Args) > 2 {
		url.port = os.Args[2]
	}

	response, err := request(url)
	check(err)
	show(string(response))
}
