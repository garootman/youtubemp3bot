import logging
import time

import requests

from tgmediabot.envs import (
    MEDIASERVER_IP,
    MEDIASERVER_PASSWORD,
    MEDIASERVER_PORT,
    MEDIASERVER_USER,
)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


auth = (MEDIASERVER_USER, MEDIASERVER_PASSWORD)
mediaserver_url = f"http://{MEDIASERVER_IP}:{MEDIASERVER_PORT}"


def ping_mediaserver():
    ping_endpoint = f"{mediaserver_url}"
    response = requests.get(ping_endpoint, timeout=10, auth=auth)
    if response.status_code == 200:
        return True
    else:
        print(response.status_code, response.text)
        return False


def get_media_info_remote(url, proxy=None):
    logger.info(f"Getting media info remotely for {url}")
    endpoint = f"{mediaserver_url}/ytdlp-formats"
    data = {"url": url, "proxy": proxy}
    response = requests.get(endpoint, json=data, timeout=10, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}


def download_media_remote(url, mediaformat, proxy=None):
    start_dl_endpoint = f"{mediaserver_url}/ytdlp-download"
    data = {"url": url, "format": mediaformat, "proxy": proxy}
    response = requests.post(start_dl_endpoint, json=data, timeout=10, auth=auth)
    print(response.status_code, response.text)
    if response.status_code != 200:
        logger.error(f"Error starting download task: {response.text}")
        return None
    elif "task_id" not in response.json() or "error" in response.json():
        logger.error(f"Error starting download task: {response.json()}")
        return None
    else:
        remote_task_id = response.json()["task_id"]
        logger.info(f"Started download task {remote_task_id} for {url}")
        return remote_task_id


def check_download_status(remote_task_id, dltimeout=600):
    # check download status for dltimeout seconds every 5 seconds
    check_dl_endpoint = f"http://{MEDIASERVER_IP}:{MEDIASERVER_PORT}/ytdlp-filename"
    start_time = time.time()
    logger.info(f"Checking download status for task {remote_task_id}")
    while time.time() - start_time < dltimeout:
        time.sleep(5)
        response = requests.get(
            check_dl_endpoint, json={"task_id": remote_task_id}, timeout=10, auth=auth
        )
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Download status for task {remote_task_id}: {data}")
            if "filename" in data:
                if data["filename"].endswith(".fail"):
                    return {"error": f"Download failed"}
                if data["istemp"] == True:
                    logger.info(
                        f"Download task {remote_task_id} is still in progress..."
                    )
                    continue
                filename = data["filename"]
                filesize = data["filesize"]
                logger.info(f"Mediaserver has {filesize} bytes to {filename}")
                return data
            # elif 'error' in data:
            #    return data
            else:
                pass
        else:
            pass
            # return {"error": response.text}
    else:
        return {"error": "Download timeout for task {remote_task_id}"}


def download_file(remote_filename, filepath):
    download_endpoint = f"{mediaserver_url}/download/{remote_filename}"
    response = requests.get(download_endpoint, timeout=120, auth=auth)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        filesize = len(response.content)
        logger.info(f"Downloaded {remote_filename} to {filepath}")
        return {"status": "success", "filename": remote_filename, "filesize": filesize}


def send_to_telegram(task_id):
    post_tg_endpoint = f"{mediaserver_url}/upload-to-telegram"
    body = {"task_id": task_id}
    response = requests.post(post_tg_endpoint, json=body, timeout=10, auth=auth)
    # {"status": "success", "tg_file_id": "Unknown", "task": "upload_to_telegram", "filesize": filesize}
    if response.status_code == 200:  # and "filesize" in response.json():
        return True
    logger.error(f"Error sending to telegram: {response.status_code} {response.text}")
    return False


# +===================================


def test_ping_mediaserver():
    assert ping_mediaserver() == True


def test_get_media_info_remote():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    proxy = "http://2dh5uiDTSX:vxQCr3xYC9Pbg46@137.59.7.64:5608"  # None
    info = get_media_info_remote(url, proxy)
    assert "formats" in info


def test_download_media_remote():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mediaformat = "mp3"
    proxy = "http://2dh5uiDTSX:vxQCr3xYC9Pbg46@137.59.7.64:5608"  # None
    remtid = download_media_remote(url, mediaformat, proxy)
    assert remtid


def test_check_download_status():
    remtid = "testvideoasdasdasd"
    data = check_download_status(remtid)
    assert data["istemp"] == False
    assert data["filesize"] > 0
    assert "filename" in data


def test_send_to_telegram():
    remtid = "testvideoasdasdasd"
    assert send_to_telegram(remtid) == True


if __name__ == "__main__":
    test_ping_mediaserver()
    test_get_media_info_remote()
    test_download_media_remote()
    test_check_download_status()
    test_send_to_telegram()

    print("All tests passed!")
