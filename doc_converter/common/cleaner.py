""" Cron job to cleanup temp files """
import os, logging, time, shutil
from uwsgidecorators import cron
from config import UPLOAD_FOLDER, DOWNLOAD_FOLDER

cleanup_folders = [
    UPLOAD_FOLDER,
    DOWNLOAD_FOLDER
]

try:
    logger.info("Cleanup cron job intialized.")
except:
    pass

@cron(-1, -1, -1, -1, -1)
def cleanup_files(num):
    """
    Cleans up upload and download folders
    """
    current_time = time.time()
    files_cleared = 0
    for fld in cleanup_folders:
        for the_file in os.listdir(fld):
            file_path = os.path.join(fld, the_file)
            creation_time = os.path.getctime(file_path)
            if (current_time - creation_time) > 1800:
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        files_cleared += 1
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(e)
    if (files_cleared > 0):
        logger.info("Cleanup operation complete. {} files cleared.".format(files_cleared))

