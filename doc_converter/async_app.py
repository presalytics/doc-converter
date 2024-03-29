import logging
import os
import io
import pathlib
import uuid
import typing
import queue
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request,
    status,
    Form,
    BackgroundTasks
)
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi_utils.tasks import repeat_every
from doc_converter import util  # type: ignore
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.util import EVENT_BROKER_URL, MAX_JOB_RETRIES
from doc_converter.emitter import emit_event


logger = logging.getLogger(__name__)


app = FastAPI(root_path=util.ROOT_PATH)


TASK_QUEUE: queue.Queue = queue.Queue()


IS_PROCESSING = False


class TaskArgs(object):
    upload_file: UploadFile
    convert_type: str
    metadata: typing.Dict

    def __init__(self, upload_file, convert_type, metadata={}, *args, **kwargs):
        self.upload_file = upload_file
        self.convert_type = convert_type
        self.metadata = metadata


@app.get("/")
def home():
    return RedirectResponse(url="/docs")


def conversion_task(upload_file: UploadFile, convert_type: str, metadata: typing.Dict = {}):
    logger.info("File conversion started for {0} to {1}".format(upload_file.filename, convert_type))
    retry_loop_on = True
    retries = 0
    while (retry_loop_on):
        try:
            pm = ProcessMgr.from_upload_file(upload_file, convert_type, metadata=metadata, mode=ProcessMgr.Modes.IN_PROCESS)
            pm.convert()
            emit_event(pm)
            retry_loop_on = False
        except Exception as ex:
            try:
                pm.teardown()
                pm.storage.clean()
            except Exception:
                pass
            if retries < MAX_JOB_RETRIES:
                retries += 1
            else:
                logger.exception(ex, "Conversion failed.  Max retry attempts exceeded.")
                retry_loop_on = False
                raise ex


@app.on_event("startup")
@repeat_every(seconds=0.1, logger=logger, wait_first=True)
def conversion_loop():
    global IS_PROCESSING
    global TASK_QUEUE
    if not IS_PROCESSING and not TASK_QUEUE.empty():
        next_task: TaskArgs = TASK_QUEUE.get()
        logger.debug("Conversion task pulled from queue.  id: {0}, convertType: {1}, size: {2}".format(
            next_task.metadata.get("id", None),
            next_task.convert_type,
            next_task.upload_file.file._file.getbuffer().nbytes
        ))  # type: ignore
        IS_PROCESSING = True
        conversion_task(next_task.upload_file, next_task.convert_type, next_task.metadata)
        IS_PROCESSING = False
        TASK_QUEUE.task_done()


@app.post('/convert')
def svgconvert(request: Request,
               background_tasks: BackgroundTasks,
               file: UploadFile = File(...),
               convertType: str = Form(...),
               userId: str = Form(...),
               id: str = Form(...),
               storyId: str = Form(...)):
    """
    Converts the uploaded file to an svg file.
    """
    try:
        task_args = TaskArgs(file, convertType, metadata={"id": id, "userId": userId, "storyId": storyId})
        logger.debug("Conversion request received.  id: {0}, convertType: {1}, size: {2}".format(id, convertType, file.file._file.getbuffer().nbytes))  # type: ignore
        TASK_QUEUE.put(task_args)
        content = {
            "id": id,
            "status": "processing. Wait for event emitted from {0}".format(EVENT_BROKER_URL)
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(status_code=400, detail="Your file could not be read.  Please modify your request and try again.")


def get_api_description():
    readme = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    description = ''
    with open(readme, 'r') as f:
        description = f.read()
    return description.replace('Presalytics Doc Converter', '')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Presalytics Doc Converter",
        version="1.0.0",
        description=get_api_description(),
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://presalytics.blob.core.windows.net/media/filer_public_thumbnails/filer_public/ed/0e/ed0e957a-d585-4094-a788-caf03e31b66d/icon_transparent_orange_lg.png__900x900_q85_subsampling-2.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


def boot_test():
    fname = "Rectangle.pptx"
    test_filepath = pathlib.Path(__file__).parent.joinpath("test_files").joinpath(fname)
    with open(test_filepath, 'rb') as f:
        file_object = io.BytesIO(f.read())
    file = UploadFile(fname, file_object)
    conversion_task(file, "svg", metadata={"id": str(uuid.uuid4()), "userId": uuid.uuid4()})


try:
    boot_test()
    logger.info("Boot test completed successfully.")
except Exception as ex:
    logger.exception(ex, "Boot Tests Failed.  Exiting...")
    exit(1)
