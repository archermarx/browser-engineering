#include <string>

#define URI_SCHEMES \
    X(none) \
    X(http) \
    X(https) \
    X(file) \
    X(data) \
    X(view_source) \
    X(about) \
    X(invalid)

#define X(uri) uri,
enum class uri_scheme {
    URI_SCHEMES
};
#undef X

std::string scheme_name (uri_scheme scheme);
uri_scheme get_scheme (const std::string &scheme_str);

struct URL {
    public:
        uri_scheme scheme;
        std::string host;
        std::string path;

        URL (const std::string &url); 
};
