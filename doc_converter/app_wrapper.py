import os
import logging
import subprocess
import threading
import requests
import time
import shutil
import ntpath
import typing


logger = logging.getLogger(__name__)


class DocConverter(object):
    def __init__(self,
                 convert_to: str = "png",
                 in_dir: str = None,
                 out_dir: str = None,
                 clean_dirs: bool = True,
                 filepath: str = None,
                 *args, **kwargs):
        if filepath and in_dir:
            raise Exception('Cannot supply keyword args filepath and in_dir to same instance')
        self.in_dir = in_dir or os.getenv('IN_DIR', None) or os.path.join(os.getcwd(), "in")
        self.filepath = filepath
        self.out_dir = out_dir or os.getenv('OUT_DIR', None) or os.path.join(os.getcwd(), "out")
        self.convert_to = convert_to
        self.clean_dirs = clean_dirs
        self.validate_conversion()
        self.start_docker_app()
        self._init_out_dir()

    def start_docker_app(self):  # noqa: C901
        try:
            print("Docker starting.  This may take a moment")
            self.docker_process = subprocess.Popen(["docker-compose", "up"], stdout=subprocess.PIPE)
            app_starting = True
            api_started = False
            worker_started = False
            while app_starting:
                if self.docker_process.stdout:
                    output = self.docker_process.stdout.readline().decode('utf-8')
                    if output == '' and self.docker_process.poll() is not None:
                        raise Exception('The Docker subprocess has closed.  Please try again.  Is Docker installed on your system?')
                    if output:
                        if 'Application startup complete' in output:
                            api_started = True
                        if 'Connected to redis' in output:
                            worker_started = True
                    if api_started and worker_started:
                        app_starting = False
            print("Application running.")
        except subprocess.CalledProcessError:
            print("Docker could not start the application.  Is Docker installed on your system?")
            exit(1)
        except Exception as ex:
            print(ex.args[0])
            exit(1)

    def validate_conversion(self):
        if self.convert_to not in ["svg", "png"]:
            print('Only "svg" and "png" are valid convert_tos')
            exit(1)

    class ConvertThread(threading.Thread):
        def __init__(self,
                     filename,
                     in_dir,
                     out_dir,
                     convert_to: str = "png",
                     *args,
                     **kwargs):
            self.filename = filename
            self.convert_to = convert_to
            self.server = os.getenv("SERVER", "http://127.0.0.1:8080")
            self.in_dir = in_dir
            self.out_dir = out_dir
            self.file_title = self.path_leaf(self.filename).split(".")[0]
            super(DocConverter.ConvertThread, self).__init__(*args, **kwargs)

        def run(self):
            print("Starting conversion for file: {}".format(self.path_leaf(self.filename)))
            try:
                file_url = self.convert()
                self.poll_for_file(file_url)
                print("File {0} converted to {1}".format(self.filename, self.convert_to))
            except Exception as ex:
                logger.exception(ex)
                print("Conversion failed for file: {}".format(self.filename))

        def convert(self) -> str:
            resp = None
            with open(self.filename, 'rb') as _file:  # type: ignore
                f = {'file': _file}
                resp = requests.post(self.server + '/convert/{0}'.format(self.convert_to), files=f)  # type: ignore
            if resp:
                data = resp.json()
                return str(data["url"])
            else:
                raise Exception('No response from server.  Is Docker installed?')

        def path_leaf(self, path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        def poll_for_file(self, file_url):
            file_bytes = None
            retries = 0
            while not file_bytes:
                resp = requests.get(file_url)
                if resp.status_code == 200:
                    file_bytes = resp.content
                    fname = os.path.join(self.out_dir, self.file_title + "." + self.convert_to)  # type: ignore
                    with open(fname, 'wb+') as f:
                        f.write(file_bytes)
                    return fname
                elif resp.status_code == 202:
                    time.sleep(0.5)
                else:
                    raise Exception('Received and unexpected response from the test server')
                retries += 1
                if retries > 10:
                    raise Exception('This file does not exist')

    def run(self, convert_to: str = None):
        if not convert_to:
            convert_to = self.convert_to
        if self.filepath:
            t = self.run_conversion_thread(self.filepath, convert_to)
            t.join() if t else None
        else:
            threads = []
            for file in os.listdir(self.in_dir):
                fpath = os.path.join(self.in_dir, file)
                t = self.run_conversion_thread(fpath, convert_to)
                threads.append(t)
            [t.join() if t else None for t in threads]  # type: ignore[func-returns-value]
        print("File conversion complete")

    def run_conversion_thread(self, filepath, convert_to) -> typing.Optional[ConvertThread]:
        if os.path.isfile(filepath):
            t = self.ConvertThread(filepath, self.in_dir, self.out_dir, convert_to)
            t.start()
            return t
        else:
            return None

    def _clean_out_dir(self):
        if self.clean_dirs:
            print("Cleaning out file dir {0}: ".format(self.out_dir))
            for file_obj in os.listdir(self.out_dir):
                path = os.path.join(self.out_dir, file_obj)
                try:
                    shutil.rmtree(path)
                except OSError:
                    os.remove(path)

    def _init_out_dir(self):
        if os.path.isdir(self.out_dir):
            self._clean_out_dir()
        else:
            os.mkdir(self.out_dir)

    def __del__(self):
        print("Shutting down docker.")
        subprocess.run(["docker-compose", "down"])
