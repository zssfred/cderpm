%ifarch x86_64
%define _archflag -m64
%endif

%ifarch %{ix86}
%define _archflag -m32
%endif

Name:                cde
Version:             2.2.4
Release:             4%{?dist}
Summary:             Common Desktop Environment

Group:               User Interface/Desktops
License:             LGPLv2+
URL:                 http://cdesktopenv.sourceforge.net/
# Source is in git.  Actual releases can be found here:
#     http://sourceforge.net/projects/cdesktopenv/files/
# Source repo can be cloned this way:
#     git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
# The checkout-cde.sh generates the source archives used by this spec file.
Source0:             %{name}-src-%{version}.tar.gz
Source1:             checkout-cde.sh
Source2:             dt.conf
Source3:             dt.sh
Source4:             dt.csh
Source5:             dtspc
Source6:             cde.desktop

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)

# Runtime requirements
Requires:            xinetd

# These BuildRequires come from the main RHEL repo.
BuildRequires:       xorg-x11-proto-devel
BuildRequires:       openmotif-devel
BuildRequires:       chrpath
BuildRequires:       ksh

# These BuildRequires come from the RHEL Optional repo.
BuildRequires:       xorg-x11-xbitmaps

%description
CDE is the Common Desktop Environment from The Open Group.

%prep
%setup -q

sed -i -e '1i #define FILE_MAP_OPTIMIZE' programs/dtfile/Utils.c

echo "#define KornShell /bin/ksh" >> config/cf/site.def
echo "#define CppCmd cpp" >> config/cf/site.def
echo "#define YaccCmd bison -y" >> config/cf/site.def
echo "#define HasTIRPCLib YES" >> config/cf/site.def
echo "#define HasZlib YES" >> config/cf/site.def
echo "#define DtLocalesToBuild" >> config/cf/site.def

%build
export LANG=C
export LC_ALL=C
export IMAKECPP=cpp
%{__make} World BOOTSTRAPCFLAGS="%{optflags} %{_archflag}"
sed -i -e 's:mkProd -D :&%{buildroot}:' admin/IntegTools/dbTools/installCDE

%install
srcdir="$(pwd)"
pushd admin/IntegTools/dbTools
export LANG=C
export LC_ALL=C
./installCDE -s "$srcdir" -pseudo -pI "%{buildroot}%{_prefix}/dt" -pV "%{buildroot}%{_localstatedir}/dt" -pC "%{buildroot}%{_sysconfdir}/dt"
popd

# Remove the rpath setting from ELF objects.
# XXX: This is a heavy hammer which should really be fixed by not using -rpath
# in the build in the first place.  Baby steps.
find %{buildroot}%{_prefix}/dt/bin -type f | \
    grep -v -E "(lndir|mergelib|xon|makeg|xmkmf|mkdirhier|dtinfogen|dthelpgen.ds|dtlp|dtappintegrate|dtdocbook|Xsession|dtfile_error|dterror.ds|dthelptag|dthelpprint.sh)" | \
    xargs chrpath -d
find %{buildroot}%{_prefix}/dt/lib -type f -name "lib*.so*" | xargs chrpath -d
chrpath -d %{buildroot}%{_prefix}/dt/dthelp/dtdocbook/instant
chrpath -d %{buildroot}%{_prefix}/dt/dthelp/dtdocbook/xlate_locale
chrpath -d %{buildroot}%{_prefix}/dt/lib/dtudcfonted/*
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/dbdrv
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/dtinfogen_worker
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/dtinfo_start
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/MixedGen
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/NCFGen
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/NodeParser
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/nsgmls
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/StyleUpdate
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/valBase
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/validator

# Specific permissions required on some things
chmod 2555 %{buildroot}%{_prefix}/dt/bin/dtmail

# Configuration files
install -D -m 0644 %SOURCE2 %{buildroot}%{_sysconfdir}/ld.so.conf.d/dt.conf
install -D -m 0755 %SOURCE3 %{buildroot}%{_sysconfdir}/profile.d/dt.sh
install -D -m 0755 %SOURCE4 %{buildroot}%{_sysconfdir}/profile.d/dt.csh
install -D -m 0600 contrib/xinetd/ttdbserver %{buildroot}%{_sysconfdir}/xinetd.d/ttdbserver
install -D -m 0600 contrib/xinetd/cmsd %{buildroot}%{_sysconfdir}/xinetd.d/cmsd
install -D -m 0600 %SOURCE5 %{buildroot}%{_sysconfdir}/xinetd.d/dtspc
install -D -m 0644 %SOURCE6 %{buildroot}%{_datadir}/xsessions/cde.desktop

%clean
rm -rf %{buildroot}

%post
PATH=/bin:/usr/bin

# Add 'dtspc' line to /etc/services
grep -qE "^dtspc" /etc/services >/dev/null 2>&1
if [ $? -eq 1 ]; then
    echo -e "dtspc\t6112/tcp\t#subprocess control" >> /etc/services
fi

# Make sure rpcbind runs with -i
if [ -f /etc/sysconfig/rpcbind ]; then
    . /etc/sysconfig/rpcbind
    echo "$RPCBIND_ARGS" | grep -q "\-i" >/dev/null 2>&1
    [ $? -eq 1 ] && echo "RPCBIND_ARGS=\"-i\"" >> /etc/sysconfig/rpcbind
else
    echo "RPCBIND_ARGS=\"-i\"" >> /etc/sysconfig/rpcbind
fi

%postun
PATH=/bin:/usr/bin
TMPDIR="$(mktemp -d)"

# Remove 'dtspc' line from /etc/services
grep -qE "^dtspc" /etc/services >/dev/null 2>&1
if [ $? -eq 0 ]; then
    grep -vE "^dtspc\s+6112" /etc/services > $TMPDIR/services
    mv $TMPDIR/services /etc/services
fi

rm -rf $TMPDIR

%files
%defattr(-,root,root,-)
%doc CONTRIBUTORS COPYING README copyright HISTORY
%{_prefix}/dt
%{_localstatedir}/dt
%config %{_sysconfdir}/ld.so.conf.d/dt.conf
%config %{_sysconfdir}/profile.d/dt.sh
%config %{_sysconfdir}/profile.d/dt.csh
%config %{_sysconfdir}/dt
%config %{_sysconfdir}/xinetd.d/cmsd
%config %{_sysconfdir}/xinetd.d/dtspc
%config %{_sysconfdir}/xinetd.d/ttdbserver
%{_datadir}/xsessions

%changelog
* Tue May 16 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-4
- Complete packaging using the installCDE script
- Initial set of configuration files and control scripts
- Runtime requirement on xinetd
- xsession file to support launching CDE from gdm login screen

* Thu May 11 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-3
- Shift to using installCDE to install the build
- Add ksh as a BuildRequires

* Wed May 10 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-2
- Sort out the file list and get things moved to the correct place

* Thu Apr 27 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-1
- First update of this package to CDE 2.2.4

* Thu Aug 23 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-3.20120816gitce4004f
- Unpack dt.tar in the buildroot, create required directories
- Disable the use of -Wl,-rpath,PATH during the build

* Fri Aug 17 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-2.20120816gitce4004f
- Use /bin/sh in installation scripts, not /bin/ksh
- Use -m64 and -m32 in BOOTSTRAPCFLAGS to get correct linking

* Thu Aug 16 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-1.20120816gitce4004f
- Initial packaging attempt
