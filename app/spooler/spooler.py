import os, logging, sys
from environs import Env
from uwsgidecorators import spool, cron
from subprocess import Popen, PIPE, call

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
    # logger.debug("command args: {}".format(command))
    p = Popen(command, stdout=PIPE, stderr=PIPE, env=BASE_ENV)
    output, err = p.communicate()
    # strcommand = "HOME=/tmp/uploads && " + ' '.join(command)
    # logger.debug(strcommand)
    # os.system(strcommand)
    # os.system("echo $USER")
    rc = p.returncode
    if rc != 0:
        logger.error("Spooler error: {}, {}, {}, {}".format(str(rc), args['filename'], str(err), str(output)))
        raise IOError("spool error from svg_convert.  Filename: {}".format(args['filename']))
    else:
        logger.debug(output)
    
