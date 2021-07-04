#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

echo "Starting libreoffice headless process in background"
libreoffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service" --norestore --nologo --nodefault --headless -env:UserInstallation=file:///tmp/libreoffice &
echo "Waiting for libreoffice to initialize"
sleep 5
echo "Starting celery..."
python3 -m celery -A doc_converter.celery.celery_app worker --loglevel=DEBUG -P solo