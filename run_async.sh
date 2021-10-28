#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

echo "Starting libreoffice headless process in background"
libreoffice --accept="socket,host=localhost,port=8100;urp;StarOffice.Service" --norestore --nologo --nodefault --headless -env:UserInstallation=file:///tmp/libreoffice &
echo "Waiting for libreoffice to initialize"
sleep 5
echo "Starting application..."
python3 -m uvicorn doc_converter.async_app:app --host 0.0.0.0 --port 80