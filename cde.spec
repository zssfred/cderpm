%ifarch x86_64
%define _archflag -m64
%endif

%ifarch %{ix86}
%define _archflag -m32
%endif

# Set a macro to use for distribution variances
%if 0%{?fedora}
%define _distribution fedora
%endif

%if 0%{?rhel}
%define _distribution rhel
%endif

%if 0%{?epel}
%define _distribution epel
%endif

%if "%{?distsuffix:%{distsuffix}}%{!?distsuffix:0}" == "pclos"
%define _distribution pclos
%endif

%define _githash f294ef4a
%if "%{_githash}" == ""
%define _git
%else
%define _git git%{_githash}
%endif
%define _cdeversion 2.3.2

Name:                cde
Version:             %{_cdeversion}%{_git}
%if "%{_distribution}" == "pclos"
Release:             %mkrel 3
%else
Release:             3%{?dist}
%endif
Summary:             Common Desktop Environment

Group:               User Interface/Desktops
License:             LGPLv2+
URL:                 http://cdesktopenv.sourceforge.net/
# Source is in git.  Actual releases can be found here:
#     http://sourceforge.net/projects/cdesktopenv/files/
# Source repo can be cloned this way:
#     git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
# The checkout-cde.sh generates the source archives used by this spec file.
Source0:             %{name}-%{version}.tar.gz
Source1:             checkout-cde.sh
Source2:             dt.conf
Source3:             dt.sh
Source4:             dt.csh
Source5:             dtspc
Source6:             cde.desktop
Source7:             fonts.alias
Source8:             fonts.dir
Source9:             dtlogin.service

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)

Requires:            xinetd
Requires:            ksh
%if "%{_distribution}" == "fedora"
Requires:            xstdcmap
Requires:            ( xorg-x11-utils or xdpyinfo or xwininfo or xvinfo or xprop or xlsfonts or xlsclients or xlsatoms or xev )
%else
Requires:            xorg-x11-server-utils
Requires:            xorg-x11-utils
%endif
%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
Requires:            xorg-x11-xinit
Requires:            xorg-x11-server-Xorg
Requires:            xorg-x11-fonts-ISO8859-1-100dpi
Requires:            xorg-x11-fonts-ISO8859-2-100dpi
Requires:            xorg-x11-fonts-ISO8859-9-100dpi
Requires:            xorg-x11-fonts-ISO8859-14-100dpi
Requires:            xorg-x11-fonts-ISO8859-15-100dpi
Requires:            xorg-x11-fonts-100dpi
Requires:            xorg-x11-fonts-misc
%endif
%if "%{_distribution}" == "pclos"
Requires:            xinit
Requires:            xset
Requires:            bdftopcf
Requires:            x11-server-xorg
Requires:            x11-font-misc
# for dtterm terminfo definition
Requires:            ncurses-extraterms
%endif
Requires:            ncompress
Requires:            rpcbind

%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
BuildRequires:       xorg-x11-proto-devel
%if 0%{?rhel} >= 7
%{?systemd_requires}
BuildRequires:       motif-devel
BuildRequires:       systemd
%endif
%if 0%{?rhel} <= 6
BuildRequires:       openmotif-devel
%endif
BuildRequires:       patchelf
%endif
%if "%{_distribution}" == "pclos"
BuildRequires:       x11-proto-devel
BuildRequires:       lib64openmotif4
BuildRequires:       lib64openmotif4-devel
%endif
BuildRequires:       bdftopcf
BuildRequires:       file
BuildRequires:       ksh
BuildRequires:       m4
BuildRequires:       ncompress
BuildRequires:       bison
BuildRequires:       byacc
BuildRequires:       gcc-c++
%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
BuildRequires:       libXp-devel
BuildRequires:       libXt-devel
BuildRequires:       libXmu-devel
BuildRequires:       libXft-devel
BuildRequires:       libXinerama-devel
BuildRequires:       libXpm-devel
BuildRequires:       libXaw-devel
BuildRequires:       libX11-devel
BuildRequires:       libXScrnSaver-devel
BuildRequires:       libjpeg-turbo-devel
BuildRequires:       freetype-devel
BuildRequires:       openssl-devel
BuildRequires:       tcl-devel
BuildRequires:       xorg-x11-xbitmaps
BuildRequires:       libXdmcp-devel
BuildRequires:       libtirpc-devel
%endif
%if "%{_distribution}" == "pclos"
BuildRequires:       lib64xp-devel
BuildRequires:       lib64xt-devel
BuildRequires:       lib64xmu-devel
BuildRequires:       lib64xft-devel
BuildRequires:       lib64xinerama-devel
BuildRequires:       lib64xpm-devel
BuildRequires:       lib64xaw-devel
BuildRequires:       lib64x11-devel
BuildRequires:       lib64xscrnsaver-devel
BuildRequires:       lib64jpeg-devel
BuildRequires:       lib64freetype6-devel
BuildRequires:       lib64openssl-devel
BuildRequires:       lib64tcl-devel
BuildRequires:       x11-data-bitmaps
BuildRequires:       lib64xdmcp-devel
BuildRequires:       lib64tirpc-devel
%endif
BuildRequires:       ncurses

# /usr/bin/rpcgen exists in glibc-common in older releases, otherwise we
# have to explicitly pull in the rpcgen package
%if 0%{?rhel} > 7 || 0%{?fedora} > 27
BuildRequires:       rpcgen
%endif

%description
CDE is the Common Desktop Environment from The Open Group.

%prep
%setup -q

sed -i -e '1i #define FILE_MAP_OPTIMIZE' programs/dtfile/Utils.c

echo "#define KornShell /bin/ksh" >> config/cf/site.def
echo "#define CppCmd cpp" >> config/cf/site.def
echo "#define YaccCmd bison -y" >> config/cf/site.def
echo "#define HasZlib YES" >> config/cf/site.def
echo "#define DtLocalesToBuild" >> config/cf/site.def
echo "#define RegisterRPC" >> config/cf/site.def

%build
export LANG=C
export LC_ALL=C
export IMAKECPP=cpp
%{__make} World BOOTSTRAPCFLAGS="%{optflags} %{_archflag}"
sed -i -e 's:mkProd -D :&%{buildroot}:' admin/IntegTools/dbTools/installCDE

%install
srcdir="$(pwd)"
export LANG=C
export LC_ALL=C
./admin/IntegTools/dbTools/installCDE -s "$srcdir" -pseudo -pI "%{buildroot}%{_prefix}/dt" -pV "%{buildroot}%{_localstatedir}/dt" -pC "%{buildroot}%{_sysconfdir}/dt" -destdir "%{buildroot}"

%if "%{_distribution}" == "fedora" || "%{_distributon}" == "rhel" || "%{_distribution}" == "epel"
# Remove the rpath setting from ELF objects.
# XXX: This is a heavy hammer which should really be fixed by not using -rpath
# in the build in the first place.  Baby steps.
find %{buildroot}%{_prefix}/dt -type f | while read infile ; do
    typ="$(file -b --mime-type $infile)"
    if [ "$typ" = "application/x-executable" ] || [ "$typ" = "application/x-sharedlib" ]; then
        rpath="$(patchelf --print-rpath $infile >/dev/null 2>&1)"
        [ -z "$rpath" ] || patchelf --remove-rpath $infile
    fi
done
%endif

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
install -D -m 0644 %SOURCE7 %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.alias
install -D -m 0644 %SOURCE8 %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.dir

%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
# Install systemd unit file on applicable systems
%if 0%{?rhel} >= 7
install -D -m 0644 %SOURCE9 %{buildroot}%{_unitdir}/dtlogin.service
%endif

# Create terminfo file for dtterm
pushd programs/dtterm
./terminfoCreate < terminfoChecklist > dtterm.terminfo
tic dtterm.terminfo
install -D -m 0644 dtterm %{buildroot}%{_datadir}/terminfo/d/dtterm
popd
%endif

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

# Tell users what needs to happen once they have installed
echo
echo
echo "***************************************"
echo "* Important postinstall steps for CDE *"
echo "***************************************"
echo
echo "1) Enable and start rpcbind:"
if [ -x /usr/bin/systemctl ]; then
    echo "   systemctl enable rpcbind.service"
    echo "   systemctl start rpcbind.service"
else
    echo "   chkconfig rpcbind on"
    echo "   service rpcbind start"
fi
echo
echo "2) Enable and start xinetd:"
if [ -x /usr/bin/systemctl ]; then
    echo "   systemctl enable xinetd.service"
    echo "   systemctl start xinetd.service"
else
    echo "   chkconfig xinetd on"
    echo "   service xinetd start"
fi
echo
echo

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
%attr(1777, root, root) %{_localstatedir}/dt
%config %{_sysconfdir}/ld.so.conf.d/dt.conf
%config %{_sysconfdir}/profile.d/dt.sh
%config %{_sysconfdir}/profile.d/dt.csh
%config %{_sysconfdir}/dt
%config %{_sysconfdir}/xinetd.d/cmsd
%config %{_sysconfdir}/xinetd.d/dtspc
%config %{_sysconfdir}/xinetd.d/ttdbserver
%config %{_sysconfdir}/dt/config/xfonts/C/fonts.alias
%config %{_sysconfdir}/dt/config/xfonts/C/fonts.dir
%{_datadir}/xsessions
%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
%{_datadir}/terminfo
%endif
%if 0%{?rhel} >= 7
%{_unitdir}/dtlogin.service
%endif

%changelog
* Wed Aug 22 2018 David Cantrell <dcantrell@redhat.com> - 2.3.0-2
- Conditionalize the BR on rpcgen for only recent systems

* Thu Aug 16 2018 David Cantrell <dcantrell@redhat.com> - 2.3.0-1
- Upgrade to CDE 2.3.0
- Use patchelf rather than chrpath in %%install
- Build requires rpcgen
- Replace deprecated/removed ustat(2) calls with statfs(2)

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-9
- Create /usr/share/terminfo/d/dtterm entry

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-8
- In the postinstall script, check for systemctl in /usr/bin
- Build with libtirpc-devel since that does not work correctly for CDE
  on 64-bit platforms right now
- Add systemd unit file for dtlogin for EL-7 and Fedora

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-7
- Small fix for libast/ast.h in the dtksh source
- Require xorg-x11-fonts-misc to map to default CDE fonts

* Thu Aug 24 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-6
- Add fonts.alias and fonts.dir files for /etc/dt/config/xfonts/C
- Patch /etc/xinetd.d/ttdbserver file to enable by default
- Ensure /var/dt is installed with 1777 permissions
- In the RPM postinstall script, tell the user to make sure rpcbind
  and xinetd services are enabled

* Tue May 30 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-5
- Updated spec file for CentOS 7.x building

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
