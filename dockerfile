FROM libreoffice_python

ENV DocConverterPort ${DocConverterPort}
ENV DocConverterServer ${DocConverterServer}

ADD requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /srv/doc_converter
WORKDIR /srv/doc_converter

# RUN export DocConverterPort \
#     && export DocConverterServer \
#     && chmod +x update-nginx.sh \
#     && ./update-nginx.sh

RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/sites-available
RUN chmod +x start.sh


EXPOSE ${DocConverterPort}

CMD [ "./start.sh" ]