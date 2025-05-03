import os
from datetime import datetime
import random
import ctypes

from winotify import Notification

from wallengine import wallfiles
from wallengine import config

import logging

logger = logging.getLogger("wallengine")

class WallEngine:
    def __init__(self, wall_cache_dir, wall_cache_size, wall_cache_tags, wall_cache_rng_pool_size=320):
        if not os.path.isdir(wall_cache_dir):
            os.mkdir(wall_cache_dir)
        self.wall_cache_dir = wall_cache_dir
        self.wall_cache_size = wall_cache_size
        self.wall_cache_tags = wall_cache_tags
        self.wall_cache_pool_size=wall_cache_rng_pool_size
        self.cache_imgs = self.get_current_cache()
        self.renew_wall_cache()

    def renew_wall_cache(self, cleanup_files=False):
        """
        Update/Rotate wallpapers with new content.
        :param cleanup_files: set True if old files should be deleted
        :return:
        """
        """
        
        :return:
        """
        new_wallpapers = wallfiles.download_wallpapers(tags=self.wall_cache_tags,
                                                   download_dir=self.wall_cache_dir,
                                                   amount=self.wall_cache_size,
                                                   pool_size=self.wall_cache_pool_size,
                                                   api=random.choice(config.e6apis))
        logger.info("Current walls: " + str(new_wallpapers))
        if cleanup_files:
            wallfiles.trash_files(self.cache_imgs)
        self.cache_imgs = new_wallpapers
        self.img_pos = 0
        return new_wallpapers

    def get_current_cache(self):
        """
        Get current files in img_cache dir.
        :return: files in cache
        """
        cache = wallfiles.get_files_in_dir(self.wall_cache_dir)
        logger.info("Found wallpapers in cache: " + str(cache))
        return cache

    def next_wallpaper(self):
        """
        Set wallpaper to next in cache.
        :return: Return code of SystemParametersInfoW
        https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
        """
        if len(self.cache_imgs) <= 0:
            self.renew_wall_cache()
        w = self.cache_imgs.pop(0)
        wallpaper = os.path.abspath(w['file_path'])
        logger.info("Setting wallpaper to " + str(wallpaper))
        # SPI_SETDESKWALLPAPER = 0x0014
        sysparamw_return = ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, wallpaper, 0)
        logger.debug("SystemParametersInfoW Return: " + str(sysparamw_return))
        with open('wallpaper-history.txt', 'a+') as f:
            f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {w['post_url']}\n')
        toast = Notification(app_id="Wallpaper Engine",
                             title=datetime.now().strftime("@%H:%M:%S"),
                             msg=w['post_url'],
                             duration="long",
                             icon=os.path.dirname(os.path.realpath(__file__)) + '/notification.ico',
                             )
        toast.add_actions(label=f"{w['site']} Post", launch=w['post_url'])
        toast.show()
        return sysparamw_return
