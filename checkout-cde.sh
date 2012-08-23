#!/bin/sh

CWD=$(pwd)
rm -rf cdesktopenv-code
git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
cd cdesktopenv-code/cde
GITHASH="$(git log --pretty=format:'%h' -n 1)"
DATESTAMP="$(date +%Y%m%d)"
VER="$(grep RELEASE Makefile | grep "=" | awk '{ print $4; }')"
cd ${CWD}
find cdesktopenv-code -type d -name .git | xargs rm -rf
OUTPUT="cde-${VER}-${DATESTAMP}git${GITHASH}.tar.xz"
tar -cvf - cdesktopenv-code | xz -9c > ${OUTPUT}
rm -rf cdesktopenv-code
sha1sum ${OUTPUT} > ${CWD}/sources
echo
echo "New source archived to ${OUTPUT}"
