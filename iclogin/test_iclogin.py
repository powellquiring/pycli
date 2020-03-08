import iclogin
import pytest
import click
from pathlib import Path


def create_dir(tmpdir, file_contents):
    dir = Path(str(tmpdir))
    for (f, contents) in file_contents.items():
        with (dir / f).open(mode="w") as file:
            file.write(contents)


def create_and_parse_dir(tmpdir, file_contents):
    create_dir(tmpdir, file_contents)
    return iclogin.parse_dir(Path(tmpdir))


def create_files_find_target(tmpdir, target, files):
    dir = Path(str(tmpdir))
    for f in files:
        with (dir / f).open(mode="w") as file:
            file.write('{"apikey": "a"}')
    return iclogin.find_target(dir, target)


def test_find_file_0(tmpdir):
    create_dir(tmpdir, {"a.json": '{"apikey": "abcd"}'})
    (f, apikey, error) = iclogin.find_target(tmpdir, "a")
    assert apikey == "abcd"
    assert f == Path(tmpdir) / "a.json"


def test_find_file_1(tmpdir):
    (f, apikey, error) = iclogin.find_target(tmpdir, "a")
    assert apikey == None
    assert f == None
    assert error != None


def test_find_file_2(tmpdir):
    create_dir(tmpdir, {"a.json": '{"apikey": "abcd"}'})
    (f, apikey, error) = iclogin.find_target(tmpdir, "b")
    assert apikey == None
    assert f == None
    assert error != None


def test_find_file_3(tmpdir):
    create_dir(
        tmpdir, {"a.json": '{"apikey": "abcd"}', "a.apikey.json": '{"apikey": "aa"}'}
    )
    (f, apikey, error) = iclogin.find_target(tmpdir, "b")
    assert apikey == None
    assert f == None
    assert error != None


def test_find_target_0(tmpdir):
    (f, apikey, errs) = create_files_find_target(tmpdir, "a", ["a.json"])
    assert errs == None
    assert f == Path(tmpdir) / "a.json"


def test_find_target_1(tmpdir):
    (f, apikey, errs) = create_files_find_target(
        tmpdir, "b", ["a.json", "b.json", "c.json"]
    )
    assert f == Path(tmpdir) / "b.json"


def test_find_target_2(tmpdir):
    (f, apikey, errs) = create_files_find_target(tmpdir, "a", ["a.apiKey.json"])
    assert f == Path(tmpdir) / "a.apiKey.json"


def test_find_target_3(tmpdir):
    (f, apikey, errs) = create_files_find_target(tmpdir, "a", ["a"])
    assert f == Path(tmpdir) / "a"


def test_parse_dir(tmpdir):
    (goods, errors) = create_and_parse_dir(tmpdir, {})
    assert len(goods) == 0
    assert len(errors) == 0


def test_parse_dir(tmpdir):
    (goods, errors) = create_and_parse_dir(tmpdir, {"a.json": '{"apikey": "abcd"}'})
    assert len(goods) == 1
    assert len(errors) == 0
