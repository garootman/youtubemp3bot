import os
import shutil

import pytest

from tgmediabot.splitter import convert_audio, delete_files_by_chunk

# parepare files: make a copy of "test_cutting.m4a.test" to "test_cutting.m4a"
# this is done to avoid modifying the original file and bypassing .gitignore

folder = "test_audio"
filepath = os.path.join(folder, "test_cutting.m4a")
timeout = 100  # seconds
init_path = os.path.join("tests", "unit", "test_cutting.m4a.test")


def test_prepare():
    os.makedirs(folder, exist_ok=True)
    shutil.copy(init_path, filepath)
    assert os.path.exists(filepath)


def test_convert_audio():
    resfile, stderr = convert_audio(filepath, timeout)
    assert os.path.exists(resfile)
    assert os.path.getsize(resfile) > 3000


def test_cleanup():
    x = delete_files_by_chunk(folder, "test_cutting")
    assert len(x) == 1
    shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    test_prepare()
    test_convert_audio()
    test_cleanup()
    print("All tests passed")
