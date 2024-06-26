import logging
import os
import random
import re
from abc import ABC, abstractmethod

import requests

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROXY_API_URL = (
    "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
)

from tgmediabot.envs import PROXY_TOKEN

"""        {
            "id": "d-15894556632",
            "username": "2dh5uiDTSX",
            "password": "vxQCr3xYC9Pbg46",
            "proxy_address": "89.116.78.80",
            "port": 5691,
            "valid": true,
            "last_verification": "2024-06-10T09:01:55.269783-07:00",
            "country_code": "GB",
            "city_name": "London",
            "asn_name": "Uab \"Bite Lietuva\"",
            "asn_number": 210906,
            "high_country_confidence": false,
            "created_at": "2024-06-07T12:04:25.112970-07:00"
        },
"""


class ProxyRevolver:

    def __init__(self, proxy_token=PROXY_TOKEN):
        self.__current = 0
        self.__proxies = []
        self.__token = proxy_token
        self._load_proxies()

        if not self.__proxies:
            logger.error("No proxies loaded")
            return
        countries = set([i.get("country_code", "") for i in self.__proxies])
        self.countries = [i.upper() for i in countries if i]
        logger.info(
            f"Starting ProxyRevolver with {len(self.__proxies)} proxies, countries: {self.countries}"
        )
        self.__current = random.randint(0, len(self.__proxies) - 1)

    def _load_proxies(self):
        try:
            logger.info("Loading proxies")
            response = requests.get(
                PROXY_API_URL,
                headers={"Authorization": self.__token},
            )
            data = response.json()
            if not data:
                logger.error("No data from proxy API")
                return
            self.__proxies = data.get("results", [])
            logger.info(f"Loaded {len(self.__proxies)} proxies")
            logger.debug(f"Proxies: {self.__proxies}")
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")

    def _proxy_to_http_syntax(self, proxy):
        if not proxy:
            return None
        return f"http://{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}"

    def check_proxy(self, proxy, timeout=5):
        try:
            logger.debug(f"Checking proxy {proxy}")
            response = requests.get(
                "http://api.ipify.org", proxies={"http": proxy}, timeout=timeout
            )
            if response.status_code == 200:
                logger.debug(f"Proxy {proxy} is working")
                return True
            else:
                logger.error(f"Proxy {proxy} is not working")
                logger.debug(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"Proxy {proxy} is not working: {e}")
        return False

    def get_any_proxy(self):
        if not self.__proxies:
            return None
        proxy = self.__proxies[self.__current]
        self.__current += 1
        if self.__current >= len(self.__proxies):
            self.__current = 0
        return proxy

    def get_proxy(self):
        p = self.get_any_proxy()
        return self._proxy_to_http_syntax(p)

    def _lookup_proxy_by_yes_countries(self, countries_yes):
        if not countries_yes:
            return None
        country_list = countries_yes
        country_list = [c.strip().upper() for c in country_list]
        for proxy in self.__proxies:
            valid_country_proxies = [
                i for i in self.__proxies if i["country_code"].upper() in country_list
            ]
            if valid_country_proxies:
                return random.choice(valid_country_proxies)
        return None

    def _lookup_proxy_by_no_countries(self, countries_no):
        if not countries_no:
            return None
        country_list = countries_no
        country_list = [c.strip().upper() for c in country_list]
        for proxy in self.__proxies:
            valid_country_proxies = [
                i
                for i in self.__proxies
                if i["country_code"].upper() not in country_list
            ]
            if valid_country_proxies:
                return random.choice(valid_country_proxies)
        return None

    def get_proxy_by_countries(self, countries_yes, countries_no):
        if not self.__proxies:
            return None
        elif not countries_yes and not countries_no:
            return self.get_any_proxy()
        elif countries_yes:
            proxy = self._lookup_proxy_by_yes_countries(countries_yes)
            if proxy:
                return proxy
        elif countries_no:
            proxy = self._lookup_proxy_by_no_countries(countries_yes)
            if proxy:
                return proxy

        return None

    def get_checked_proxy_by_countries(self, countries_yes, countries_no, attempts=3):
        logger.info(f"Getting proxy by countries: {countries_yes} not {countries_no}")
        if not self.__proxies:
            return None
        for _ in range(attempts):
            proxy = self.get_proxy_by_countries(countries_yes, countries_no)
            http_proxy = self._proxy_to_http_syntax(proxy)
            if self.check_proxy(http_proxy):
                logger.info(f"Got a working proxy: {http_proxy}")
                return http_proxy
            logger.debug(f"Proxy {http_proxy} failed")
        logger.error(f"Failed to get a proxy after {attempts} attempts")
        return None
