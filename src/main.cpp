#include <iostream>
#include "fmt/core.h"

#include "url.h"

int main (int argc, char** argv) {
    std::string url_str = "https://example.org";
    if (argc > 1) {
        url_str = argv[1];
    }
    auto url = URL(url_str);

    fmt::println("scheme = {}", scheme_name(url.scheme));
}
