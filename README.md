# himawaripy
*Put near-realtime picture of Earth as your desktop background*

himawaripy is a Python 3 script that fetches near-realtime (10 minutes delayed)
picture of Earth as its taken by
[Himawari 8 (ひまわり8号)](https://en.wikipedia.org/wiki/Himawari_8) and sets it
as your desktop background.

Set a cronjob that runs in every 10 minutes to automatically get the
near-realtime picture of Earth.

## Supported Desktop Environments
### Tested
* Unity 7

### Not Tested
* GNOME 3
* MATE
* LXDE
* KDE

### Not Supported
* any other desktop environments that are not mentioned above.

## Configuration
You can configure the level of detail, by modifying the script. You can set the
global variable `LEVEL` to `4`, `8`, `16`, or `20` to increase the quality (and
thus the file size as well). Please keep in mind that it will also take more
time to download the tiles.

You can also change the path of the latest picture, which is by default
`~/.config/himawari/himawari-latest.png`, by changing the `OUTPUT_FILE` variable.

## Installation
    cd /path/to/your/scripts
    git clone https://github.com/masasin/himawaripy.git
    
    # configure
    cd himawaripy
    vi himawaripy.py
    
    # test whether it's working
    ./himawaripy.py
    
    # set up a cronjob
    crontab -e
    # Add these lines:
    USER_HOME = /home/yourusername
    
    */10 * * * * $USER_HOME/path/to/your/scripts/himawaripy/himawaripy.py
    
### For KDE Users
> So the issue here is that KDE does not support changing the desktop wallpaper
> from the commandline, but it does support polling a directory for file changes
> through the "Slideshow" desktop background option, whereby you can point KDE
> to a folder and have it load a new picture at a certain interval.
>
> The idea here is to:
>
> * Set the cron for some interval (say 9 minutes)
> * Open Desktop Settings -> Wallpaper -> Wallpaper Type -> Slideshow
> * Add the `~/.config/himawari` dir to the slideshow list
> * Set the interval check to 10 minutes (one minute after the cron, also
>   depending on your download speed)

Many thanks to [xenithorb](https://github.com/xenithorb) [for the solution](https://github.com/xenithorb/himawaripy/commit/01d7c681ae7ce47f639672733d0f734574662833)!

## Example
![Earth, as 2016/02/04/13:30:00 GMT](http://i.imgur.com/4XA6WaM.jpg)
    
## Attributions
Thanks to *[Bora Alper](https://github.com/boramalper)* for the initial Python
implementation. I made it a bit more Pythonic and added logging, but his also
seems to still be under active development.

Thanks to *[MichaelPote](https://github.com/MichaelPote)* for the [initial
implementation](https://gist.github.com/MichaelPote/92fa6e65eacf26219022) using
Powershell Script.

Thanks to *[Charlie Loyd](https://github.com/celoyd)* for image processing logic
([hi8-fetch.py](https://gist.github.com/celoyd/39c53f824daef7d363db)).

Obviously, thanks to the Japan Meteorological Agency for opening these pictures
to public.
