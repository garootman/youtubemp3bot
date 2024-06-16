import os
import subprocess

from .chunk_duration import get_chunk_duration_str
from .cleanup import delete_small_files


def split_audio(filepath, chunklenstr, file_size, timeout):
    if os.path.getsize(filepath) <= file_size:
        return [filepath], "", ""

    directory, filename = os.path.split(filepath)
    basename, file_ext = os.path.splitext(filename)
    output_filename = os.path.join(directory, basename + "_%02d" + file_ext)
    if not directory:
        directory = "."
        filepath = os.path.join(directory, filename)

    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        filepath,
        "-c",
        "copy",
        "-map",
        "0",
        "-segment_time",
        chunklenstr,
        "-f",
        "segment",
        "-reset_timestamps",
        "1",
        output_filename,
    ]
    print(f"Splitting {filepath} into {chunklenstr} chunks")
    try:
        print("Running ffmpeg command:", command)
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        print("ffmpeg result:", result)
    except subprocess.TimeoutExpired:
        msg = "ffmpeg subprocess expired timeuot", timeout, "seconds"
        print(msg)
        return [], "", msg

    # delfiles = delete_small_files(directory, basename, 2000)

    resfiles = os.listdir(directory)
    resfiles = [f for f in resfiles if f.startswith(basename) and f.endswith(file_ext)]
    resfiles = [os.path.join(directory, f) for f in resfiles]
    resfiles = [i for i in resfiles if i != filepath]

    return sorted(resfiles), result.stdout.decode(), result.stderr.decode()
