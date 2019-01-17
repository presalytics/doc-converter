import os, logging, sys
from uwsgidecorators import spool, cron
from subprocess import Popen, PIPE

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

logger.info("Logger Initialized")

@spool(pass_arguments=True)
def svg_convert(args):
    command = [
        "soffice",
        "--headless",
        "--invisible",
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
    p = Popen(command, stdout=PIPE, stderr=PIPE, bufsize=-1, close_fds=True)
    output, err = p.communicate()
    rc = p.returncode
    if rc != 0 or str(err) != '':
        logger.error("Spooler error: {}, {}, {}, {}".format(str(rc), args['filename'], str(err), str(output)))
        raise IOError("spool error from svg_convert.  Filename: {}".format(args['filename']))
    
