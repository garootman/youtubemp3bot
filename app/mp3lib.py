import math
import os
import subprocess

from assist import now


def split_audio(filepath, chunklenstr, file_size, timeout):
    if os.path.getsize(filepath) <= file_size:
        return [filepath], "", ""

    stt = now(True)
    directory, filename = os.path.split(filepath)
    basename, file_ext = os.path.splitext(filename)
    output_filename = os.path.join(directory, basename + "_%02d" + file_ext)

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

    print("executing shell command: ", " ".join(command))
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        msg = "ffmpeg subprocess expired timeuot", timeout, "seconds"
        print(msg)
        return [], "", msg

    resfiles = os.listdir(directory)
    resfiles = [f for f in resfiles if f.startswith(os.path.splitext(filename)[0])]
    resfiles = [os.path.join(directory, f) for f in resfiles]
    # remove original file from resfiles
    resfiles = [i for i in resfiles if i != filepath]

    delfiles = [f for f in resfiles if os.path.getsize(f) < 2000]
    for f in delfiles:
        print("deleted", f)
        os.remove(f)

    print("splitting done in", now(stt) - stt, "ms")
    return sorted(resfiles), result.stdout.decode(), result.stderr.decode()
