import os, logging, sys, time, shutil
from environs import Env
from subprocess import Popen, PIPE, call
from doc_converter.common.util import dictConfig, strip_scripts, USE_BLOB, USE_REDIS
from doc_converter.storage.storagewrapper import Blobber
from doc_converter.storage.redis_wrapper import RedisWrapper
from doc_converter.config import UPLOAD_FOLDER, DOWNLOAD_FOLDER
from doc_converter.spooler.uno_controller import UnoConverter


try:
    from uwsgidecorators import spool #cannot run this in debug mode on local machine, uwsgi must be running
except:
    # Creates a null spooler decorator for debugging purposes
    from functools import wraps
    def spool(*args, **kwargs):
        def wrapper(*args, **kwargs):
            pass
        return wrapper

    def empty_func():
        pass

    empty_func = spool(empty_func)

logger = logging.getLogger('doc_converter.spooler')

BASE_ENV = os.environ.copy()
BASE_ENV['HOME'] = "/tmp"

cleanup_folders = [
    UPLOAD_FOLDER,
    DOWNLOAD_FOLDER
]

if USE_BLOB:
    try:
        svg_blobber = Blobber()
    except Exception:
        logger.warning("Connection to Azure storage failed.  Unable to interact with blob storage")

if USE_REDIS:
    try:
        r = RedisWrapper()
    except Exception:
        logger.warning("Connection to Redis database failed.  Unable to interact with redis")



# @spool(pass_arguments=True)
# def svg_convert(args):
#     command = [
#         "soffice",
#         "--headless",
#         "--convert-to",
#         "{}:{}".format(args['convert_type'], args['filter']),
#         args['filename'],
#         "--outdir",
#         args['out_dir']
#     ]
#     try:
#          os.remove(args['out_filename'])
#     except:
#         pass
#     logger.debug("command args: {}".format(command))
#     p = Popen(command, stdout=PIPE, stderr=PIPE, env=BASE_ENV) # BASE_ENV changes HOME directory to /tmp so libreoffice can write .cache files as not-root user
#     output, err = p.communicate()
#     # Note: sometimes it's easier to debug os.system than popen when processes hang or terminately silently.  libreoffice has bad error messaging.
#     # strcommand = "HOME=/tmp/uploads && " + ' '.join(command)
#     # logger.debug(strcommand)
#     # os.system(strcommand)

#     rc = p.returncode
#     if rc != 0:
#         logger.error("Spooler error: {}, {}, {}, {}".format(str(rc), args['filename'], str(err), str(output)))
#         raise IOError("spool error from svg_convert.  Filename: {}".format(args['filename']))
#     else:
#         logger.debug(output)
    
#     #add methods for post-processing
#     newfile = args['out_filename']

# #    strip_scripts(newfile)
#     blob_name = args['blob_name']
#     if blob_name is not None:
#         upload_to_blob(blob_name, newfile)


@spool(pass_arguments=True)
def uno_spooler(args):
    logger.info("Spooler request begun")
    converter = UnoConverter(input_dir=UPLOAD_FOLDER, output_dir=DOWNLOAD_FOLDER)
    filename = args["filename"]
    try:
        new_svg_path = converter.convert(filename, "svg")
        # new_file = strip_scripts(new_svg_path) leaving scripts in for now
        blob_name = args['blob_name']
        if blob_name is not None:
            if USE_REDIS:
                try:
                    r.store(new_svg_path, blob_name)
                except Exception as ex:
                    logger.exception(ex)
            if USE_BLOB:
                try:
                    upload_to_blob(blob_name, new_svg_path)
                except Exception as ex:
                    logger.exception(ex)
        logger.info("Spooler request completed.")
    except Exception as ex:
        logger.exception(ex)



def upload_to_blob(blob_name, filename):
    svg_blobber.put_blob(
        blob_name=blob_name,
        filepath=filename
    )

    


