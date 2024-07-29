import logging
import os
import subprocess

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def convert_audio(filepath, timeout=60):

    directory, filename = os.path.split(filepath)
    basename, file_ext = os.path.splitext(filename)
    new_ext = ".mp3"
    output_filename = os.path.join(directory, basename + new_ext)
    if not directory:
        directory = "."
        filepath = os.path.join(directory, filename)

    # if file not exists: return error
    if not os.path.exists(filepath):
        msg = f"File {filepath} not exists"
        logger.error(msg)
        return "", msg

    command = [
        "ffmpeg",
        "-loglevel",
        "error",  # только ошибки
        "-y",  # force rewrite
        "-i",
        filepath,  # входной файл
        # "-ar", "44100",  # частота дискретизации
        # "-q:a", "2",  # качество аудио
        # "-b:a", "128k",  # битрейт аудио
        "-f",
        "mp3",  # выходной формат
        output_filename,  # выходной файл
    ]

    logger.info(f"Converting {filepath} mp3 file")
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
        return "", msg

    logger.debug(f"Converted files to mp3: {output_filename}")

    return output_filename, ""
