TARGET_PATH = ".data/images"
BIN_FOLDER_NAME = "bin"
RES_FOLDER_NAME = "out"
SNAPSHOTS_FOLDER_NAME = "snapshots"
VIDEO_FOLDER_NAME = "video"
LOG_LIMIT = 50
REFERENCE_FILENAME = "base.pkl"
FRAME_RATE = 24
DEFAULT_SNAPSHOT_COUNTER = 500
LARGE_SEGMENT_PIXEL_COUNT = 5000
MAX_IMAGE_SIZE = 1000
SNAPSHOT_TIMES = (
    # no. of pixels in a segment, time to take a snapshot every n updates
    (50, 10),
    (100, 15),
    (200, 20),
    (300, 25),
    (500, 30),
    (1000, 35),
    (2000, 40),
    (5000, 50),
    (12000, 100),
    (25000, 200),
)


class Render:
    ACTIVE = "active"
    OFFLINE = "offline"


class Color:
    BLACK = 0
    WHITE = 255


class Resolution:
    YOUTUBE_HD = (1080, 1920)
