FROM libreoffice_python

ENV DocConverterPort ${DocConverterPort}
ENV DocConverterServer ${DocConverterServer}

# when supervisord for python3 (supervisor v4+) gets installed in the pip package direcotry, install supervisor with requirements.txt.  Temporaliyt install from source
ADD ./load-files/requirements.txt .
RUN pip3 install -r requirements.txt \
    && mkdir /var/log/uwsgi

COPY . /srv/doc_converter
WORKDIR /srv/doc_converter


RUN rm /etc/nginx/sites-enabled/default
COPY ./load-files/nginx.conf /etc/nginx/sites-available
COPY ./load-files/doc_converter.service /etc/systemd/system/doc_converter.service
COPY ./load-files/supervisord.conf /etc/supervisord.conf
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled \
    && chown -R www-data:www-data ./app/log ./app/upload ./app/download
#RUN chmod +x start.sh \
#    && chmod +x status.sh


EXPOSE ${DocConverterPort}
#EXPOSE ${DocConverterRemoteDebugPort}

CMD [ "supervisord" ]