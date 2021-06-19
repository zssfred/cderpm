#!/bin/sh

errorExit() {
	echo "*** $*" 1>&2
	exit 1
}

VER="$(grep '^%define *_cdeversion' cde.spec | awk '{ print $3; }')"
GITHASH="$(grep '^%define *_githash' cde.spec | awk '{ print $3; }')"
CWD=$(pwd)
if cd cdesktopenv-code/cde 2>/dev/null; then
	git reset --hard HEAD || errorExit "Error git reset"
	git fetch || errorExit "Error git fetch"
	git checkout master || errorExit "Error git checkout"
else
	git clone --recursive git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code || errorExit "Error git clone"
	cd cdesktopenv-code/cde || errorExit "Error chdir"
fi
if [ -n "${GITHASH}" ]; then
	git checkout ${GITHASH} || errorExit "Error git checkout ${GITHASH}"
else
	GITHASH="$(git log --pretty=format:'%h' -n 1)"
fi
cd ${CWD}
OUTPUT="cde-${VER}git${GITHASH}.tar.gz"
tar --transform="s/cdesktopenv-code\/cde\//cde-${VER}git${GITHASH}\//" -czvf ${OUTPUT} cdesktopenv-code/cde || errorExit "Error tar"
echo
echo "New source archived to ${OUTPUT}"
