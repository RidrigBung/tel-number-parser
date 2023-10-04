from typing import Set, List, Union
import asyncio
from aiohttp import ClientSession
import re


async def download_page(url: str) -> str:
    async with ClientSession() as session:
        async with session.get(url=url) as response:
            page = await response.text(encoding='utf-8')
            return page


async def parse_numbers(page: str) -> Set[str]:
    pattern = r'(?:(?:\+7|8)(?:\s\({,1}\d{3}\){,1}\s\d{3})(?:\s{,1}\-{,1}\d{2}){2}|\d{3}(?:\-\d{2}){2})'
    raw_numbers = set(re.findall(pattern, page))
    numbers: Set[str] = set()
    for number in raw_numbers:
        tel: str = ""
        # Если номер телефона без кода города (формат NNN-NN-NN)
        if len(number) == 9:
            tel = "8495"
            start = 0
        # Если обычный номер телефона
        else:
            tel = "8"
            if number[0] == "+":
                start = 2
            else:
                start = 1
        for c in range(start, len(number)):
            if number[c].isdigit():
                tel += number[c]
        numbers.add(tel)
    return numbers


async def get_phone_numbers(urls: List[str]) -> List[Union[str, Set[str]]]:
    pages: List[str] = []
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(download_page(url)))
    pages = await asyncio.gather(*tasks)

    phone_numbers: List[Union[str, Set[str]]] = []
    tasks = []
    for page in pages:
        tasks.append(asyncio.create_task(parse_numbers(page)))
    phone_numbers = await asyncio.gather(*tasks)

    return phone_numbers


if __name__ == "__main__":
    urls = ["https://hands.ru/company/about", "https://repetitors.info"]
    phone_numbers = asyncio.run(get_phone_numbers(urls))
    print(list(zip(urls, phone_numbers)))
