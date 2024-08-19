# uses yt-dlp to get available formats for given url

import json
import os
import subprocess

from assist import new_id

json_folder = "jsondata"
json_folder = os.path.join(os.path.dirname(__file__), json_folder)
if not os.path.exists(json_folder):
    os.makedirs(json_folder)


def get_formats(url, proxy=None, cleanup=True):
    # uses subprocess to run yt-dlp command
    # returns available formats for given url in json format
    while True:
        resfile_path = os.path.join(json_folder, new_id(10, False) + ".json")
        errfile_path = os.path.join(json_folder, new_id(10, False) + ".err")
        if not os.path.exists(resfile_path):
            break
    # a command to get available formats for given url, save
    # saves the output to json file
    command = ["yt-dlp", "-J", url]
    if proxy:
        command.append("--proxy")
        command.append(proxy)

    resfile = open(resfile_path, "w")
    errfile = open(errfile_path, "w")
    subprocess.run(command, stdout=resfile, stderr=errfile)
    resfile.close()
    errfile.close()

    # read the json file and return the data
    # also return error if any
    with open(resfile_path, "r") as file:
        data = json.load(file)
    with open(errfile_path, "r") as file:
        error = file.read()

    if cleanup:
        os.remove(resfile_path)
        os.remove(errfile_path)
    else:
        # re-dump data with indent for better readability
        with open(resfile_path, "w") as file:
            json.dump(data, file, indent=4)
    if data:
        error = None
    return data, error
