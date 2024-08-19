import requests

PORT = 8000  # 16378
base_url = f"http://localhost:{PORT}"

yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
proxy = "http://2dh5uiDTSX:vxQCr3xYC9Pbg46@137.59.7.64:5608"  # None
format = "136+140"
task_id = "test"


def test_ytdlp_formats():
    endpoint = "/ytdlp-formats"
    req_url = base_url + endpoint
    # "http://localhost:8000/ytdlp-formats",
    response = requests.get(req_url, json={"url": yt_url, "proxy": proxy})
    assert response.json() != {}


def test_ytdlp_download():
    endpoint = "/ytdlp-download"
    req_url = base_url + endpoint
    body = {"url": yt_url, "format": format, "proxy": proxy}
    response = requests.post(req_url, json=body)
    assert response.json() != {}


def test_ytdlp_file_by_task():
    endpoint = "/ytdlp-filename"
    req_url = base_url + endpoint

    body = {"task_id": task_id}
    response = requests.get(req_url, json=body)
    # print(response.json())
    # {'status': 'success', 'filename': 'test.txt'}
    assert response.json()["status"] == "success"
    assert response.json()["filename"] == "test.txt"


def test_download_file():
    # put a file in the downloads folder
    filepath = "downloads/test.txt"
    with open(filepath, "w") as f:
        f.write("lorem ipsum blet")
    endpoint = "/download/test.txt"
    req_url = base_url + endpoint
    response = requests.get(req_url)
    assert response.status_code == 200
    assert response.content == b"lorem ipsum blet"


def test_tg_upload():
    endpoint = "/upload-to-telegram"
    req_url = base_url + endpoint

    # 0. test with no file_name or task_id
    body = {}
    response = requests.post(req_url, json=body)
    assert response.status_code == 400

    # 1. test with file_name
    body = {"file_name": "test.txt"}
    response = requests.post(req_url, json=body)
    # {"status":"success","tg_file_id":5341441747027253628}
    assert response.json()["status"] == "success"

    # 2. test with task_id
    body = {"task_id": "asdasd0987654321"}
    response = requests.post(req_url, json=body)
    assert response.json()["status"] == "success"


def test_remove_bg():
    endpoint = "/remove-bg"
    req_url = base_url + endpoint
    filepath = "testdata/test.jpg"
    # upload a file to endpoint with post
    files = {"file": open(filepath, "rb")}
    response = requests.post(req_url, files=files)
    assert response.status_code == 200
    # assert that response is a file
    assert response.headers["Content-Type"] == "image/png"
    # save response to file
    with open("testdata/test_remove_bg.png", "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    test_remove_bg()
    test_ytdlp_formats()
    test_ytdlp_download()
    test_ytdlp_file_by_task()
    test_download_file()
    test_tg_upload()
    print("All tests passed")
