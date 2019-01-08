FROM libreoffice_python

ENV DocConverterPort ${DocConverterPort}
ENV DocConverterServer ${DocConverterServer}

# when supervisord for python3 (supervisor v4+) gets installed in the pip package direcotry, install supervisor with requirements.txt.  Temporaliyt install from source
ADD ./load-files/requirements.txt .
RUN pip3 install -r requirements.txt \
    && apt-get install -y git \
    && pip3.7 install git+https://github.com/Supervisor/supervisor

COPY . /srv/doc_converter
WORKDIR /srv/doc_converter

# RUN export DocConverterPort \
#     && export DocConverterServer \
#     && chmod +x update-nginx.sh \
#     && ./update-nginx.sh

RUN rm /etc/nginx/sites-enabled/default
COPY ./load-files/nginx.conf /etc/nginx/sites-available
COPY ./load-files/doc_converter.service /etc/systemd/system/doc_converter.service
COPY ./load-files/supervisord.conf /etc/supervisord.conf
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled
#RUN chmod +x start.sh \
#    && chmod +x status.sh


EXPOSE ${DocConverterPort}

CMD [ "supervisord" ]