from wallengine import config

import requests

import random
import os
import send2trash

import logging

logger = logging.getLogger("wallfiles")

def download_wallpapers(tags, api, download_dir, amount, pool_size):
    """
    Get files from e621.net
    :param tags: e621 tags
    :param download_dir: target download directory
    :param amount: amount of files to be downloaded
    :param pool_size: pool size to download from
    :return:
    """
    submissions = get_submissions(tags, api, amount, pool_size)
    walls = download_submissions(submissions, download_dir)
    return walls


def trash_files(files):
    """
    Put list of files into recycle bin
    :param files: list of files
    :return:
    """
    for file in files:
        try:
            send2trash.send2trash(file)
        except Exception as e:
            logger.error('Could not remove file ' + str(file) + '. Exception: ' + str(e))


def get_files_in_dir(fdir):
    """
    Get files in directory.
    :param fdir: directory to be scanned
    :return: list of files in directory
    """
    files = []
    for file in os.listdir(os.path.join(fdir)):
        files.append(os.path.join(".", fdir, file))
    return files


def _download_file(url, filename, overwrite=False):
    """
    Download a file via stream.
    :param url: url to download
    :param filename: filename to download to
    :param overwrite: overwrite file if it exists
    :return: filename to download to
    """
    logger.info("Downloading " + str(url) + " -> " + str(filename))
    if os.path.isfile(filename) and overwrite:
        logger.warning("File already exists! Skipping..")
        return filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk:
                    f.write(chunk)
    return filename


def get_submissions(tags, api, amount=16, pool_size=320):
    """
    Get submissions from e621.net: https://e621.net/help/api
    :param tags: list of tags for e621
    :param amount: size of samples
    :param pool_size: submission pool size to take the samples from
    :return: list of randomly picked submissions
    """

    api_url = f'https://{api}/posts.json?tags={'+'.join(tags)}&limit={pool_size}'
    logger.debug('Getting e6 api call json for ' + api_url)
    r = requests.get(api_url, allow_redirects=True, headers={'User-Agent': f'wallpaper engine {config.version} by femtoAmpere'})

    if not "posts" in r.json():
        logger.error('Could not get posts from e6 api. Response: ' + str(r.json()))
        return []
    
    submissions = []
    for submission in r.json()["posts"]:
        if submission["file"]["url"] and submission["id"] not in submissions:
            logger.debug("Adding submission " + str(submission["id"]))
            submission['site'] = api
            submission['post_url'] = f'https://{api}/posts/{submission["id"]}'
            submissions.append(submission)
            continue
        logger.warning("Could not get submissions: " + str(submissions))

    _ = random.shuffle(submissions)
    return submissions[:amount]


def download_submissions(submissions, target_dir):
    """
    Download a submission from e621.net
    :param submissions: list of submissions (https://e621.net/help/api)
    :param target_dir: directory to download submissions to
    :return: list of filenames of downloaded submissions
    """
    downloaded = []
    for submission in submissions:
        groupdir = os.path.join(target_dir, submission['site'])
        if not os.path.isdir(groupdir):
            os.mkdir(groupdir)
        fname = os.path.join(".", groupdir, str(submission['id']) + '.' + submission['file']['ext'])

        try:
            submission['file_path'] = _download_file(submission['file']['url'], fname)
            downloaded.append(submission)
        except Exception as e:
            logger.error('Could not download post ' + str(submission[1]['id']) + '. Exception: ' + str(e))
    return downloaded
