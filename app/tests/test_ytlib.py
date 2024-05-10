import sys

import pytest

sys.path.append("../")

correct_id = "rX3W5evpeJE"
broken_id = "rX3W5evpeJX"
correct_path = "https://www.youtube.com/watch?v=rX3W5evpeJE"
broken_path = "https://www.youtube.com/watch?v=rX3W5evpeJX"


def test_link_parsing():
    from ytlib import universal_check_link

    assert (
        universal_check_link("https://youtu.be/YwAvrJCyZ04?si=Xwzge_T3Um4ye0Ec")
        == "YwAvrJCyZ04"
    )
    assert (
        universal_check_link("https://www.youtube.com/watch?v=YwAvrJCyZ04")
        == "YwAvrJCyZ04"
    )
    assert (
        universal_check_link("https://www.youtube.com/embed/YwAvrJCyZ04")
        == "YwAvrJCyZ04"
    )
    assert (
        universal_check_link("https://www.youtube.com/v/YwAvrJCyZ04") == "YwAvrJCyZ04"
    )
    assert (
        universal_check_link("https://www.youtube.com/playlist?list=YwAvrJCyZ04")
        == "YwAvrJCyZ04"
    )


def test_video_download():
    # test downloading a video
    from ytlib import download_video

    vid_id = "rX3W5evpeJE"
    assert download_video(vid_id, "./videos") == f"./videos/{vid_id}.mp4"


def test_fail_download():
    # test failing to download a video
    from ytlib import download_video

    vid_id = "rX3W5evpeJX"
    assert download_video(vid_id, "./videos") == None
