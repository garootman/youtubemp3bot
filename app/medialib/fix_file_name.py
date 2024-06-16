import os


def fix_file_name(filename: str, task_id: str) -> str:
    if os.path.exists(filename):
        return filename
    folder, file = os.path.split(filename)
    basename, extname = os.path.splitext(file)
    # check if filename is found in folder
    # inlcude only files with task_id in filename
    # exclude .part files
    files = os.listdir(folder)
    files = [f for f in files if str(task_id) in f]
    files = [f for f in files if not f.endswith(".part")]
    # check if filename is found in folder
    if files:
        file = files[0]
        print(f"FIXED: {file} found in {folder}")
        return os.path.join(folder, file)
    # check if basename is found in folder
    raise FileNotFoundError(f"File {file} not found in {folder}")
