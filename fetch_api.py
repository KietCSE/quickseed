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
                    # print("JSON is invalid")
                    print(f"\033[1;31m{'FETCH: JSON is invalid'}\033[0m")
                    return None
    except aiohttp.ClientConnectionError:
        # print("Error occur when connecting with server")
        print(f"\033[1;31m{'ERROR OCCUR WHEN CONNECTING WITH SERVER'}\033[0m")
    except Exception as e:
        # print(f"Something went wrong!!")
        print(f'\033[1;31m{'SOMETHING WENT WRONG!!'}\033[0m')
        return None


async def postAPI(url, data): 
    try:
        async with aiohttp.ClientSession() as session: 
            async with session.post(url, json=data) as response: 
                try: 
                    data = await response.json()
                    return data
                except aiohttp.ContentTypeError:
                    # print("JSON is invalid")
                    print(f"\033[1;31m{'FETCH: JSON is invalid'}\033[0m")
                    return None
    except aiohttp.ClientConnectionError:
        # print("Error occur when connecting with server")
        print(f"\033[1;31m{'ERROR OCCUR WHEN CONNECTING WITH SERVER'}\033[0m")
    except Exception as e:
        # print(f"Something went wrong!!")
        print(f'\033[1;31m{'SOMETHING WENT WRONG!!'}\033[0m')
        return None
     #             try: 
    #                 data = await response.json()
    #                 return data
    #             except aiohttp.ContentTypeError:
    #                 print("JSON is invalid")
    #                 return None 
    # except aiohttp.ClientConnectionError:
    #     print("Error occur when connecting with server")
    # except Exception as e:
    #     print(f"Something went wrong!!")
    #     return None       