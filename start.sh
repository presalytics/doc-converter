#!/usr/bin/env bash
set -exv
echo "creating symbolic link to sites-avialable"
ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled
echo "Start nginx server"
service nginx restart

echo "launching uwsgi"
uwsgi --ini uwsgi.ini

