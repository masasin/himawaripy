#!/usr/bin/env python3
from contextlib import contextmanager
from io import BytesIO
from json import loads
import os
from subprocess import call
import logging
import sys
from time import strptime, strftime
import sys

from PIL import Image
import requests
from tqdm import tqdm

from utils import get_desktop_environment


_home_dir = os.getenv("USER_HOME", "/tmp")
_log_dir = os.path.join(_home_dir, ".logs")
_log_file = os.path.join(_log_dir, "himawaripy.log")
os.makedirs(_log_dir, exist_ok=True)

json_url = "http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json"
image_url = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

# Time formats
logfile_fmt = "%(name)-12s : %(levelname)-8s  %(message)s"
console_fmt = "%(levelname)-8s : %(message)s"
date_fmt_iso = "%Y-%m-%d %H:%M:%S"
date_fmt_url = "%Y/%m/%d/%H%M%S"

# Tile size
width = 550
height = 550

level = 4  # Increases the quality and the size. Possible values: 4, 8, 16, 20

output_file = os.path.expanduser("~/.config/himawari/himawari-latest.png")

# Log everything to file
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s " + logfile_fmt,
                    datefmt=date_fmt_iso,
                    filename=_log_file,
                    filemode="a")

# Log important data to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(console_fmt))
logging.getLogger("").addHandler(console)

# Hide info logs from requests
for library in ("PIL", "requests", "urllib3"):
    logging.getLogger(library).setLevel(logging.WARNING)

logger = logging.getLogger("himawaripy")


def main():
    logger.info("Updating...")
    latest_timestamp = get_latest_timestamp(json_url)
    logger.info("Latest version: {} GMT"
                .format(strftime(date_fmt_iso, latest_timestamp)))
    time_as_url = strftime(date_fmt_url, latest_timestamp)

    with create_png() as image:
        build_png(image, time_as_url)

    set_background()
    logger.info("Done!")


def get_latest_timestamp(json_url):
    latest_json = requests.get(json_url)
    return strptime(loads(latest_json.content.decode())["date"], date_fmt_iso)


@contextmanager
def create_png():
    png = Image.new('RGB', (width*level, height*level))
    yield png
    logger.info("Saving image")
    os.makedirs(os.path.split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")


def build_png(png, time_as_url):
    with tqdm(desc="Tiles downloaded", total=level**2, leave=True,
              unit=" tiles", unit_scale="true") as pbar:
        for x in range(level):
            for y in range(level):
                tile_url = image_url.format(level, width, time_as_url, x, y)
                tiledata = requests.get(tile_url).content
                tile = Image.open(BytesIO(tiledata))
                png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))
                pbar.update()


def set_background():
    logger.info("Setting background")
    de = get_desktop_environment()
    if de in ("gnome", "unity", "cinnamon"):
        # Because of a bug and stupid design of gsettings
        # see http://askubuntu.com/a/418521/388226
        if de == "unity":
            call("gsettings set org.gnome.desktop.background "
                 "draw-background false".split())
        call("gsettings set org.gnome.desktop.background picture-uri "
             "file://{}".format(output_file).split())
        call("gsettings set org.gnome.desktop.background "
             "picture-options scaled".split())
    elif de == "mate":
        call('gconftool-2 -type string -set '
             '/desktop/gnome/background/picture_filename "{}"'
             .format(output_file).split())
    elif de == "xfce4":
        call("xfconf-query --channel xfce4-desktop --property "
                "/backdrop/screen0/monitor0/image-path --set {}"
             .format(output_file).split())
    elif de == "lxde":
        call("display -window root {}".format(output_file).split())
    elif de == "mac":
        call('osascript -e \'tell application "Finder" to set '
             'desktop picture to POSIX file "{}"\''
             .format(output_file).split())
    else:
        logger.error("Your desktop environment '{}' is not supported."
                     .format(de))
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        logger.critical("Connection error! Are you online?")
        sys.exit(1)
