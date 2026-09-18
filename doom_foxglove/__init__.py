"""Foxglove DOOM hero loop: ViZDoom as a fake robot on a Foxglove SDK WebSocket."""

__version__ = "0.1.0"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
CAMERA_TOPIC = "/doom/camera"
CMD_VEL_TOPIC = "/cmd_vel"
BUTTONS_TOPIC = "/doom/buttons"
MAP_TOPIC = "/doom/map"
TF_TOPIC = "/tf"
ENTITIES_TOPIC = "/doom/entities"
PLAYER_TOPIC = "/doom/player"
LOG_TOPIC = "/doom/log"
EVENTS_TOPIC = "/doom/events"
MAP_FRAME = "map"
BASE_FRAME = "base_link"
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
TICK_HZ = 35
DOOM_UNITS_PER_METER = 32.0
