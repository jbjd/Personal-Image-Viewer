import os


def read_file_utf8(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fp:
        return fp.read()


def write_file_utf8(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)


def make_folder_and_write_file_utf8(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)
