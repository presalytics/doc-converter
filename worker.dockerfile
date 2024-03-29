FROM presalytics/libreoffice-python:latest

# when supervisord for python3 (supervisor v4+) gets installed in the pip package direcotry, install supervisor with requirements.txt.  Temporaliyt install from source
ADD ./requirements.txt .
RUN pip3 install -U pip \
    && pip3 install -r requirements.txt


COPY . /srv/doc_converter
WORKDIR /srv/doc_converter


COPY ./.bashrc /root
COPY ./run_worker.sh /bin
RUN  mkdir /var/www/.config /var/www/.config/dconf /tmp/libreoffice /tmp/convert \ 
    && chown -R www-data:www-data /var/www /srv/doc_converter \
    && chmod -R 777 /tmp /var/www /srv

EXPOSE 5679

CMD [ "run_worker.sh" ]