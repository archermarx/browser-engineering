#include "css.h"
#include "fmt/core.h"

#include <stdexcept>

using std::string;

CssParser::CssParser(string &s): str(s) {}

static bool p_isspace(char c) {
    return c == ' ' || c == '\r' || c == '\t' || c == '\n';
}

static bool p_isalpha(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

static bool p_isdigit(char c) {
    return c >= '0' && c <= '9';
}

static bool p_iswordchar(char c) {
    return p_isalpha(c) || p_isdigit(c) ||
           c == '#' || c == '-' || c == '.' || c == '%';
}

static int consume_whitespace(string &s, size_t &i) {
    size_t start = i;
    while (i < s.length() && p_isspace(s[i])) {
        i++;
    }
    return i - start;
}

static int consume_literal_char(string &s, size_t &i, char c) {
    size_t start = i;
    if (i < s.length() && s[i] == c) {
        i++;
    }
    return i - start;
} 

static int consume_word(string &s, size_t &i) {
    size_t start = i;
    while (i < s.length() && p_iswordchar(s[i])) {
        i++;
    }
    return i - start;
}

static int consume_until_char(string &s, size_t &i, char c) {
    size_t start = i;
    while (i < s.length() && s[i] != c) {
        i++;
    }
    return i - start;
}

void CssParser::whitespace() {
    consume_whitespace(this->str, this->i);
}

string CssParser::word() {
    size_t start = this->i;
    auto stat = consume_word(this->str, this->i);
    if (!stat) {
        throw std::runtime_error("Expected word");
    }
    return this->str.substr(start, this->i - start);
}

void CssParser::literal(char c) {
    auto stat = consume_literal_char(this->str, this->i, c);
    if (!stat) {
        throw std::runtime_error(fmt::format("Expected {}", c));
    }
}

std::pair<string,string> CssParser::pair() {
    auto prop = this->word();
    this->whitespace();
    this->literal(':');
    this->whitespace();
    auto val = this->word();
    return {prop, val};
}

std::unordered_map<string, string> CssParser::body() {
    std::unordered_map<string, string> pairs{};

    while(this->i < this->str.length()) {
        try {
            auto [prop, val] = this->pair();
            pairs[prop] = val;
            this->whitespace();
            this->literal(';');
            this->whitespace();
        } catch (std::runtime_error &e) {
            consume_until_char(this->str, this->i, ';');
            if (this->str[this->i] == ';') {
                this->literal(';');
                this->whitespace();
            } else {
                break;
            }
        }
    }
    return pairs;
}

void CssParser::parse() {
    auto pairs = this->body();
    for (const auto& [k, v]: pairs) {
        fmt::println("got: {} = {}", k, v);
    }
}

void CssParser::show() {}
