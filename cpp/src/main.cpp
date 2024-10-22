#include <iostream>
#include "fmt/core.h"

#include "url.h"
#include "css.h"

//int main (int argc, char** argv) {
//    std::string url_str = "https://example.org";
//    if (argc > 1) {
//        url_str = argv[1];
//    }
//    auto url = URL(url_str);
//
//    fmt::println(
//        "scheme = {}, host = {}, path = {}",
//        scheme_name(url.scheme), url.host, url.path);
//
//    request(url);
//}
//

void parse_css (int argc, char **argv) {
    std::string content = "";
    if (argc > 1) {
        content = argv[1];
    }
    
    auto parser = CssParser(content);
    parser.parse();
    parser.show();
}

int main(int argc, char **argv) {
    parse_css(argc, argv);
}
