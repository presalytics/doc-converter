#! /bin/bash
set -exv
. ./../../.env
PATH=$ProjectRoot/doc_converter/docs:$PATH
PATH_TO_OUTPUT_FOLDER=$ProjectRoot/doc_converter/docs/xml
OUTFILENAME=doc_converter.md
if [ -z "$GROUP" ]; then
    GROUP=$USER
fi
rm -R -f $PATH_TO_OUTPUT_FOLDER
rm -f $OUTFILENAME
mkdir $PATH_TO_OUTPUT_FOLDER
chgrp $GROUP $PATH_TO_OUTPUT_FOLDER
chmod g+s $PATH_TO_OUTPUT_FOLDER
doxygen Doxyfile
moxygen -o $OUTFILENAME $PATH_TO_OUTPUT_FOLDER
rm -R -f $PATH_TO_OUTPUT_FOLDER