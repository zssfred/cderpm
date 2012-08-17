%define checkout 20120816gitce4004f

Name:                cde
Version:             2.2.0
Release:             1.%{checkout}%{?dist}
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

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)
BuildRequires:       imake
BuildRequires:       xorg-x11-xbitmaps
BuildRequires:       xorg-x11-proto-devel
BuildRequires:       openmotif-devel

%description
CDE is the Common Desktop Environment from The Open Group.

%prep
%setup -q -n cdesktopenv-code/cde

# Fix the awk script used to create the installation tarball so it works with gawk.
%patch0 -p1

# 64-bit platforms have libraries in /usr/lib64
PLATFORM="$(/bin/arch)"
if [ "${PLATFORM}" = "x86_64" -o "${PLATFORM}" = "ppc64" ]; then
    echo "#define UsrLibDir /usr/lib64" > config/cf/host.def
fi

# The build system expects to find X headers in the local tree.
mkdir -p imports/x11/include
cd imports/x11/include
ln -s /usr/include/X11 .

%build
# XXX: this should be make World, but will figure out docs later
%{__make} World.dev

%install
rm -rf %{buildroot}

CDE=$(pwd)
cd ${CDE}/admin/IntegTools/dbTools
./installCDE -s ${CDE} -t ${CDE}/tars -nocompress
#cd ${CDE}/admin/IntegTools/post_install/linux
#./configRun -e

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CONTRIBUTORS COPYING README copyright

%changelog
* Thu Aug 16 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-1.20120816gitce4004f
- Initial packaging attempt
