%ifarch x86_64
%define _archflag -m64
%endif

%ifarch %{ix86}
%define _archflag -m32
%endif

Name:                cde
Version:             2.2.4
Release:             3%{?dist}
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

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)

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

%build
%{__make} World BOOTSTRAPCFLAGS="%{optflags} %{_archflag}"

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

## Move things to the right place
#mv %{buildroot}/bin/* %{buildroot}%{_prefix}/dt/bin
#rmdir %{buildroot}/bin

#mkdir -p %{buildroot}%{_datadir}/X11/app-defaults
#mv %{buildroot}/app-defaults/C/* %{buildroot}%{_datadir}/X11/app-defaults
#rm -rf %{buildroot}/app-defaults

#mkdir -p %{buildroot}%{_includedir}/X11
#mv %{buildroot}/C %{buildroot}%{_includedir}/X11/bitmaps

# Remove the rpath setting from ELF objects.
# XXX: This is a heavy hammer which should really be fixed by not using -rpath
# in the build in the first place.  Baby steps.
chmod 0755 %{buildroot}%{_prefix}/dt/bin/nsgmls
find %{buildroot}%{_prefix}/dt/bin -type f | \
    grep -v -E "(lndir|mergelib|xon|makeg|xmkmf|mkdirhier)" | \
    xargs chrpath -d
find %{buildroot}%{_prefix}/dt/lib -type f -name "lib*.so*" | xargs chrpath -d

# Create other required directories.
mkdir -p %{buildroot}%{_sysconfdir}/dt
mkdir -p %{buildroot}%{_localstatedir}/dt

# These are provided by the Motif package
#pushd %{buildroot}%{_includedir}/X11/bitmaps
#rm -f xm_hour16 xm_hour16m xm_hour32 xm_hour32m xm_noenter16 xm_noenter16m xm_noenter32 xm_noenter32m
#popd

# XXX: Does this need to exist somewhere?
#rm -rf %{buildroot}/infolib
#rm -rf %{buildroot}/ja

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CONTRIBUTORS COPYING README copyright HISTORY
%{_prefix}/dt
%{_localstatedir}/dt
%config %{_sysconfdir}/dt

%changelog
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
