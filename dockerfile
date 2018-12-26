FROM python:3-stretch

RUN apt-get remove -y --purge libreoffice* libexttextcat-data* && sudo apt-get -y autoremove

# Install wget
RUN apt-get update -y && \
    apt-get install -y wget

# Install LibreOffice 
