#!/usr/bin/env python3
import os
from app.converter import app as application

if __name__ == '__main__':
    application.run(host=os.environ.get('DocConverterServer'), port=os.environ.get('DocConverterPort'))
