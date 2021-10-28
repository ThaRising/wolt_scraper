import urllib.parse
from typing import List

import requests

from .type import Coordinates


def aobject(cls):
    __new__ = cls.__new__

    async def init(obj, *arg, **kwarg):
        await obj.__init__(*arg, **kwarg)
        return obj

    def new(cls, *arg, **kwarg):  # noqa
        obj = __new__(cls, *arg, **kwarg)
        coro = init(obj, *arg, **kwarg)
        return coro

    cls.__new__ = new
    return cls


@aobject
class WoltMiner:
    async def __init__(self):
        from pyppeteer import launch
        self.browser = await launch(headless=True)
        self.page = await self.browser.newPage()
        await self.page.goto('https://wolt.com')

    async def get_cookies(self, address: str):
        consent_button = await self.page.querySelector(
            'button[data-localization-key="gdpr-consents.banner.accept-button"]'
        )
        await consent_button.click()
        search_field = await self.page.querySelector('#front-page-input')
        await search_field.type(address)
        search_button = await self.page.querySelector(
            '[class^="AddressPickerInput-module"] > button'
        )
        await search_button.click()
        cookies = await self.page.cookies()
        return [{c.get("name"): c.get("value")} for c in cookies]

    async def close(self) -> None:
        await self.browser.close()


class Wolt:
    UA = [
        "Mozilla/5.0",
        "(X11; Linux x86_64)",
        "AppleWebKit/537.36",
        "(KHTML, like Gecko)",
        "Chrome/94.0.4606.71",
        "Safari/537.36"
    ]

    def __init__(self, cookies) -> None:
        self.cookies = cookies
        self.session = requests.Session()
        for cookie in cookies:
            self.session.cookies.update(cookie)
        self.session.headers.update({
            "user-agent": " ".join(self.UA),
            "sec-ch-ua": '";Not A Brand";v="99", "Chromium";v="94"',
            "platform": "Web",
            "origin": "https://wolt.com",
            "referer": "https://wolt.com",
            "w-wolt-session-id": list(
                [c for c in cookies if c.get("__woltAnalyticsId")][0].values()
            )[0]
        })

    def _get_coordinates(self, address: str) -> Coordinates:
        url = 'https://nominatim.openstreetmap.org/search/' + \
              urllib.parse.quote(address) + '?format=json'
        return Coordinates(self.session.get(url).json())

    def _get_search(self, address: str) -> requests.Response:
        coords = self._get_coordinates(address)
        return self.session.get(
            # f"https://restaurant-api.wolt.com/v1/pages/front?{coords!s}"
            f"https://restaurant-api.wolt.com/v1/pages/restaurants?{coords!s}"
        )

    def get_search(self, address: str) -> List[dict]:
        data = self._get_search(address).json().get("sections")[0]["items"]
        _restaurants = []
        for restaurant in data:
            r = {
                "title": restaurant.get("title"),
                "address": f"{restaurant.get('venue')['address']}, {restaurant.get('venue')['city']}",
                "url": restaurant.get("link")["target"]
            }
            _restaurants.append(r)
        return _restaurants
