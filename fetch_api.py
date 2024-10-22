import aiohttp
import asyncio 

# def hello(): print("hello world")

async def fetchAPI(url): 
    try: 
        async with aiohttp.ClientSession() as session: 
            async with session.get(url) as response:
                try: 
                    data = await response.json()
                    return data
                except aiohttp.ContentTypeError:
                    print("JSON is invalid")
                    return None
    except aiohttp.ClientConnectionError:
        print("Error occur when connecting with server")
    except Exception as e:
        print(f"Something went wrong!!")
        return None


async def postAPI(url, data): 
    try:
        async with aiohttp.ClientSession() as session: 
            async with session.post(url, json=data) as response: 
                try: 
                    data = await response.json()
                    return data
                except aiohttp.ContentTypeError:
                    print("JSON is invalid")
                    return None 
    except aiohttp.ClientConnectionError:
        print("Error occur when connecting with server")
    except Exception as e:
        print(f"Something went wrong!!")
        return None
            