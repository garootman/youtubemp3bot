import os
import random
import re

from envs import LOCAL_PROXY_URL, USE_PROXY

PROXIES = []
if USE_PROXY == "LOCALHOST":
    PROXIES = [LOCAL_PROXY_URL]
elif USE_PROXY:
    # if .proxylist.txt exists, read it and use the proxies from there
    if os.path.exists(".proxylist.env"):
        with open(".proxylist.env", "r") as f:
            PROXIES = f.read().splitlines()
            PROXIES = [p.strip() for p in PROXIES if p]


class ProxyRevolver:
    # rotates proxies from list withouth deleting them
    # once gets to the end of the list, starts from the beginning
    # if no proxies, returns None
    # starts current with random value within the list

    def __init__(self, proxies):
        http_syntax_proxies = []
        for proxy in proxies:
            http_proxy = self._proxy_url_to_http_syntax(proxy)
            if http_proxy:
                print(f"Added proxy {http_proxy}")
                http_syntax_proxies.append(http_proxy)
            else:
                print(f"Invalid proxy format: {proxy}")

        self.proxies = http_syntax_proxies
        print(f"Starting ProxyRevolver with {len(self.proxies)} proxies")
        if not self.proxies:
            return
        self.current = random.randint(0, len(self.proxies) - 1)

    def _proxy_url_to_http_syntax(self, proxy):
        # checks proxy string formatting
        # returns proxy in valid http format

        if re.match(r"http://.*:.*@.*:\d+", proxy):
            return proxy
        elif re.match(r".*:\d+:\w+:\w+", proxy):
            parts = proxy.split(":")
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif re.match(r".*:\d+", proxy):
            parts = proxy.split(":")
            return f"http://{parts[0]}:{parts[1]}"

        return None

    def get_proxy(self):
        if not self.proxies:
            return None

        proxy = self.proxies[self.current]
        self.current += 1
        if self.current >= len(self.proxies):
            self.current = 0
        return proxy

    def reject_proxy(self, proxy):
        # proxy turned out to be bad, remove it from the list
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            print(f"Removed proxy {proxy}, {len(self.proxies)} left")
        else:
            print(f"Proxy {proxy} not found in the list")


proxy_mgr = ProxyRevolver(PROXIES)
