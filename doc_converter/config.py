""" module for loading configuration defaults.  gets overriden by environment variables """
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'upload')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'download')
