"""Socketio based API to Hifiberry OS - audiocontrol2"""
import logging

from socketio import AsyncClient, AsyncClientNamespace

from .consts import DEFAULT_HOST, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

class Audiocontrol2SIO:

    def __init__(self, sio) -> None:
        self.connected = False
        self.metadata = Metadata(sio)
        self.player = Player(sio)
        self.volume = Volume(sio)
        self._sio = sio

    @classmethod
    async def connect(cls, host=DEFAULT_HOST, port=DEFAULT_PORT, wait_timeout=10):
        _LOGGER.debug("TRYING TO CONNECT")
        sio = AsyncClient()
        audiocontrol = Audiocontrol2SIO(sio)
        sio.register_namespace(audiocontrol.metadata)
        sio.register_namespace(audiocontrol.player)
        sio.register_namespace(audiocontrol.volume)

        @sio.event
        async def connect():
            _LOGGER.debug("audiocontroller connected to host %s", host)
            audiocontrol.connected = True

        @sio.event
        async def disconnect():
            _LOGGER.debug("audiocontroller disconnected from host %s", host)
            audiocontrol.connected = False

        await sio.connect(f'http://{host}:{port}', wait_timeout=wait_timeout)
        return audiocontrol

    async def disconnect(self):
        await self._sio.disconnect()

class Player(AsyncClientNamespace):

    def __init__(self, sio):
        super().__init__(namespace="/player")
        self.sio = sio

    async def play(self):
        await self.sio.emit("play", namespace="/player")

    async def pause(self):
        await self.sio.emit("pause", namespace="/player")

    async def playpause(self):
        await self.sio.emit("playpause", namespace="/player")

    async def stop(self):
        await self.sio.emit("stop", namespace="/player")

    async def next(self):
        await self.sio.emit("next", namespace="/player")

    async def previous(self):
        await self.sio.emit("previous", namespace="/player")

    async def get_status(self):
        return await self.sio.call("status", namespace="/player")

    async def playing(self):
        """The audiocontrol2 api has an undocumented endpoint /api/player/playing returning 
        whether or not any player is active.
        """
        return await self.sio.call("playing", namespace="/player")

class Metadata(AsyncClientNamespace):

    def __init__(self, sio):
        super().__init__(namespace="/metadata")
        self.sio = sio
        self.callbacks = set()
        self.title = None
        self.artist = None
        self.albumTitle = None
        self.albumArtist = None
        self.tracknumber = None
        self.artUrl = None
        self.externalArtUrl = None
        self.playerName = None
        self.playerState = None
        self.positionupdate = None

    def add_callback(self, callback):
        self.callbacks.add(callback)

    async def on_update(self, meta):
        self._set_metadata(meta)
        _LOGGER.debug("updated metadata: %s", meta)
        for callback in self.callbacks:
            callback(meta)

    async def get_metadata(self):
        meta = await self.sio.call("get", namespace="/metadata")
        self._set_metadata(meta)
        return meta

    def _set_metadata(self, meta):
        for field, value in meta.items():
            setattr(self, field, value)


class Volume(AsyncClientNamespace):

    def __init__(self, sio):
        super().__init__(namespace="/volume")
        self.sio = sio
        self.callbacks = set()
        self.percent = None

    def add_callback(self, callback):
        self.callbacks.add(callback)

    async def on_connect(self):
        _LOGGER.debug('on connect volume')
        await self.get()

    async def on_update(self, volume):
        _LOGGER.debug("update volume %s", volume)
        self.percent = volume['percent']
        for callback in self.callbacks:
            callback(volume)

    async def get(self):
        _LOGGER.debug("getting volume")
        volume = await self.sio.call("get", namespace="/volume")
        self.percent = volume['percent']
        return volume

    async def set(self, volume: int):
        _LOGGER.debug("setting volume: %s", volume)
        response =  await self.sio.call("set", {'percent': volume}, namespace="/volume")
        self.percent = response['percent']
        return response
