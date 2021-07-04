import logging
import io
import uuid
import os
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request,
    status
)
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
from doc_converter import util  # type: ignore
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.processmgr.redis_wrapper import RedisWrapper


logger = logging.getLogger(__name__)


app = FastAPI(root_path=util.ROOT_PATH)


@app.get("/")
def home():
    return RedirectResponse(url="/docs")


@app.post('/convert/svg')
def svgconvert(request: Request, file: UploadFile = File(...)):
    """
    Converts the uploaded file to an svg file.
    """
    try:
        pm = ProcessMgr.from_upload_file(file, "svg")
        pm.reserve_cache_key()
        pm.handoff_to_worker()
        content = {
            "cacheKey": pm.redis_key,
            "status": "processing",
            "url": "{0}://{1}{2}/svg/{3}".format(request.url.scheme, request.url.netloc, request.scope.get("root_path"), pm.redis_key)
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(status_code=400, detail="Your file could not be read.  Please modify your request and try again.")


@app.post('/convert/png')
def pngconvert(request: Request, file: UploadFile = File(...)):
    """
    Converts the uploaded file to an png file.
    """
    try:
        pm = ProcessMgr.from_upload_file(file, "png")
        pm.reserve_cache_key()
        pm.handoff_to_worker()
        content = {
            "cacheKey": pm.redis_key,
            "status": "processing",
            "url": "{0}://{1}{2}/png/{3}".format(request.url.scheme, request.url.netloc, request.scope.get("root_path"), pm.redis_key)
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(status_code=400, detail="Your file could not be read.  Please modify your request and try again.")


@app.get('/png/{id}')
def png_get(id: uuid.UUID, request: Request):
    r = RedisWrapper.get_redis()
    key = "png-" + str(id)
    file_content = r._redis.get(key)
    if file_content == b'\x00':
        content = {
            "cacheKey": str(id),
            "status": "processing",
            "url": str(request.url)
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    elif not file_content:
        raise HTTPException(status_code=404, detail="This file has expried (or never existed), please retry conversion")
    return StreamingResponse(io.BytesIO(file_content), media_type="image/png")


@app.get('/svg/{id}')
def svg_get(id: uuid.UUID, request: Request):
    r = RedisWrapper.get_redis()
    key = "svg-" + str(id)
    file_content = r._redis.get(key)
    if file_content == b'\x00':
        content = {
            "cacheKey": str(id),
            "status": "processing",
            "url": str(request.url)
        }
        return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
    elif not file_content:
        raise HTTPException(status_code=404, detail="This file has expried (or never existed), please retry conversion")
    return StreamingResponse(io.BytesIO(file_content), media_type="image/svg+xml")


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
