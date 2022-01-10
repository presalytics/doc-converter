import requests
import logging
import uuid
import base64
import mimetypes
import json
from cloudevents.http import CloudEvent, to_binary
from doc_converter.processmgr.processmgr import ProcessMgr
from doc_converter.util import EVENT_BROKER_URL, EVENT_SOURCE


logger = logging.getLogger(__name__)


class SimpleEventEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            return super(SimpleEventEncoder, self).default(obj)


def emit_event(process_mgr: ProcessMgr):
    event_type = "doc_converter." + process_mgr.convert_type + "_created"
    filename = process_mgr.key + "." + process_mgr.convert_type
    attributes = {
        "type": event_type,
        "subject": filename,
        "id": str(uuid.uuid4()),
        "source": EVENT_SOURCE
    }

    data = {
        "resourceId": process_mgr.key,
        "userId": process_mgr.metadata.get("userId", None),
        "file": base64.b64encode(process_mgr.storage.get_file()).decode("utf-8"),
        "filename": filename,
        "MIMEType": mimetypes.MimeTypes().guess_type(filename)[0]
    }

    event = CloudEvent(attributes, data)

    headers, body = to_binary(event)
    headers["Content-Type"] = "application/json"  # type: ignore

    if EVENT_BROKER_URL:
        body_json = json.dumps(body, cls=SimpleEventEncoder)
        resp = requests.post(EVENT_BROKER_URL, data=body_json, headers=headers)
        if resp.ok:
            logger.info("Event Id {0} Sent to {1}.  Event broker responded with status code: {2}".format(attributes.get("id"), EVENT_BROKER_URL, resp.status_code))
        else:
            logger.error("Event broker responded status code {0} with error message {1}".format(resp.status_code, resp.text))
    else:
        logger.info("No EVENT_BROKER_URL provided. No event emitted {}".format(event._attributes['subject']))
