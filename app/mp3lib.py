import math
import os
import subprocess

from assist import now


def split_mp4_audio(filepath, chunklenstr, file_size, timeout, delete_original=False):
    if os.path.getsize(filepath) <= file_size:
        return [filepath], "", ""

    stt = now(True)
    directory, filename = os.path.split(filepath)
    basename, _ = os.path.splitext(filename)
    output_filename = os.path.join(directory, basename + "_%02d.mp4")

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

    if delete_original:
        print("deleted original", filepath)
        os.remove(filepath)
    print("splitting done in", now(stt) - stt, "ms")
    return sorted(resfiles), result.stdout.decode(), result.stderr.decode()


if __name__ == "__main__":
    filepath = "./audios/u_pnia4Xhlw.mp4"
    split_mp4_audio(filepath, "00:40:00", 50 * 1024 * 1024, 60, delete_original=False)
