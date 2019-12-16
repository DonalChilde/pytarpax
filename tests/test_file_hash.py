import hashlib
import string
from pathlib import Path

import pytest

from pytarpax.lib import file_hash


def test_open_type():
    file_path = Path(__file__)
    with open(file_path, "rb") as binary_read:
        print(type(binary_read))
    with open(file_path, "r") as binary_read:
        print(type(binary_read))


def test_hashlib_type():
    hash_lib = hashlib.md5()
    print(type(hash_lib))
    hash_lib = hashlib.blake2b()
    print(type(hash_lib))


def test_guarantee_hashers(capsys):
    hashers = hashlib.algorithms_guaranteed
    with capsys.disabled():
        print(hashers)


def is_hex(test_string: str):
    """test whether a string contains only hexadecimal digits

    https://stackoverflow.com/a/11592292/105844

    Arguments:
        s {str} -- [description]

    Returns:
        [type] -- [description]
    """
    hex_digits = set(string.hexdigits)
    # if test_string is long, then it is faster to check against a set
    return all(c in hex_digits for c in test_string)


def test_file_hash():
    # file_path = Path(__file__)
    file_path = Path(__file__)
    result = file_hash.get_file_hash(file_path, "md5")
    md5_hash = md5sum(file_path)
    assert is_hex(result.file_hash)
    assert result.file_hash == md5_hash
    assert result.file_path == file_path
    assert result.hash_method == "md5"
    # with capsys.disabled():
    #     print([result.file_hash, md5_hash, file_path])


def md5sum(filename, blocksize=65536):
    hash_ = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash_.update(block)
    return hash_.hexdigest()


def test_file_hash_generator():
    dir_path = Path("/home/chad/projects/utilities/tests/utilities")
    file_path_list = list(dir_path.glob("**/*.py"))
    f_gen = file_hash.get_file_hash_generator(file_path_list, "md5")
    print("individual")
    for file_path in file_path_list:
        print(file_hash.get_file_hash(file_path, "md5"))
    print("generator")
    for x in f_gen:
        print(x)
        assert is_hex(x[1])


def test_file_hash_generator2():
    dir_path = Path(__file__).parent
    file_path_list = dir_path.glob("**/*")
    f_gen = file_hash.get_file_hash_generator(file_path_list, "md5")
    total_count = 0
    for count, value in enumerate(f_gen):
        total_count = count + 1
        assert isinstance(value, file_hash.FileHash)
    assert total_count > 1
    print(f"Files: {total_count}")


def make_test_files():
    parent_dir = Path(__file__).parent
    test_path_1 = Path(str(parent_dir) + "/test_data/test_file_1.txt")
    test_path_2 = Path(str(parent_dir) + "/test_data/test_file_2.txt")
    test_path_3 = Path(str(parent_dir) + "/test_data/test_file_3.txt")
    test_path_4 = Path(str(parent_dir) + "/test_data/test_file_4.txt")
    test_data = {
        "test_data_1": {"data": b"", "test_path": test_path_1,},
        "test_data_2": {
            "data": b"this is a single line of text",
            "test_path": test_path_2,
        },
        "test_data_3": {
            "data": b"this is several lines of text.\nThe second line.\nThe third line.",
            "test_path": test_path_3,
        },
        "test_data_4": {
            "data": b"""A tripple quote
                        multiline
                        string.
                        """,
            "test_path": test_path_4,
        },
    }

    for _, value in test_data.items():
        with open(value["test_path"], "w+b") as out_file:
            out_file.write(value["data"])
    return test_data


def test_all_hashers():
    test_data = make_test_files()
    for hash_method in file_hash.HASH_METHODS:
        print(f"hash_method: {hash_method}")
        for _, value in test_data.items():
            hasher = file_hash.get_hasher(hash_method)
            hasher.update(value["data"])
            string_hash = hasher.hexdigest()
            file_hash_data = file_hash.get_file_hash(value["test_path"], hash_method)
            assert string_hash == file_hash_data.file_hash
