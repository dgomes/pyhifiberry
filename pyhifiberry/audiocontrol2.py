"""API to Hifiberry OS - audiocontrol2"""
import json
import asyncio
import logging
import aiohttp

from .consts import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    API_PLAYER,
    API_PLAYER_GET_COMMANDS,
    API_PLAYER_POST_COMMANDS,
    API_PLAYER_ACTIVE,
    API_TRACK,
    API_TRACK_GET,
    API_TRACK_POST,
    API_VOLUME,
    API_SYSTEM,
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Audiocontrol2Exception(Exception):
    """Exception class for Audiocontrol2."""

    def __init__(self, message="Operation not completed", original=None):
        LOGGER.error("Audiocontrol2Exception %s caused by: %s", message, original)
        self.original = original
        self.message = message
        super().__init__(message)

class Audiocontrol2:
    """Implements the interfaces in https://github.com/hifiberry/audiocontrol2/blob/master/doc/api.md."""

    def __init__(self, websession, host=DEFAULT_HOST, port=81, authtoken=None):
        self.websession = websession
        self.base_url = f"http://{host}:{port}"
        self.authtoken = authtoken

    async def _request(self, method, api_template, endpoint="", json_dict={}):
        """Issue API requests."""

        headers = {}
        if self.authtoken:
            headers = {"Authtoken": self.authtoken}

        url = api_template.format(self.base_url, endpoint)
        LOGGER.debug("request %s %s with %s", method, url, json_dict)

        try:
            async with self.websession.request(
                method, url, headers=headers, json=json_dict, timeout=2
            ) as res:
                if res.status != 200:
                    raise Audiocontrol2Exception(f"Couldn't request {url}, status: {res.status}")
                if res.content_type == "application/json":
                    return await res.json()
                return await res.text()
        except asyncio.TimeoutError as err:
            raise Audiocontrol2Exception("Timeout connecting to Hifiberry host.", err)
        except aiohttp.ClientError as err:
            raise Audiocontrol2Exception("Could not connect to Hifiberry host.", err)
        except json.decoder.JSONDecodeError as err:
            raise Audiocontrol2Exception("Error processing Hifiberry response.", err)

    async def player(self, command):
        if command in API_PLAYER_POST_COMMANDS:
            r = await self._request("POST", API_PLAYER, command)
            return r is not None

        elif command in API_PLAYER_GET_COMMANDS:
            r = await self._request("GET", API_PLAYER, command)
            return r

        else:
            raise Audiocontrol2Exception("Unknown player command")

    async def info(self):
        r = await self._request("GET", API_SYSTEM, "info")
        return r

    async def status(self):
        r = await self._request("GET", API_PLAYER, "status")
        return r

    async def player_activate(self, playername):
        r = await self._request("POST", API_PLAYER_ACTIVE, playername)
        return r is not None

    async def metadata(self):
        r = await self._request("GET", API_TRACK, "metadata")
        return json.loads(r)

    async def lastfm(self, action):
        if action in ["love", "unlove"]:
            r = await self._request("POST", API_TRACK, action)
            return r is not None

        raise Audiocontrol2Exception("Last.fm supported actions: love/unlove")

    async def volume(self, vol=None):
        if vol is None:
            r = await self._request("GET", API_VOLUME)
            return r["percent"]

        r = await self._request("POST", API_VOLUME, json={"percent": str(vol)})
        return r

    async def poweroff(self):
        await self._request("POST", API_SYSTEM, "poweroff")
