class TclToken:
    __slots__ = ("contents", "ending_whitespace")

    def __init__(self, contents: str, ending_whitespace: str = "") -> None:
        self.contents: str = contents
        self.ending_whitespace: str = ending_whitespace

    def __getitem__(self, key: str) -> str:
        return self.contents[key]

    def __str__(self) -> str:
        return self.contents + self.ending_whitespace


def tcl_parse(source: str) -> list[TclToken]:  # noqa: PLR0912
    token_start: int = 0
    token_end: int = 0
    source_end: int = len(source)

    tokens: list[TclToken] = []

    def find_token_end(token: str) -> int:
        nonlocal source, token_start
        return source.find(token, token_start + 1)

    while token_start < source_end:
        first_char: str = source[token_start]
        if first_char.isspace():
            if tokens and tokens[-1].ending_whitespace != "\n":
                tokens[-1].ending_whitespace = first_char
            token_start += 1
            continue

        if first_char == "#":
            if tokens:
                tokens[-1].ending_whitespace = "\n"
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
            tokens.append(TclToken(string_token))
        else:
            token_end = token_start + 1
            while token_end < source_end and not source[token_end].isspace():
                token_end += 1
            token: str = source[token_start:token_end]
            if token == "\\" and source[token_end : token_end + 1] == "\n":
                token_end += 1
            else:
                if tokens and token == "}":
                    tokens[-1].ending_whitespace = ""

                tokens.append(TclToken(token))

        token_start = token_end

    if tokens and tokens[-1].ending_whitespace != "":
        tokens[-1].ending_whitespace = ""

    return tokens


def tcl_unparse(tokens: list[TclToken]) -> str:
    return "".join(str(token) for token in tokens)


def tcl_minify(source: str) -> str:
    return tcl_unparse(tcl_parse(source))


# test = """
# uplevel \\#0 {
#     package require msgcat 1.6
#     if { $::tcl_platform(platform) eq {windows} } {
#         if { [catch { package require registry 1.1 }] } {
#             namespace eval ::tcl::clock [list variable NoRegistry {}]
#         }  # some comment
#     }
# }
# namespace eval ::tcl::clock \\
# [list variable LibDir [info library]]
# """
# print(tcl_minify(test))
