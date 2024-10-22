import aiohttp
import asyncio 

def hello(): print("hello world")

async def fetchAPI(url): 
    async with aiohttp.ClientSession() as session: 
        async with session.get(url) as response:
            if response.status == 200: 
                try: 
                    data = await response.json()
                    return data
                except aiohttp.ContentTypeError:
                    print("JSON is invalid")
            else:
                print("Error HTTP: {response.status}")
                return None



async def postAPI(url, data): 
    async with aiohttp.ClientSession() as session: 
        async with session.post(url, json=data) as response: 
            if response.status == 200: 
                try: 
                    data = await response.json()
                    return data
                except aiohttp.ContentTypeError:
                    print("JSON is invalid")
            else:
                print("Error HTTP: {response.status}")
                return None