import os 
import logging 
import re
import io
import uuid
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request,
    status
)
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from doc_converter import util  # type: ignore
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.processmgr.redis_wrapper import RedisWrapper


logger = logging.getLogger(__name__)


app = FastAPI(root_path=util.ROOT_PATH)


app.get("/")
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
        raise HTTPException(status=404, detail="This file has expried (or never existed), please retry conversion")
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
        raise HTTPException(status=404, detail="This file has expried (or never existed), please retry conversion")
    return StreamingResponse(io.BytesIO(file_content), media_type="image/svg+xml")


