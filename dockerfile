FROM libreoffice_python

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
COPY ./load-files/.bashrc /root
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled \
    && if [ -d ./doc_converter/log ] ; then rm -r ./doc_converter/log ; fi \
    && mkdir /tmp/uploads /tmp/downloads /tmp/svgspool ./doc_converter/docs ./doc_converter/log \
    && chown -R www-data:www-data ./doc_converter/log /tmp/uploads /tmp/downloads /tmp/svgspool ./doc_converter/docs
    
EXPOSE 5002

CMD [ "supervisord" ]