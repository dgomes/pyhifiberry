from enum import Enum

DEFAULT_HOST = "hifiberry.local"
DEFAULT_PORT = 81

API_PLAYER = "{}/api/player/{}"
API_PLAYER_ACTIVE = "{}/api/player/active/{}"
API_PLAYER_POST_COMMANDS = ["play", "pause", "playpause", "stop", "next", "previous"]
API_PLAYER_GET_COMMANDS = ["status"]

API_TRACK = "{}/api/track/{}"
API_TRACK_POST = ["love", "unlove"]
API_TRACK_GET = ["metadata"]

API_VOLUME = "{}/api/volume"