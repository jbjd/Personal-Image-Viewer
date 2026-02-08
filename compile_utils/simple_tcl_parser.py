def is_whitespace_or_semicolon(token: str) -> bool:
    return token.isspace() or token == ";"


def is_delimiter(token: str) -> bool:
    return is_whitespace_or_semicolon(token) or token in ("[", "]", "{", "}")


def tcl_parse(source: str) -> list[str]:  # noqa: PLR0912
    token_start: int = 0
    token_end: int = 0
    source_end: int = len(source)

    tokens: list[str] = []

    def find_token_end(token: str) -> int:
        nonlocal source, token_start
        return source.find(token, token_start + 1)

    while token_start < source_end:
        first_char: str = source[token_start]
        if first_char.isspace():
            if not tokens or is_whitespace_or_semicolon(tokens[-1]):
                if tokens and (
                    first_char == "\n"
                    or (first_char == ";" and tokens[-1] in (" ", "\t"))
                ):
                    tokens[-1] = first_char
            else:
                tokens.append(first_char)
            token_start += 1
            continue

        if is_delimiter(first_char):
            tokens.append(first_char)
            token_start += 1
            continue

        if first_char == "#":
            comment_end: int = find_token_end("\n")
            if comment_end == -1:
                break  # end of file
            token_end = comment_end
        elif first_char == '"':
            string_end: int = find_token_end('"')
            if string_end == -1:
                raise SyntaxError("Found unclosed string")
            token_end = string_end + 1
            string_token: str = source[token_start:token_end].replace("\\n", "")
            tokens.append(string_token)
        else:
            token_end = token_start + 1
            while token_end < source_end and not is_delimiter(source[token_end]):
                token_end += 1
            token: str = source[token_start:token_end]
            if token == "\\" and source[token_end : token_end + 1] == "\n":
                token_end += 1
            else:
                tokens.append(token)

        token_start = token_end

    return tokens


def tcl_optimize(tokens: list[str], remove_print: bool) -> None:
    if not tokens:
        return

    new_tokens: list[str] = []
    for token in tokens:
        if token == "}" and new_tokens and new_tokens[-1].isspace():
            new_tokens[-1] = token
        else:
            new_tokens.append(token)

    tokens[:] = new_tokens


def tcl_unparse(tokens: list[str]) -> str:
    return "".join(str(token) for token in tokens)


def tcl_minify(source: str, remove_print: bool = True) -> str:
    tokens: list[str] = tcl_parse(source)

    tcl_optimize(tokens, remove_print)

    return tcl_unparse(tokens)


# test = """
# uplevel \\#0 {
#     package require msgcat 1.6
#     if { $::tcl_platform(platform) eq {windows} } {
#         if { [catch { package require registry 1.1 }] } {
#             namespace eval ::tcl::clock [list variable NoRegistry {}]
#         }  # some comment
#     }
# }
# puts "hello   world";
# namespace eval ::tcl::clock \\
# [list variable LibDir [info library]]


# """
# print(tcl_minify(test))
