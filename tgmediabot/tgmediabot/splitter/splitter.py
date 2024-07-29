import logging
import os
import subprocess

from .chunk_duration import get_chunk_duration_str
from .cleanup import delete_small_files

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def split_audio(filepath, chunklenstr, file_size, timeout):
    if os.path.getsize(filepath) <= file_size:
        logger.info(f"File {filepath} is smaller than {file_size}, not splitting")
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
        logger.debug("ffmpeg result:", result)
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
