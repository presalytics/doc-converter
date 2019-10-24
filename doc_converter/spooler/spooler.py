import os, logging, sys, time, shutil
from environs import Env
from subprocess import Popen, PIPE, call
from doc_converter.common.util import dictConfig
from doc_converter.storage.storagewrapper import Blobber
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

try:
    svg_blobber = Blobber()
except:
    logger.warning("Connection to Azure storage failed.  Unable to interact with blob storage")

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
        blob_name = args['blob_name']
        if blob_name is not None:
            upload_to_blob(blob_name, new_svg_path)

        logger.info("Spooler request completed.")

    except Exception as ex:
        logger.error(ex)

def strip_scripts(filename):
    """ function to strip javascript out of svg file to reduce filesize.
        NOTE:  Not implemented.  function works, just need to figure
        out how to load js library front end.

        TODO: add libreoffice scripts to javascript library so svg
            files can be displayed without embedded js.
    """
    stop = "<script type=".encode('utf-8')
    temp_filename = filename + ".tmp"
    with open(filename, encoding='utf-8') as infile, open(temp_filename, 'w', encoding='utf-8') as outfile:
        buff = []
        for line in infile:
            line = line.encode('utf-8')
            if stop not in line:
                buff.append(line)
                continue
            if stop in line:
                logger.debug("Stop found")
                buff.append("</svg>".encode('utf-8'))
                break
        outlist = [x.decode('utf-8') for x in buff]
        outfile.write(''.join(outlist))
        buff = []
    os.rename(temp_filename, filename)

def upload_to_blob(blob_name, filename):
    svg_blobber.put_blob(
        blob_name=blob_name,
        filepath=filename
    )

    


