import logging
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def delete_files_by_chunk(folder, chunk):
    # deletes files in folder, that have chunk in filename
    deleted = []
    for file in os.listdir(folder):
        if chunk in file:
            filepath = os.path.join(folder, file)
            os.remove(filepath)
            deleted.append(filepath)
            logger.info(f"Deleted by chunk {filepath}")
    return deleted


def delete_small_files(folder, chunk, size):
    # deletes files in folder, that have chunk in filename and size less than size
    deleted = []
    for file in os.listdir(folder):
        if chunk in file:
            filepath = os.path.join(folder, file)
            if os.path.getsize(filepath) < size:
                os.remove(filepath)
                deleted.append(filepath)
                logger.info(f"Deleted by size less than {size} {filepath}")
    return deleted
