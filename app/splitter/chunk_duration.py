import math


def get_chunk_duration_str(file_duration, file_size, max_file_size):
    total_chunks = math.ceil(file_size / max_file_size)
    chunk_duration = math.ceil(file_duration / total_chunks)  #
    minutes = math.ceil(chunk_duration / 60)
    chunk_duration = minutes * 60
    hours = chunk_duration // 3600
    minutes = (chunk_duration % 3600) // 60
    seconds = 0
    duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    return duration_str
