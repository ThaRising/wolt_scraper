import asyncio
from pprint import pprint


async def main():
    address = "Greifswalder Straße 146 Berlin Germany"

    from woltscrape.wolt.client import WoltMiner, Wolt
    woltminer = await WoltMiner()
    cookies = await woltminer.get_cookies(address)
    await woltminer.close()

    wolt = Wolt(cookies)
    return wolt.get_search(address)

if __name__ == '__main__':
    eventloop = asyncio.get_event_loop()
    data = eventloop.run_until_complete(main())
    pprint(data)
