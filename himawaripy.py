#!/usr/bin/env python3
from contextlib import contextmanager
from io import BytesIO
from json import loads
from os import makedirs
from os.path import expanduser, split
from subprocess import call
import logging
import sys
from time import strptime, strftime
from urllib.request import urlopen

from PIL import Image
from tqdm import tqdm

from utils import get_desktop_environment


json_url = "http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json"
image_url = "http://himawari8.nict.go.jp/img/D531106/{}d/{}/{}_{}_{}.png"

# Time formats
date_fmt_iso = "%Y-%m-%d %H:%M:%S"
date_fmt_url = "%Y/%m/%d/%H%M%S"

# Tile size
width = 550
height = 550

level = 4  # Increases the quality and the size. Possible values: 4, 8, 16, 20

output_file = expanduser("~/.config/himawari/himawari-latest.png")


def main():
    logging.info("Updating...")
    latest_timestamp = get_latest_timestamp(json_url)
    logging.info("Latest version: {} GMT\n"
                 .format(strftime(date_fmt_iso, latest_timestamp)))
    time_as_url = strftime(date_fmt_url, latest_timestamp)

    with create_png() as image:
        build_png(image, time_as_url)

    set_background()
    logging.info("Done!")


def get_latest_timestamp(json_url):
    with urlopen(json_url) as latest_json:
        return strptime(loads(latest_json.read().decode("utf-8"))["date"],
                        date_fmt_iso)


@contextmanager
def create_png():
    png = Image.new('RGB', (width*level, height*level))
    yield png
    logging.info("Saving image")
    makedirs(split(output_file)[0], exist_ok=True)
    png.save(output_file, "PNG")


def build_png(png, time_as_url):
    with tqdm(desc="Tiles downloaded", total=level**2, leave=True,
              unit=" tiles", unit_scale="true") as pbar:
        for x in range(level):
            for y in range(level):
                with urlopen(image_url.format(level, width,
                                              time_as_url,
                                              x, y)) as tile_w:
                    tiledata = tile_w.read()

                tile = Image.open(BytesIO(tiledata))
                png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))
                pbar.update()


def set_background():
    logging.info("Setting background")
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
        logging.error("Your desktop environment '{}' is not supported."
                      .format(de))
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)-8s: %(message)s")
    main()
