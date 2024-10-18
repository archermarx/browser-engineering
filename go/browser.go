package main

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"io"
	"net"
	"os"
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
	scheme, url := split1(url, "://")
	host, path := split1(url, "/")
	if !str.HasPrefix(path, "/") {
		path = "/" + path
	}

	// check for port
	host, port := split1(host, ":")

	if scheme != "http" && scheme != "https" {
		panic("only http or https supported")
	}

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

	u := Url{scheme: scheme, host: host, path: path, port: port}
	return u
}

func show(body string) {
	in_tag := false
	for _, c := range body {
		if c == '<' {
			in_tag = true
		} else if c == '>' {
			in_tag = false
		} else if !in_tag {
			fmt.Printf("%c", c)
		}
	}
	fmt.Println()
}

func request(url Url) ([]byte, error) {

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
	req := fmt.Sprintf("GET %s HTTP/1.0\r\n", url.path)
	req += fmt.Sprintf("Host: %s\r\n", url.host)
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

	response, _ := request(url)
	show(string(response))
}
