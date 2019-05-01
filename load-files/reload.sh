#!/usr/bin/env bash
set -exv
. ./../../.env
rm -f nginx.conf
sed "s|DC_LISTEN_PORT|${DocConverterPort}|g
    s|DC_SERVER|${DocConverterServer}|g" nginx_conf.tmpl > nginx.conf
echo "Listen Port: ${DocConverterPort}"
echo "IP Address: ${DocConverterServer}"
docker stop doc-converter || true && docker rm doc-converter || true
docker build ./.. -t doc-converter --no-cache --build-arg DocConverterPort=${DocConverterPort} --build-arg DocConverterServer=${DocConverterServer} --build-arg DocConverterRemoteDebugPort=${DocConverterRemoteDebugPort}
docker run -d -t --network=host -p ${DocConverterServer}:${DocConverterPort}:${DocConverterPort} -p ${DocConverterServer}:${DocConverterRemoteDebugPort}:${DocConverterRemoteDebugPort} --name doc-converter --env-file ./../../.env doc-converter
docker logs doc-converter