import os
import random
import re

import requests


class ProxyRevolver:

    def __init__(self, proxy_list):
        self.__current = 0
        self.__proxies = []
        for p in proxy_list:
            self.add_proxy(p)
        print(f"Starting ProxyRevolver with {len(self.__proxies)} proxies")
        if not self.__proxies:
            return
        self.__current = random.randint(0, len(self.__proxies) - 1)

    def add_proxy(self, proxy):
        proxy = self._proxy_url_to_http_syntax(proxy)
        if proxy:
            self.__proxies.append(proxy)
            return
        print(f"Invalid proxy format: {proxy}")

    def _proxy_url_to_http_syntax(self, proxy):
        proxy = str(proxy).strip()
        if re.match(r"http://.*:.*@.*:\d+", proxy):
            return proxy
        elif re.match(r".*:\d+:\w+:\w+", proxy):
            parts = proxy.split(":")
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif re.match(r".*:\d+", proxy):
            parts = proxy.split(":")
            return f"http://{parts[0]}:{parts[1]}"
        print(f"Invalid proxy format: {proxy}")
        return None

    def check_proxy(self, proxy, timeout=5):
        try:
            response = requests.get(
                "http://api.ipify.org", proxies={"http": proxy}, timeout=timeout
            )
            if response.status_code == 200:
                return True
            else:
                print(f"Proxy {proxy} is not working")
        except Exception as e:
            print(f"Proxy {proxy} is not working: {e}")
        return False

    def get_proxy(self):
        if not self.__proxies:
            return None
        proxy = self.__proxies[self.__current]
        self.__current += 1
        if self.__current >= len(self.__proxies):
            self.__current = 0
        return proxy

    def get_checked_proxy(self, attempts=3):
        if not self.__proxies:
            return None
        for _ in range(attempts):
            proxy = self.get_proxy()
            if self.check_proxy(proxy):
                return proxy

    def reject_proxy(self, proxy):
        # proxy turned out to be bad, remove it from the list
        if proxy in self.__proxies:
            self.__proxies.remove(proxy)
            print(f"Removed proxy {proxy}, {len(self.__proxies)} left")
        else:
            print(f"Proxy {proxy} not found in the list")
