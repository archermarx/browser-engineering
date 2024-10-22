#ifndef BROWSER_CSS_H
#define BROWSER_CSS_H

#include <string>
#include <memory>
#include <utility>
#include <unordered_map>

struct CssParser {
    std::string &str;
    size_t i = 0;

    CssParser(std::string &s);
    void parse(); 
    void show();
    void whitespace();
    void literal(char c);
    std::string word();
    std::pair<std::string, std::string> pair();
    std::unordered_map<std::string, std::string> body();
};

#endif // BROWSER_CSS_H
