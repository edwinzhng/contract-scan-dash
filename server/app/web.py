import asyncio
import requests

async def get_async(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, requests.get, url)


async def post_async(url, data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, requests.post, url, data)
