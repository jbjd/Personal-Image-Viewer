import os


def read_utf8_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fp:
        return fp.read()


def write_utf8_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)
