import subprocess
import os

slideshow_minutes = 16  # minutes until wallpaper swaps

slideshow_screens = 3  # number of screens/monitors you are using

directory = "wallpapers"
version = subprocess.check_output("git describe --tag --long --always --dirty", cwd=os.path.dirname(os.path.abspath(__file__))).decode("utf8", errors="ignore").strip()

rng_pool_size = 320  # pool size to pick submissions from. maximum 320 https://e621.net/help/api

tags = [
    #
    # recommended tags
    "-animated",
    "-comic",
    "order:score",
    "date:month",  # also works with date:month or date:4_weeks_ago
    #
    # size tags
    #"width:>2560",  # use width if you select "fill" in wallpaper settings
    "height:>1439",  # use height if you select "fit" in wallpaper settings
    #
    # rating tags
    #"rating:s",
    #
    # user tags (owo)
    "big_breasts",
    "-sonic_the_hedgehog_(series)"
]

e6apis = [
    "e621.net",
    "e6ai.net"
]

if rng_pool_size > 320 or rng_pool_size < 1:  # hard limit of 320 https://e621.net/help/api
    rng_pool_size = 320
