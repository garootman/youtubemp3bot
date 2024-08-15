import logging
import os
import subprocess

from .chunk_duration import get_chunk_duration_str
from .cleanup import delete_small_files

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_bitrate(filepath):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=bit_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        filepath,
    ]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
        )
    except subprocess.TimeoutExpired:
        msg = "ffprobe subprocess expired timeout 10 seconds"
        logger.error(msg)
        return 0

    bitrate = int(result.stdout.decode().strip())
    return bitrate


def split_media(filepath, file_duration, max_size):
    filesize = os.path.getsize(filepath)
    timeout = file_duration + 10
    if filesize <= max_size:
        logger.info(f"File {filepath} is smaller than {max_size}, not splitting")
        return [filepath], "", ""
    # bitrate = get_bitrate(filepath)
    # get chunk_size with 10% overhead
    chunklenstr = get_chunk_duration_str(file_duration, filesize, max_size)

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
        "-y",  # force rewrite
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
    logger.info(f"Splitting {filepath} into {chunklenstr} chunks")
    try:
        command_str = " ".join([str(i) for i in command])
        logger.debug(f"Running ffmpeg command: {command_str}")
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        msg = f"ffmpeg subprocess finished with code {result.returncode}"
        logger.debug(msg)
    except subprocess.TimeoutExpired:
        msg = f"ffmpeg subprocess expired timeout {timeout} seconds"
        logger.error(msg)
        return [], "", msg

    # delfiles = delete_small_files(directory, basename, 2000)

    resfiles = os.listdir(directory)
    resfiles = [f for f in resfiles if f.startswith(basename) and f.endswith(file_ext)]
    resfiles = [os.path.join(directory, f) for f in resfiles]
    resfiles = [i for i in resfiles if i != filepath]
    logger.debug(f"Split files: {resfiles}")

    return sorted(resfiles), result.stdout.decode(), result.stderr.decode()
