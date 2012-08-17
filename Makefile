CWD := $(shell pwd)
RPMBUILD = rpmbuild --define='_topdir $(CWD)' \
                    --define='_sourcedir $(CWD)' \
                    --define='_specdir $(CWD)'

all:
	$(RPMBUILD) -ba cde.spec

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
