import aiohttp
import asyncio
from pyhifiberry import audiocontrol2

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            api = audiocontrol2.Audiocontrol2(session, host="hifiberry", authtoken="hifiberry")

            status =  await api.status()
            print(status)
           
            print(await api.info())
            await api.poweroff()
            return
 
    except audiocontrol2.Audiocontrol2Exception as err:
        print(err) 
        if err.original:
            print("Original Exception: ", err.original)       

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
