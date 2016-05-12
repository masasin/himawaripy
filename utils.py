# http://stackoverflow.com/a/21213358/4466589
import os
import sys
from subprocess import call, check_output, CalledProcessError
import re

from config import OUTPUT_FILE, logger, xfce_displays


def set_background():
    logger.info("Setting background")
    de = get_desktop_environment()
    if de in ("gnome", "unity", "cinnamon", "pantheon", "gnome-classic"):
        # Because of a bug and stupid design of gsettings
        # see http://askubuntu.com/a/418521/388226
        if de == "unity":
            call("gsettings set org.gnome.desktop.background "
                 "draw-background false".split())
        call("gsettings set org.gnome.desktop.background picture-uri "
             "file://{}".format(OUTPUT_FILE).split())
        call("gsettings set org.gnome.desktop.background "
             "picture-options scaled".split())
        call("gsettings set org.gnome.desktop.background "
             "primary-color FFFFFF".split())
    elif de == "mate":
        call("gsettings set org.mate.background picture-filename {}"
             .format(OUTPUT_FILE).split())
    elif de == "i3":
        call("feh --bg-fill {}".format(OUTPUT_FILE).split())
    elif de == "xfce4":
        for display in xfce_displays:
            call("xfconf-query --channel xfce4-desktop --property "
                 "{} --set {}".format(display, OUTPUT_FILE).split())
    elif de == "lxde":
        call("pcmanfm --set-wallpaper {} --wallpaper-mode=fit"
             .format(OUTPUT_FILE).split())
    elif de == "mac":
        call('osascript -e tell application "System Events"\n'
             'set theDesktops to a reference to every desktop\n'
             'repeat with aDesktop in theDesktops\n'
             'set the picture of aDesktop to "{}"\nend repeat\nend tell'
             .format(OUTPUT_FILE).split())
        call("killall Dock".split())
    elif has_program("feh"):
        logger.info("Unknown desktop environment '{}'".format(de)
                    + ", but 'feh' is installed and will be used.")
        os.environ["DISPLAY"] = ":0"
        call("feh --bg-max {}".format(OUTPUT_FILE).split())
    elif has_program("nitrogen"):
        logger.info("Unknown desktop environment '{}'".format(de)
                    + ", but 'nitrogen' is installed and will be used.")
        os.environ["DISPLAY"] = ":0"
        call("nitrogen --restore".split())
    else:
        logger.error("Your desktop environment '{}' is not supported"
                     .format(de))
        sys.exit(1)


def get_desktop_environment():
    # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else:  # Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None:
            desktop_session = desktop_session.lower()
            if desktop_session in ("gnome", "unity", "cinnamon", "mate",
                                   "xfce4", "lxde", "fluxbox", "blackbox",
                                   "openbox", "icewm", "jwm", "afterstep",
                                   "trinity", "kde", "pantheon", "i3",
                                   "gnome-classic"):
                return desktop_session

            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if
            # using LXDE. There is no guarantee that they will not do the same
            # with the other desktop environments.
            elif ("xfce" in desktop_session
                  or desktop_session.startswith("xubuntu")):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"       
            elif desktop_session.startswith("lubuntu"):
                return "lxde" 
            elif desktop_session.startswith("kubuntu"): 
                return "kde" 
            elif desktop_session.startswith("razor"): # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if "deprecated" not in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        # From http://ubuntuforums.org/showthread.php?t=652320
        elif is_running("xfce-mcs-manage"):
            return "xfce4"
        elif is_running("ksmserver"):
            return "kde"

    # We couldn't detect it so far, so let's try one last time
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")
    if current_desktop:
        current_desktop = current_desktop.lower()
        if current_desktop in ["gnome", "unity", "kde"]:
            return current_desktop

        # Special Cases
        elif current_desktop == "xfce":
            return "xfce4"
        elif current_desktop == "x-cinnamon":
            return "cinnamon"

    return "unknown"


def has_program(program):
    try:
        check_output("which {}".format(program).split())
        return True
    except CalledProcessError:
        return False


def is_running(process):
    try:
        check_output("pidof {}".format(process).split())
        return True
    except CalledProcessError:
        return False
