import time

from wallengine import wallengine, config

import logging

# https://docs.python.org/3.6/howto/logging-cookbook.html
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s *%(levelname)s* %(name)s in %(filename)s.%(funcName)s (%(threadName)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=__file__ + ".log",
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger("").addHandler(console)

engine = wallengine.WallEngine(
    wall_cache_dir=config.directory,
    wall_cache_size=int(config.slideshow_screens * 60 / config.slideshow_minutes),  #  cache for 60 minutes
    wall_cache_tags=config.tags,
    wall_cache_rng_pool_size=config.rng_pool_size
    )

while True:
    # Windows wallpaper picture setting
    engine.next_wallpaper()
    time.sleep(config.slideshow_minutes * 60)

    """
    # Windows wallpaper: slideshow setting
    engine.renew_wall_cache(cleanup_files=True)
    time.sleep(config.slideshow_minutes * 60 * 2 * 0.8)
    """
