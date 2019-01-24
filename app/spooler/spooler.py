import os, logging, sys
from environs import Env
from uwsgidecorators import spool, cron
from subprocess import Popen, PIPE, call
from doc_converter.app.storage.storagewrapper import Blobber

env = Env()
env_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
if os.path.exists(env_file):
    env.read_env(path=env_file)
else:
    env.read_env()

file_path = os.path.join(os.path.dirname(__file__), '../log/spooler.log')
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(file_path)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

log_level = logging.getLevelName(os.environ.get('DocConverterLogLevel'))
logger.setLevel(log_level)

logger.info("Spooler Logger Initialized")

BASE_ENV = os.environ.copy()
BASE_ENV['HOME'] = "/tmp"

svg_blobber = Blobber()

@spool(pass_arguments=True)
def svg_convert(args):
    command = [
        "soffice",
        "--headless",
        "--convert-to",
        "{}:{}".format(args['convert_type'], args['filter']),
        args['filename'],
        "--outdir",
        args['out_dir']
    ]
    try:
         os.remove(args['out_filename'])
    except:
        pass
    logger.debug("command args: {}".format(command))
    p = Popen(command, stdout=PIPE, stderr=PIPE, env=BASE_ENV) # BASE_ENV changes HOME directory to /tmp so libreoffice can write .cache files as not-root user
    output, err = p.communicate()
    # Note: sometimes it's easier to debug os.system than popen when processes hang or terminately silently.  libreoffice has bad error messaging.
    # strcommand = "HOME=/tmp/uploads && " + ' '.join(command)
    # logger.debug(strcommand)
    # os.system(strcommand)

    rc = p.returncode
    if rc != 0:
        logger.error("Spooler error: {}, {}, {}, {}".format(str(rc), args['filename'], str(err), str(output)))
        raise IOError("spool error from svg_convert.  Filename: {}".format(args['filename']))
    else:
        logger.debug(output)
    
    #add methods for post-processing
    newfile = args['out_filename']
    strip_scripts(newfile)
    blob_name = args['blob_name']
    if blob_name is not None:
        upload_to_blob(blob_name, newfile)


def strip_scripts(filename):
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
        file_path=filename
    )

    


