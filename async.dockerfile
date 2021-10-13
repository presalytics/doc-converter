FROM debian:bullseye-slim as libreofficeBase

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y apt-file \
    && apt-get install -y software-properties-common \
    && apt-get update \
    && apt-file update \
    && apt-get -y install build-essential \
    && apt-get -y install python3-dev \
    && apt-get install -y python3-pip

RUN apt-get update && apt-get install -y libreoffice --no-install-recommends  --no-install-suggests

RUN apt-get update \
    && apt-get install -y fontconfig \
    && apt-get install -y cabextract \
    && apt-get install -y xfonts-utils \ 
    && echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections \
    && apt-get install wget \
    && wget http://ftp.de.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.8_all.deb \
    && dpkg -i ttf-mscorefonts-installer_3.8_all.deb \
    && mkdir ~/.fonts \
    && apt-get install -y wget \
    && wget -qO- http://plasmasturm.org/code/vistafonts-installer/vistafonts-installer | bash \
    && apt clean
    # TODO: ADD OTHER WINDOWS FONTS VIA SERVER

RUN  mkdir /tmp/libreoffice /tmp/convert && chmod -R 777 /tmp/convert /tmp/libreoffice

WORKDIR /app


COPY requirements.txt .

RUN pip3 install -U pip && pip3 install --no-cache-dir -r requirements.txt


COPY ./run_async.sh /bin

ADD ./doc_converter ./doc_converter
ADD README.md .

CMD ["./run_async.sh"]


