import pytest


def test_import_tgmediabot():
    import tgmediabot.assist
    import tgmediabot.chatmanager
    import tgmediabot.envs

    # import tgmediabot.database
    import tgmediabot.medialib
    import tgmediabot.modelmanager
    import tgmediabot.paywall
    import tgmediabot.proxies
    import tgmediabot.splitter
    import tgmediabot.taskmanager
    from tgmediabot.taskprocessor import TaskProcessor
    import tgmediabot.telelib


if __name__ == "__main__":
    test_import_tgmediabot()
    print("All tests passed!")
