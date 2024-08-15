import math


def get_chunk_duration_str(file_duration, file_size, max_file_size):
    total_chunks = math.ceil(file_size / max_file_size)
    chunk_duration = math.floor(file_duration / total_chunks)  #
    minutes = math.floor(chunk_duration / 60)
    minutes = max(minutes, 1)
    chunk_duration = minutes * 60
    hours = chunk_duration // 3600
    minutes = (chunk_duration % 3600) // 60
    seconds = 0
    duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    return duration_str


# durstr = get_chunk_duration_str(13 * 60, 210 * 1024 * 1024, 48 * 1024 * 1024)
# print(durstr)
