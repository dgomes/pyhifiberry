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
        _LOGGER.info("TRYING TO CONNECT")
        sio = AsyncClient()
        audiocontrol = Audiocontrol2SIO(sio)
        sio.register_namespace(audiocontrol.metadata)
        sio.register_namespace(audiocontrol.player)
        sio.register_namespace(audiocontrol.volume)

        @sio.event
        async def connect():
            _LOGGER.info("audiocontroller connected to host %s", host)
            audiocontrol.connected = True

        @sio.event
        async def disconnect():
            _LOGGER.info("audiocontroller disconnected from host %s", host)
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
        return await self.sio.call("playing", namespace="/player")

class Metadata(AsyncClientNamespace):

    def __init__(self, sio):
        super().__init__(namespace="/metadata")
        self.sio = sio
        self.callbacks = set()

    def add_callback(self, callback):
        self.callbacks.add(callback)

    async def on_update(self, data):
        _LOGGER.info("update")
        for callback in self.callbacks:
            callback(data)

    def set_metadata(self, metadata):
        self.metadata = metadata

    async def get_metadata(self):
        return await self.sio.call("get", namespace="/metadata")

class Volume(AsyncClientNamespace):

    def __init__(self, sio):
        super().__init__(namespace="/volume")
        self.sio = sio
        self.callbacks = set()

    def add_callback(self, callback):
        self.callbacks.add(callback)

    async def on_update(self, data):
        _LOGGER.info("update")
        for callback in self.callbacks:
            callback(data)

    async def get(self):
        return await self.sio.call("get", namespace="/volume")

    async def set(self, volume):
        return await self.sio.call("set", volume, namespace="/volume")
