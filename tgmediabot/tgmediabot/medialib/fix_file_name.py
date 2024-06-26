import logging
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_file_name(filename: str, task_id: str) -> str:
    logger.debug(f"Fixing filename {filename} with task_id {task_id}")
    if os.path.exists(filename):
        return filename
    folder, file = os.path.split(filename)
    basename, extname = os.path.splitext(file)
    logger.debug(f"Folder: {folder}, basename: {basename}, extname: {extname}")
    # check if filename is found in folder
    # inlcude only files with task_id in filename
    # exclude .part files
    files = os.listdir(folder)
    files = [f for f in files if str(task_id) in f]
    files = [f for f in files if not f.endswith(".part")]
    # check if filename is found in folder
    if files:
        file = files[0]
        logger.info(f"FIXED: {file} found in {folder}")
        logger.debug(f"All matching files in folder: {files}")
        return os.path.join(folder, file)
    # check if basename is found in folder
    logger.critical(f"File {file} not found in {folder}")
    logger.debug(f"All files in folder: {files}")
    raise FileNotFoundError(f"File {file} not found in {folder}")
