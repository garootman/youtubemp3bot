import math
import os
import subprocess

from assist import now


def split_mp4_audio(filepath, chunklenstr, file_size, delete_original=False):
    if os.path.getsize(filepath) <= file_size:
        return [filepath], "", ""

    stt = now()
    directory, filename = os.path.split(filepath)
    basename, _ = os.path.splitext(filename)
    output_filename = os.path.join(directory, basename + "_%02d.mp4")

    command = [
        "ffmpeg",
        "-loglevel",
        "error",
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

    print("executing shell command: ", " ".join(command))
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    resfiles = os.listdir(directory)
    resfiles = [f for f in resfiles if f.startswith(os.path.splitext(filename)[0])]
    resfiles = [os.path.join(directory, f) for f in resfiles]
    # remove original file from resfiles
    resfiles = [i for i in resfiles if i != filepath]

    delfiles = [f for f in resfiles if os.path.getsize(f) < 2000]
    for f in delfiles:
        print("deleted", f)
        os.remove(f)

    if delete_original:
        print("deleted original", filepath)
        os.remove(filepath)

    return sorted(resfiles), result.stdout.decode(), result.stderr.decode()


def split_mp4_audio_shitty(file_path, file_size, delete_original=True):
    # from pydub import AudioSegment
    # gets path to mp4-file, opens as AudioSegment
    # opens a file
    # checks if it is larger that MAX_FILE_SIZE
    # if larger - splits it into parts, named as file_path_1.mp3, file_path_2.mp3, etc.
    # if NOT larger - only path of original filee
    # returns list of paths to files

    init_filesize = os.path.getsize(file_path)
    if init_filesize <= file_size:
        return [file_path]

    stt = now(True)

    num_chunks = math.ceil(os.path.getsize(file_path) / file_size)
    folder, filename = os.path.split(file_path)
    filename = filename.split(".")[0]
    print(
        f"Splitting audio {file_path} ({round(init_filesize/1024/1024, 3)} MB) into {num_chunks} chunks"
    )
    audio = AudioSegment.from_file(file_path, "mp4")
    print(f"Audio loaded in {now(True) - stt} ms")

    chunk_duration = math.ceil(len(audio) / num_chunks)
    chunks = [
        audio[i : i + chunk_duration] for i in range(0, len(audio), chunk_duration)
    ]

    # Save the chunks
    ret_paths = []
    for i, chunk in enumerate(chunks):
        ctt = now(True)
        chunk_path = os.path.join(folder, f"{filename}_{i}.mp4")
        chunk.export(chunk_path, format="mp4")
        ptt = now(True) - ctt
        print(f"Chunk {i} duration {len(chunk)} saved to {chunk_path} in {ptt} ms")
        ret_paths.append(chunk_path)

    # delete original file
    if delete_original:
        os.remove(file_path)
        print(f"Original file {file_path} deleted")

    # return the list of paths to the chunks

    return ret_paths


if __name__ == "__main__":
    file_path = "./audios/oNPnbjSoWL4.mp4"
    split_mp4_audio(file_path, 48 * 1024 * 1024, delete_original=False)
