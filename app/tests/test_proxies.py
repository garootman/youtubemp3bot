import random

import pytest
from proxies import ProxyRevolver

proxy_mgr = ProxyRevolver()


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
    p = proxy_mgr.get_proxy_by_countries(c, None)
    assert p


if __name__ == "__main__":
    test_proxy_revolver()
    test_get_tested_proxy()
    test_get_proxy_by_countries()
    print("All tests passed")
