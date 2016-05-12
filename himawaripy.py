#!/usr/bin/env python3
from contextlib import contextmanager
from io import BytesIO
from json import loads
import os
import sys
from time import strptime, strftime

from PIL import Image
import requests
from tqdm import tqdm

from config import (HEIGHT, WIDTH, LEVEL, OUTPUT_FILE, TIMEOUT, JSON_URL,
                    IMAGE_URL, DATE_FMT_ISO, DATE_FMT_URL, logger)


def main():
    logger.info("Updating...")
    latest_timestamp = get_latest_timestamp(JSON_URL)
    logger.info("Latest version: {} GMT"
                .format(strftime(DATE_FMT_ISO, latest_timestamp)))
    time_as_url = strftime(DATE_FMT_URL, latest_timestamp)

    with create_png() as image:
        build_png(image, time_as_url)

    set_background()
    logger.info("Done!")


def get_latest_timestamp(JSON_URL):
    latest_json = requests.get(JSON_URL, timeout=TIMEOUT)
    return strptime(loads(latest_json.content.decode())["date"], DATE_FMT_ISO)


@contextmanager
def create_png():
    png = Image.new('RGB', (WIDTH*LEVEL, HEIGHT*LEVEL))
    yield png
    logger.info("Saving image")
    os.makedirs(os.path.split(OUTPUT_FILE)[0], exist_ok=True)
    png.save(OUTPUT_FILE, "PNG")


def build_png(png, time_as_url):
    with tqdm(desc="Tiles downloaded", total=LEVEL**2, leave=True,
              unit="tile", unit_scale="true") as pbar:
        for x in range(LEVEL):
            for y in range(LEVEL):
                tile_url = IMAGE_URL.format(LEVEL, WIDTH, time_as_url, x, y)
                tiledata = requests.get(tile_url, timeout=TIMEOUT).content
                tile = Image.open(BytesIO(tiledata))
                png.paste(tile, (WIDTH*x, HEIGHT*y, WIDTH*(x+1), HEIGHT*(y+1)))
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
             "file://{}".format(OUTPUT_FILE).split())
        call("gsettings set org.gnome.desktop.background "
             "picture-options scaled".split())
    elif de == "mate":
        call('gconftool-2 -type string -set '
             '/desktop/gnome/background/picture_filename "{}"'
             .format(OUTPUT_FILE).split())
    elif de == "xfce4":
        call("xfconf-query --channel xfce4-desktop --property "
                "/backdrop/screen0/monitor0/image-path --set {}"
             .format(OUTPUT_FILE).split())
    elif de == "lxde":
        call("display -window root {}".format(OUTPUT_FILE).split())
    elif de == "mac":
        call('osascript -e \'tell application "Finder" to set '
             'desktop picture to POSIX file "{}"\''
             .format(OUTPUT_FILE).split())
    else:
        logger.error("Your desktop environment '{}' is not supported"
                     .format(de))
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.error("Interrupted by user")
    except requests.exceptions.ConnectionError:
        logger.exception("Connection error! Are you online?")
        sys.exit(1)
    except requests.exceptions.Timeout:
        logger.exception("Timeout error!")
        sys.exit(1)
