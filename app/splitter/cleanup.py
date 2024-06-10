import os


def delete_files_by_chunk(folder, chunk):
    # deletes files in folder, that have chunk in filename
    deleted = []
    for file in os.listdir(folder):
        if chunk in file:
            filepath = os.path.join(folder, file)
            os.remove(filepath)
            deleted.append(filepath)
            print(f"Deleted {filepath}")
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
                print(f"Deleted {filepath}")
    return deleted
