import os

import pytest

from tgmediabot.splitter import convert_audio, delete_files_by_chunk

# parepare files: make a copy of "test_cutting.m4a.test" to "test_cutting.m4a"
# this is done to avoid modifying the original file and bypassing .gitignore

folder = "test_audio"
filepath = os.path.join(folder, "test_cutting.m4a")
timeout = 100  # seconds
init_path = os.path.join("tests", "unit", "test_cutting.m4a.test")


def test_prepare():

    os.system(f"mkdir -p {folder}")
    os.system(f"cp {init_path} {filepath}")
    assert os.path.exists(filepath)


# test sequence:
# check correct workflow: returns the path to the converted file in mp3
# assert that the file exists and is not empty


def test_convert_audio():
    resfile, stderr = convert_audio(filepath, timeout)
    assert os.path.exists(resfile)
    assert os.path.getsize(resfile) > 3000


def test_cleanup():
    x = delete_files_by_chunk(folder, "test_cutting")
    assert len(x) == 2
    # delete the folder
    os.system(f"rm -rf {folder}")


if __name__ == "__main__":
    test_prepare()
    test_convert_audio()
    test_cleanup()
    print("All tests passed")
