import re


def tcl_parse(source: str) -> list[str]:
    source = re.sub(r"\\\n[ \t]*", " ", source)

    token_start: int = 0
    token_end: int = 0
    source_end: int = len(source)

    tokens: list[str] = []

    while token_start < source_end:
        first_char: str = source[token_start]

        if _is_whitespace_or_semicolon(first_char):
            token_start += 1
            if tokens:
                if _is_whitespace_or_semicolon(tokens[-1]):
                    if first_char == "\n" or (
                        first_char == ";" and tokens[-1] in (" ", "\t")
                    ):
                        tokens[-1] = first_char
                else:
                    tokens.append(first_char)

            continue

        if _is_bracket(first_char):
            token_start += 1
            tokens.append(first_char)
            continue

        if _is_token_comment(first_char, tokens):
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
            while token_end < source_end and not _is_delimiter(source[token_end]):
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
    depth: int = 0

    for token in tokens:
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1

        if token == "}" and new_tokens and new_tokens[-1].isspace():
            new_tokens[-1] = token
        elif token == "\n" and (not new_tokens or new_tokens[-1] == "\n"):
            pass
        elif _is_token_comment(token, new_tokens):
            open_curly_count: int
            closing_curly_count: int

            # https://wiki.tcl-lang.org/page/Why+can+I+not+place+unmatched+braces+in+Tcl+comments
            if depth > 0:
                open_curly_count = token.count("{")
                closing_curly_count = token.count("}")
            else:
                open_curly_count = 0
                closing_curly_count = 0

            if open_curly_count > 0 or closing_curly_count > 0:
                depth += open_curly_count
                depth -= closing_curly_count
                new_tokens.append(token)
                continue
        else:
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


def _is_whitespace_or_semicolon(token: str) -> bool:
    return token.isspace() or token == ";"


def _is_bracket(token: str) -> bool:
    return token in ("[", "]", "{", "}")


def _is_delimiter(token: str) -> bool:
    return _is_whitespace_or_semicolon(token) or _is_bracket(token)


def _is_token_comment(token: str, previous_tokens: list[str]) -> bool:
    return token[0] == "#" and (
        not previous_tokens or previous_tokens[-1][-1:] in ("\n", ";")
    )


# test = """switch b {
#     # match a {
#      puts "Matched a" }
#     b { puts "Matched b" }
# }
# """
# print(tcl_minify(test))


# test = '''puts "escaped \\"quote\\""'''
# print(tcl_minify(test))
