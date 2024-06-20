import os

import pytest

from splitter import delete_files_by_chunk, delete_small_files, split_audio

# parepare files: make a copy of "test_cutting.m4a.test" to "test_cutting.m4a"
# this is done to avoid modifying the original file and bypassing .gitignore

folder = "test_audio"
filepath = os.path.join(folder, "test_cutting.m4a")
chunklenstr = "00:10:00"  # 10 minutes
file_size = 1 * 1024 * 1024  # 1 MB
timeout = 3  # 3 seconds


def test_prepare():
    os.system(f"mkdir -p {folder}")
    os.system(f"cp test_cutting.m4a.test {filepath}")
    assert os.path.exists(filepath)


def test_correct_file_split():
    resfiles, stdout, stderr = split_audio(filepath, chunklenstr, file_size, timeout)
    assert len(resfiles) == 2
    assert os.path.getsize(resfiles[0]) > 3000
    assert os.path.getsize(resfiles[1]) > 3000
    print(resfiles)


def test_file_not_found():
    filepath = "test_cutting_not_found.m4a"
    resfiles, stdout, stderr = split_audio(filepath, chunklenstr, file_size, timeout)
    assert resfiles == []
    assert "not found" in stderr.lower()


def test_big_filesize_one_chunk():
    file_size = 100 * 1024 * 1024  # 100 MB
    resfiles, stdout, stderr = split_audio(filepath, chunklenstr, file_size, timeout)
    assert len(resfiles) == 1
    assert os.path.getsize(resfiles[0]) > 3000


# cleanup: remove the copied file and the split files


def test_cleanup():
    x = delete_files_by_chunk(folder, "test_cutting")
    assert len(x) == 3
    # delete the folder
    os.system(f"rm -rf {folder}")


if __name__ == "__main__":
    test_prepare()
    test_correct_file_split()
    test_file_not_found()
    test_big_filesize_one_chunk()
    test_cleanup()
