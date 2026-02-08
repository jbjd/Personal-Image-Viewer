def is_whitespace_or_semicolon(token: str) -> bool:
    return token.isspace() or token == ";"


def is_delimiter(token: str) -> bool:
    return is_whitespace_or_semicolon(token) or token in ("[", "]", "{", "}")


def tcl_parse(source: str) -> list[str]:
    source = source.replace("\\\n", "")

    token_start: int = 0
    token_end: int = 0
    source_end: int = len(source)

    tokens: list[str] = []

    while token_start < source_end:
        first_char: str = source[token_start]

        if is_delimiter(first_char):
            tokens.append(first_char)
            token_start += 1
            continue

        if first_char == "#":
            comment_end: int = source.find("\n", token_start + 1)
            if comment_end == -1:
                tokens.append(source[token_start:])
            else:
                tokens.append(source[token_start:comment_end])
                token_end = comment_end
        elif first_char == '"':
            token_end = token_start + 1
            while token_end < source_end and (
                source[token_end] != '"' or source[token_end - 1] == "\\"
            ):
                token_end += 1
            token_end += 1
            string_token: str = source[token_start:token_end]
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


def tcl_optimize(tokens: list[str]) -> None:  # noqa:
    if not tokens:
        return

    new_tokens: list[str] = []

    for token in tokens:
        if token == "}" and new_tokens and new_tokens[-1].isspace():
            new_tokens[-1] = token
        elif token.isspace():
            if not new_tokens:
                pass
            elif is_whitespace_or_semicolon(new_tokens[-1]):
                if token == "\n" or (token == ";" and new_tokens[-1] in (" ", "\t")):
                    new_tokens[-1] = token
            else:
                new_tokens.append(token)
        else:
            # TODO: token[0] != "#" breaks everything for some reason
            new_tokens.append(token)

    while new_tokens and new_tokens[-1].isspace():
        new_tokens.pop()

    tokens[:] = new_tokens


def tcl_unparse(tokens: list[str]) -> str:
    return "".join(str(token) for token in tokens)


def tcl_minify(source: str) -> str:
    tokens: list[str] = tcl_parse(source)

    tcl_optimize(tokens)

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
# if { $::tcl_platform(platform) eq {windows} } {
#     puts -nonewline "hello   world";
# }
# namespace eval ::tcl::clock \\
# [list variable LibDir [info library]]

# # comment
# """
# print(tcl_minify(test))


# test = '''puts "escaped \\"quote\\""'''
# print(tcl_minify(test))
