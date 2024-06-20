import random

import pytest

from proxies import ProxyRevolver

proxy_mgr = ProxyRevolver()

import re

http_proxy_pattern = re.compile(r"http(s)?://(\w+:\w+@)?\d+\.\d+\.\d+\.\d+:\d+")


def test_proxy_revolver():
    # test proxy revolver: it loads
    assert proxy_mgr
    assert proxy_mgr.get_proxy() is not None


def test_get_tested_proxy():
    # test proxy revolver: it loads
    p = proxy_mgr.get_proxy()
    check = proxy_mgr.check_proxy(p)
    assert check


def test_get_proxy_by_countries():
    # test proxy revolver: it loads
    countries = proxy_mgr.countries
    c = random.choice(countries)
    p = proxy_mgr.get_checked_proxy_by_countries([c], None)
    assert p
    assert http_proxy_pattern.match(p)


def test_proxy_format():
    # checks that proxy returned is in the correct http format
    # format is http(s)://login:passwd@ip:port
    # or without login:passwd
    p = proxy_mgr.get_proxy()
    assert http_proxy_pattern.match(p)


if __name__ == "__main__":
    test_proxy_revolver()
    test_get_tested_proxy()
    test_get_proxy_by_countries()
    test_proxy_format()
    print("All tests passed")
