#include <utility>
#include <fmt/core.h>
#include <cassert>

#include "url.h"

#define X(uri) if (scheme_str == #uri) return uri_scheme::uri;
uri_scheme get_scheme (const std::string &scheme_str) {
    URI_SCHEMES
    if (scheme_str == "") return uri_scheme::file;
    return uri_scheme::invalid;
}
#undef X

#define X(uri) case(uri_scheme::uri): return #uri;
std::string scheme_name (uri_scheme scheme) {
   switch (scheme) {
    URI_SCHEMES
    }
}
#undef X

using std::pair, std::string;

pair<string,string> split (const string &path, const string &dlm) {
    auto pos = path.find(dlm);
    if (pos == string::npos) return {path, ""};
    auto len = path.length();
    auto head = path.substr(0, pos);
    auto tail = path.substr(pos + dlm.length(), len);
    return {head, tail};
}

URL::URL (const string &url) {
    // determine uri scheme
    auto [scheme_str, rest] = split(url, ":");
    scheme = get_scheme(scheme_str);

    assert(scheme != uri_scheme::invalid);

    if (scheme == uri_scheme::http  ||
        scheme == uri_scheme::https ||
        scheme == uri_scheme::file) {

        // consume "//" after scheme
        assert(rest.find("//") == 0);
        rest = rest.substr(2, rest.length());
    }

    // Get host and path
    [this->host, this->path] = split(rest, "/");
    path = "/" + path;

    fmt::println("scheme = {}, host = {}, path = {}", scheme_name(scheme), host, path);
    

    
}
