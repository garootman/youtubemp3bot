import logging
import os
import subprocess

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_resolution(filepath, timeout=60):
    directory, filename = os.path.split(filepath)
    basename, file_ext = os.path.splitext(filename)
    output_filename = os.path.join(directory, basename + file_ext)
    if not directory:
        directory = "."
        filepath = os.path.join(directory, filename)

    # if file not exists: return error
    if not os.path.exists(filepath):
        msg = f"File {filepath} not exists"
        logger.error(msg)
        return "", msg

    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        filepath,
    ]

    logger.info(f"Getting resolution for {filepath}")
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
        return 0, 0

    logger.debug(f"Got resolution: {result.stdout}")
    resolution = result.stdout.decode("utf-8").strip()
    if not resolution:
        msg = f"ffmpeg returned empty resolution"
        logger.error(msg)
        return 0, 0

    width, height = resolution.split("x")
    width, height = int(width), int(height)
    return width, height
