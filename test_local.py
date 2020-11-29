import aiohttp
import asyncio
from pyhifiberry import audiocontrol2

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            api = audiocontrol2.Audiocontrol2(session)

            print("Start playing")
            await api.player("play")

            status = await api.player("status")
            assert any([player['state'] == 'playing' for player in status['players']])

            await api.player("pause")
            await asyncio.sleep(2)
            await api.player("play")

            current_volume = await api.volume()
            print(await api.volume("-5"))
            assert current_volume-5 == await api.volume()
            await asyncio.sleep(2)
            print(await api.volume("+5"))
            assert current_volume == await api.volume()
    except audiocontrol2.Audiocontrol2Exception as err:
        print(err) 
        if err.original:
            print("Original Exception: ", err.original)       

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
