import json
import os
import subprocess

from assist import new_id

DOWNLOAD_FOLDER = "downloads"


def uniqueid(folder=DOWNLOAD_FOLDER):
    curr_dl_files = os.listdir(folder)
    while True:
        task_id = new_id(20)
        if task_id not in str(curr_dl_files):
            return task_id


def find_in_downloads(task_id):
    curr_dl_files = os.listdir(DOWNLOAD_FOLDER)
    print(f"looking for {task_id} in {curr_dl_files}")
    for file in curr_dl_files:
        if task_id in file:
            # exclude ytdlp files and all kinds of logs and temporary files
            if ".ytdlp" in file or ".log" in file or ".part" in file or ".frag" in file:
                continue
            print(f"File found at path: {os.path.join(DOWNLOAD_FOLDER, file)}")
            return file
    print(f"File not found for task_id: {task_id} at {DOWNLOAD_FOLDER}")
    return None


def start_download(url, format, proxy=None):
    task_id = uniqueid()
    output_template = f"{task_id}.%(ext)s"
    dl_path = os.path.join(DOWNLOAD_FOLDER, output_template)
    command = ["yt-dlp", "-f", format, "-o", dl_path, url]
    if proxy:
        command.append("--proxy")
        command.append(proxy)

    command_str = " ".join(command)
    print(f"Running command: {command_str}")

    # start download in a backgreound subprocess

    proc = subprocess.Popen(command)
    print(f"Download started with PID: {proc.pid}")

    return task_id
