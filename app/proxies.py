import random

from envs import LOCAL_PROXY_URL, USE_PROXY

if USE_PROXY == "LOCALHOST":
    PROXIES = [LOCAL_PROXY_URL]
elif USE_PROXY:
    with open(".proxylist.txt", "r") as f:
        PROXIES = f.read().splitlines()
        PROXIES = [p.strip() for p in PROXIES if p]
else:
    PROXIES = []


class ProxyRevolver:
    # rotates proxies from list withouth deleting them
    # once gets to the end of the list, starts from the beginning
    # if no proxies, returns None
    # starts current with random value within the list

    def __init__(self, proxies):
        self.proxies = proxies
        print(f"Starting ProxyRevolver with {len(self.proxies)} proxies")
        if not self.proxies:
            return
        self.current = random.randint(0, len(self.proxies) - 1)

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
