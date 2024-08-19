import os
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from models import (
    UploadTelegramRequest,
    YTDLPDownloadRequest,
    YTDLPFIleByTaskRequest,
    YTDLPFormatRequest,
)
from PIL import Image
from pydantic import BaseModel
from rembg import remove

downloads_folder = "downloads"
downloads_folder = os.path.join(os.path.dirname(__file__), downloads_folder)
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)


from tg_upload import upload_file
from ytdlp_download import find_in_downloads, start_download
from ytdlp_getformats import get_formats

DOWNLOAD_FOLDER = "downloads"

import logging

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    hddstat = os.statvfs("/")
    hdd_space_left_gb = round(
        hddstat.f_bsize * hddstat.f_bavail / 1024 / 1024 / 1024, 2
    )
    downloads_folder_size = sum(
        os.path.getsize(f) for f in os.listdir(downloads_folder) if os.path.isfile(f)
    )
    dl_size_gb = round(downloads_folder_size / 1024 / 1024 / 1024, 2)
    return {
        "message": "YTDLP Service OK",
        "total_hdd_use": dl_size_gb,
        "hdd_free_gb": hdd_space_left_gb,
    }


@app.post("/remove-bg/")
async def remove_background(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file part")
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")
    try:
        image = Image.open(BytesIO(await file.read()))
        result = remove(image)
        output = BytesIO()
        result.save(output, format="PNG")
        output.seek(0)
        output_path = "result.png"
        with open(output_path, "wb") as f:
            f.write(output.getvalue())
        return FileResponse(
            output_path,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=result.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ytdlp-formats")
def get_ytdlp_formats(request: YTDLPFormatRequest):
    url = request.url
    proxy = request.proxy
    print(f"Getting formats for {url} with proxy {proxy}")
    jsondata, error = get_formats(url, proxy=proxy, cleanup=False)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return jsondata


@app.post("/ytdlp-download")
# a POST method to start a download task
def ytdlp_download(request: YTDLPDownloadRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not request.format:
        raise HTTPException(status_code=400, detail="Format is required")
    print(
        f"Starting download for {request.url} with format {request.format} and proxy {request.proxy}"
    )
    task_id = start_download(request.url, request.format, proxy=request.proxy)
    return {"status": "success", "task_id": task_id}


@app.get("/ytdlp-filename")
# a POST method to get a filename of a download task
def ytdlp_file_by_task(request: YTDLPFIleByTaskRequest):
    if not request.task_id:
        raise HTTPException(status_code=400, detail="task_id is required")

    filename = find_in_downloads(request.task_id)
    if not filename:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "success", "filename": filename}


# a method to download a file by its name
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = os.path.join(downloads_folder, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# a method to upload a file to Telegram


@app.post("/upload-to-telegram")
async def upload_to_telegram(request: UploadTelegramRequest):
    file_name = request.file_name
    task_id = request.task_id
    if not file_name and not task_id:
        raise HTTPException(
            status_code=400, detail="Either file_name or task_id is required"
        )
    elif task_id:
        file_name = find_in_downloads(task_id)
    file_path = os.path.join(downloads_folder, file_name)
    if not file_path or not os.path.exists(file_path):
        print(f"File at {file_path} not found")
        raise HTTPException(status_code=404, detail=f"File at {file_path} not found")
    tg_file_id = await upload_file(file_path)
    return {"status": "success", "tg_file_id": tg_file_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app", host="0.0.0.0", port=16378, reload=True, log_level="debug"
    )
