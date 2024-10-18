package main

import str "strings"

func split1(s string, dlm string) (string, string) {
	ind := str.Index(s, dlm)
	if ind == -1 {
		return s, ""
	}
	return s[:ind], s[ind+len(dlm):]
}

func getExt(path string) string {
	_, ext := split1(path, ".")
	return ext
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
