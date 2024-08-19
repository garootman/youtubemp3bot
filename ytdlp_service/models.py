# file to describe models used in FastAPI server
from typing import Optional

from pydantic import BaseModel


class YTDLPFormatRequest(BaseModel):
    # will be used to get available formats by yt-dlp
    # optionally takes proxy
    url: str
    proxy: Optional[str] = None


class YTDLPDownloadRequest(BaseModel):
    # will be used to download video
    # takes url and format
    url: str
    format: str
    proxy: Optional[str] = None


class YTDLPFIleByTaskRequest(BaseModel):
    # will be used to download video
    # takes url and format
    task_id: str


class DownloadRequest(BaseModel):
    # will be used to simply download file by its name
    # file w    ill be taken from download folder
    file_name: str


class UploadTelegramRequest(BaseModel):
    # will be used to upload file to telegram
    file_name: Optional[str] = None
    task_id: Optional[str] = None
