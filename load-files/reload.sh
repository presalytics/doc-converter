#!/usr/bin/env bash
set -exv
. ./../../.env
rm -f nginx.conf
sed "s|DC_LISTEN_PORT|${DocConverterPort}|g
    s|DC_SERVER|${DocConverterServer}|g" nginx_conf.tmpl > nginx.conf
echo "Listen Port: ${DocConverterPort}"
echo "IP Address: ${DocConverterServer}"
docker stop doc_converter || true && docker rm doc_converter || true
docker build ./.. -t doc_converter --no-cache --build-arg DocConverterPort=${DocConverterPort} --build-arg DocConverterServer=${DocConverterServer} --build-arg DocConverterRemoteDebugPort=${DocConverterRemoteDebugPort}
docker run -d -t -p ${DocConverterServer}:${DocConverterPort}:${DocConverterPort} -p ${DocConverterServer}:${DocConverterRemoteDebugPort}:${DocConverterRemoteDebugPort} --name doc_converter --env-file ./../../.env doc_converter
docker logs doc_converter