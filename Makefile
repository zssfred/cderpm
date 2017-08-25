# Makefile to drive local builds of the cde RPM.
# Author:  David Cantrell <david.l.cantrell@gmail.com>

CWD := $(shell pwd)
RPMBUILD = rpmbuild --define='_topdir $(CWD)' \
                    --define='_sourcedir $(CWD)' \
                    --define='_specdir $(CWD)'
URL = https://www.burdell.org/cde/

all: fetch
	$(RPMBUILD) -ba cde.spec

fetch:
	@while read checksum filename ; do \
		if [ -f ${CWD}/$${filename} ]; then \
			computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
			if [ "$${computed}" = "$${checksum}" ]; then \
				echo "Already have $${filename} and it checks out." ; \
			else \
				curl -O $(URL)/$${filename} ; \
				computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
				if [ ! "$${computed}" = "$${checksum}" ]; then \
					echo "*** INVALID CHECKSUM $${filename}" ; \
					exit 1 ; \
				fi ; \
			fi ; \
		else \
			curl -O $(URL)/$${filename} ; \
			computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
			if [ ! "$${computed}" = "$${checksum}" ]; then \
				echo "*** INVALID CHECKSUM $${filename}" ; \
				exit 1 ; \
			fi ; \
		fi ; \
	done < $(CWD)/sources

prep:
	$(RPMBUILD) -bp cde.spec

compile:
	$(RPMBUILD) -bb cde.spec

install:
	$(RPMBUILD) -bi cde.spec

source:
	$(RPMBUILD) -bs cde.spec

clean:
	-rm -rf BUILD BUILDROOT RPMS SRPMS
	while read checksum filename ; do \
		[ -f "$$filename" ] && rm -f "$$filename" ; \
	done < $(CWD)/sources
