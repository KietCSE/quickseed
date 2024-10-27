import state as var
from fetch_api import * 
from config import HOST

async def scrape(code): 
    response = await fetchAPI(f"{HOST}/scrape/{code}")
    if (response.get("status")): 
        print(f"File name: {response.get("data").get("fileName")}")
        print(f"Seeder: {response.get("data").get("seeder")}")
        print(f"Leecher: {response.get("data").get("leecher")}")
        print(f"Success Download: {response.get("data").get("downloaded")}")
    else: 
        print(f"{response.get("message")}")

async def main():
    await scrape("e3f4b4aed9c346c76bab6afa60fd6d5198164797")

if __name__ == '__main__':
    asyncio.run(main()) 