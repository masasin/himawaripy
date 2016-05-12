# http://stackoverflow.com/a/21213358/4466589
import os
import sys
from subprocess import call, check_output
import re

from config import OUTPUT_FILE, logger


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
                                   "trinity", "kde"):
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
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
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


def is_running(process):
    # From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
    # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
    try:  # Linux/Unix
        s = check_output("ps axw".split())
    except:  #Windows
        s = check_output("tasklist /v".split())
    for x in s.stdout:
        if re.search(process, str(x)):
            return True
    return False


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
