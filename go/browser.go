package main

import (
	"log"
	"os"
	"runtime"

	"github.com/gotk3/gotk3/gtk"
)

func init() {
	runtime.LockOSThread()
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

func lex(body string, contentType string) string {
	if contentType != "text/html" {
		return body
	}
	state := InTag
	acc := ""
	text := ""
	for _, c := range body {
		switch state {
		case None:
			if c == '<' {
				state = InTag
			} else if c == '&' {
				state = InEntity
				acc = ""
			} else {
				text += string(c)
			}
		case InTag:
			if c == '>' {
				state = None
			}
		case InEntity:
			if c == ';' {
				state = None
				text += getEntity(acc)
			} else {
				acc += string(c)
			}
		}
	}
	return text
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

	Browser{}.load(url)
}

type Browser struct{}

func (b Browser) load(url Url) {
	response, err := request(url)
	check(err)
	_ = lex(string(response), url.content_type)

	gtk.Init(nil)
	// Create a new toplevel window, set its title, and connect it to the
	// "destroy" signal to exit the GTK main loop when it is destroyed.
	win, err := gtk.WindowNew(gtk.WINDOW_TOPLEVEL)
	if err != nil {
		log.Fatal("Unable to create window:", err)
	}
	win.SetTitle("Simple Example")
	win.Connect("destroy", func() {
		gtk.MainQuit()
	})

	// Create a new label widget to show in the window.
	l, err := gtk.LabelNew("Hello, gotk3!")
	if err != nil {
		log.Fatal("Unable to create label:", err)
	}

	// Add the label to the window.
	win.Add(l)

	// Set the default window size.
	win.SetDefaultSize(800, 600)

	// Recursively show all widgets contained in this window.
	win.ShowAll()

	// Begin executing the GTK main loop.  This blocks until
	// gtk.MainQuit() is run.
	gtk.Main()

}
