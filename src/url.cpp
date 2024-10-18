#include <utility>
#include <fmt/core.h>
#include <cassert>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <unistd.h>
#include <iostream>

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
    auto [hostname, pathname] = split(rest, "/");
    this->host = hostname;
    this->path = "/" + pathname;
}

void request (URL url) {
    const char* port = "80";

    // Create address structs
    addrinfo hints, *res;
    int sockfd;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    getaddrinfo(url.host.c_str(), port, &hints, &res);
    
    // Make a socket
    sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

    // connect!
    connect(sockfd, res->ai_addr, res->ai_addrlen);

    // create HTTP GET request
    auto req = fmt::format(
        "GET {} HTTP/1.0\r\n"
        "Host: {}\r\n"
        "\r\n"
        , url.path, url.host);

    // send request
    auto bytes_sent = send(sockfd, req.c_str(), req.length(), 0);
    
    // get response
    constexpr size_t chunksize = 1024;
    char buf[chunksize];

    std::string response = "";
    int bytes_received;
    do {
        bytes_received = recv(sockfd, buf, chunksize, 0);
        response += std::string(buf).substr(0, bytes_received);
    } while (bytes_received > 0);





    close(sockfd);
}
