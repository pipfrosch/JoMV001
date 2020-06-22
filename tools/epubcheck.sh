#!/bin/bash

EPUBCHECK="${HOME}/java/epubcheck-4.2.3"

OPERATION="java -jar ${EPUBCHECK}/epubcheck.jar"
OPTIONS="$@"

exec ${OPERATION} ${OPTIONS}
