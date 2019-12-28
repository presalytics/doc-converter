""" Cron job to cleanup temp files """
import os, logging, time, shutil
from doc_converter.config import UPLOAD_FOLDER, DOWNLOAD_FOLDER
try:
    from uwsgidecorators import cron #cannot run this in debug mode on local machine, uwsgi must be running
except:
    # Creates a null cron decorator for debugging purposes
    from functools import wraps
    def cron(*args, **kwargs):
        def wrapper(*args, **kwargs):
            pass
        return wrapper

    def empty_func():
        pass

    empty_func = cron(empty_func)

cleanup_folders = [
    UPLOAD_FOLDER,
    DOWNLOAD_FOLDER
]

logger = logging.getLogger('doc_converter.cleaner')

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
            try:
                creation_time = os.path.getctime(file_path)
            except FileNotFoundError:
                message = "Skipping cleanup for temp file.  File not found: {0}".format(file_path)
                logger.error(message)
                continue
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

