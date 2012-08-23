%define checkout 20120816gitce4004f

%ifarch x86_64
%define _archflag -m64
%endif

%ifarch %{ix86}
%define _archflag -m32
%endif

Name:                cde
Version:             2.2.0
Release:             3.%{checkout}%{?dist}
Summary:             Common Desktop Environment

Group:               User Interface/Desktops
License:             LGPLv2+
URL:                 http://cdesktopenv.sourceforge.net/
# Source is in git.  Actual releases can be found here:
#     http://sourceforge.net/projects/cdesktopenv/files/
# Source repo can be cloned this way:
#     git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
# The checkout-cde.sh generates the source archives used by this spec file.
Source0:             %{name}-%{version}-%{checkout}.tar.xz
Source1:             checkout-cde.sh

Patch0:              cde-fix-udbParseLib.awk.patch
Patch1:              cde-use-sh-over-ksh.patch

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)
BuildRequires:       xorg-x11-xbitmaps
BuildRequires:       xorg-x11-proto-devel
BuildRequires:       openmotif-devel
BuildRequires:       chrpath

%description
CDE is the Common Desktop Environment from The Open Group.

%prep
%setup -q -n cdesktopenv-code/cde

# Fix the awk script used to create the installation tarball so it works with gawk.
%patch0 -p1

# Use #!/bin/sh instead of #!/bin/ksh in the installation tools.
%patch1 -p1

# The build system expects to find X headers in the local tree.
mkdir -p imports/x11/include
cd imports/x11/include
ln -s /usr/include/X11 .

%build
[ -d %{buildroot} ] && chmod -R u+w %{buildroot}
rm -rf %{buildroot}
# XXX: this should be make World, but will figure out docs later
%{__make} World.dev BOOTSTRAPCFLAGS="%{optflags} %{_archflag}"

%install
[ -d %{buildroot} ] && chmod -R u+w %{buildroot}
rm -rf %{buildroot}
mkdir -p %{buildroot}

# The installation creates a dt.tar file that we extract to buildroot.
CDE=$(pwd)
cd ${CDE}/admin/IntegTools/dbTools
./installCDE -s ${CDE} -t ${CDE}/tars -nocompress
DTTAR="$(find ${CDE}/tars -name dt.tar)"
tar -C %{buildroot} -xpsvf ${DTTAR}
chmod -R u+w %{buildroot}

# Remove the rpath setting from ELF objects.
# XXX: This is a heavy hammer which should really be fixed by not using -rpath
# in the build in the first place.  Baby steps.
find %{buildroot}%{_prefix}/dt/bin -type f | \
    grep -v -E "(Xsession|dtappintegrate|dtdocbook|dterror\.ds|dtfile_error|dthelpgen\.ds|dthelpprint\.sh|dthelptag|dtinfogen|dtlp|dtsession_res|ttrmdir)" | \
    xargs chrpath -d
find %{buildroot}%{_prefix}/dt/lib -type f -name "lib*.so*" | xargs chrpath -d
find %{buildroot}%{_prefix}/dt/lib/dtudcfonted -type f -name "dt*" | xargs chrpath -d
chrpath -d %{buildroot}%{_prefix}/dt/dthelp/dtdocbook/instant
chrpath -d %{buildroot}%{_prefix}/dt/dthelp/dtdocbook/xlate_locale
chrpath -d %{buildroot}%{_prefix}/dt/infolib/etc/nsgmls

# Create other required directories.
mkdir -p %{buildroot}%{_sysconfdir}/dt
mkdir -p %{buildroot}%{_localstatedir}/dt

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CONTRIBUTORS COPYING README copyright
%{_prefix}/dt
%{_localstatedir}/dt
%config %{_sysconfdir}/dt

%changelog
* Thu Aug 23 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-3.20120816gitce4004f
- Unpack dt.tar in the buildroot, create required directories
- Disable the use of -Wl,-rpath,PATH during the build

* Fri Aug 17 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-2.20120816gitce4004f
- Use /bin/sh in installation scripts, not /bin/ksh
- Use -m64 and -m32 in BOOTSTRAPCFLAGS to get correct linking

* Thu Aug 16 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-1.20120816gitce4004f
- Initial packaging attempt
