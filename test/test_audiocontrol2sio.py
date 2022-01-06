import json
import asyncio
from typing import Any

import pytest
from pyhifiberry.audiocontrol2sio import Audiocontrol2SIO


@pytest.fixture
async def audiocontrol() -> Audiocontrol2SIO:
    api = await Audiocontrol2SIO.connect('localhost', 8080)
    while not api.connected:
        await asyncio.sleep(0.1)
    yield api
    await api.disconnect()

@pytest.mark.asyncio
async def test_disconnect(audiocontrol: Audiocontrol2SIO):
    await audiocontrol.disconnect()
    assert not audiocontrol.connected

@pytest.mark.asyncio
async def test_get_metadata(audiocontrol: Audiocontrol2SIO):
    response = await audiocontrol.metadata.get_metadata()
    assert response.get('title') is not None

@pytest.mark.asyncio
async def test_metadata_callback(audiocontrol: Audiocontrol2SIO):
    cb = MetadataCallback()
    audiocontrol.metadata.add_callback(cb)
    await audiocontrol.player.next()
    await asyncio.sleep(1)

    assert cb.metadata.get('title') == audiocontrol.metadata.title

@pytest.mark.asyncio
async def test_player_status(audiocontrol: Audiocontrol2SIO):
    status = await audiocontrol.player.get_status()
    assert 'players' in status.keys()

@pytest.mark.asyncio
async def test_player_pause_play(audiocontrol: Audiocontrol2SIO):
    await audiocontrol.player.pause()
    await asyncio.sleep(1) 
    assert not await audiocontrol.player.playing()
    await audiocontrol.player.play()
    await asyncio.sleep(1)
    assert await audiocontrol.player.playing()

@pytest.mark.asyncio
async def test_volume(audiocontrol: Audiocontrol2SIO):
    cb = VolumeCallback()
    audiocontrol.volume.add_callback(cb)
    while audiocontrol.volume.percent is None:          ### percent is set on connect so we migth have to wait here
        await asyncio.sleep(0.1)
    new_volume = audiocontrol.volume.percent + 1 if audiocontrol.volume.percent < 99 else 0
    foo = await audiocontrol.volume.set(new_volume)
    await asyncio.sleep(1)
    
    assert cb.volume['percent'] == new_volume

@pytest.mark.asyncio
async def test_set_volume(audiocontrol: Audiocontrol2SIO):
    await audiocontrol.volume.set(10)
    
    assert audiocontrol.volume.percent == 10

@pytest.mark.asyncio
async def test_set_volume_error(audiocontrol: Audiocontrol2SIO):
    with pytest.raises(Exception):
        response = await audiocontrol.volume.set('Hello')
    

class VolumeCallback:
    def __init__(self) -> None:
        self.volume = {'percent': 0}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.volume = args[0]


class MetadataCallback:
    def __init__(self) -> None:
        self.metadata = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.metadata = args[0]

