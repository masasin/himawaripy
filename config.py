import logging
import os


_HOME_DIR = os.getenv("USER_HOME", "/tmp")
_LOG_DIR = os.path.join(_HOME_DIR, ".logs")
_LOG_FILE = os.path.join(_LOG_DIR, "himawaripy.log")
os.makedirs(_LOG_DIR, exist_ok=True)

JSON_URL = "http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json"
IMAGE_URL = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"
TIMEOUT = 1  # second

# Time formats
LOGFILE_FMT = "%(name)-12s : %(levelname)-8s  %(message)s"
CONSOLE_FMT = "%(levelname)-8s : %(message)s"
DATE_FMT_ISO = "%Y-%m-%d %H:%M:%S"
DATE_FMT_URL = "%Y/%m/%d/%H%M%S"

# Tile size
WIDTH = 550
HEIGHT = 550

LEVEL = 4  # Increases the quality and the size. Possible values: 4, 8, 16, 20

OUTPUT_FILE = os.path.expanduser("~/.config/himawari/himawari-latest.png")

# Log everything to file
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s " + LOGFILE_FMT,
                    datefmt=DATE_FMT_ISO,
                    filename=_LOG_FILE,
                    filemode="a")

# Log important data to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(CONSOLE_FMT))
logging.getLogger("").addHandler(console)

# Hide info logs from PIL requests
for library in ("PIL", "requests", "urllib3"):
    logging.getLogger(library).setLevel(logging.WARNING)

logger = logging.getLogger("himawaripy")


# Xfce4 displays to change the background of
xfce_displays = ["/backdrop/screen0/monitor0/image-path",
                 "/backdrop/screen0/monitor0/workspace0/last-image"]
