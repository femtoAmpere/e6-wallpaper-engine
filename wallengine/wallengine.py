import os
from datetime import datetime
import ctypes

from wallengine import files

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
        new_wallpapers = files.download_wallpapers(tags=self.wall_cache_tags,
                                                   download_dir=self.wall_cache_dir,
                                                   amount=self.wall_cache_size,
                                                   pool_size=self.wall_cache_pool_size)
        logger.info("Current walls: " + str(new_wallpapers))
        if cleanup_files:
            files.trash_files(self.cache_imgs)
        self.cache_imgs = new_wallpapers
        self.img_pos = 0
        return new_wallpapers

    def get_current_cache(self):
        """
        Get current files in img_cache dir.
        :return: files in cache
        """
        cache = files.get_files_in_dir(self.wall_cache_dir)
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
        wallpaper = os.path.abspath(self.cache_imgs[0])
        _ = self.cache_imgs.pop(0)
        logger.info("Setting wallpaper to " + str(wallpaper))
        with open('wallpapers.txt', 'a+') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + str(wallpaper) + "\n")
        # SPI_SETDESKWALLPAPER = 0x0014
        sysparamw_return = ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, wallpaper, 0)
        logger.debug("SystemParametersInfoW Return: " + str(sysparamw_return))
        return sysparamw_return
