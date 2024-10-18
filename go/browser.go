package main

import (
	"fmt"
	"os"
	str "strings"
)

type Url struct {
	scheme, host, path string
}

func split1(s string, dlm string) (string, string) {
	ind := str.Index(s, dlm)
	if ind == -1 {
		return s, ""
	}
	return s[:ind], s[ind+len(dlm):]
}

func newUrl(url string) *Url {
	scheme, url := split1(url, "://")
	host, path := split1(url, "/")
	if len(path) == 0 {
		path = "/"
	}
	u := Url{scheme: scheme, host: host, path: path}
	return &u
}

func main() {
	var input string
	if len(os.Args) == 1 {
		input = "http://example.com"
	} else {
		input = os.Args[1]
	}

	url := newUrl(input)

	fmt.Printf("%+v\n", *url)
}
