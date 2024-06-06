DOWNLOAD_OPTIONS = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "outtmpl": "",
    "bypass_geoblock": True,
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "no_warnings": True,  # silent mode
    # client mozilla
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    },
}

GETINFO_OPTIONS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "format": "best",
}
