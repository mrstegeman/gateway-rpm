Name: webthings-gateway
Version: 0.12.0
Release: 1%{?dist}
Summary: WebThings Gateway by Mozilla

License: MPL-2.0
URL: https://iot.mozilla.org/gateway/

BuildRequires: autoconf automake nodejs npm git python python3 python3-pip python3-setuptools libffi-devel python3-devel gcc gcc-c++ systemd make zlib-devel libpng-devel
Requires: {{nodejs}} {{python3}} python3-pip libffi python2-six
Requires(pre): shadow-utils

Source0: %{name}_0.12.0.orig.tar.gz
Source1: %{name}.service

Patch0: fix-config.patch
Patch1: add-launcher.patch
Patch2: add-env.patch

%description
Web of Things gateway, created by Mozilla, which can bridge existing
Internet of Things (IoT) devices to the web.

%define debug_package %{nil}

%prep
%autosetup -n %{name} -p1

%build
NPM_CACHE=$(mktemp -dq)
CPPFLAGS="-DPNG_ARM_NEON_OPT=0" npm --cache "${NPM_CACHE}" ci
./node_modules/.bin/webpack
npm --cache "${NPM_CACHE}" prune --production
rm -rf "${NPM_CACHE}"
# clean up node modules to prevent broken and unnecessary dependencies
rm -rf ./node_modules/performance-now/test/
chmod a+x %{name}
mkdir python
python3 -m pip install \
  --install-option="--prefix=" \
  --no-binary=:all: \
  -t ./python \
  ./gateway-addon-python

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc/profile.d
mkdir -p %{buildroot}/opt/%{name}
mkdir -p %{buildroot}/opt/%{name}/config
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
cp -r build %{buildroot}/opt/%{name}
cp config/default.js %{buildroot}/opt/%{name}/config
cp -r node_modules %{buildroot}/opt/%{name}
cp package-lock.json %{buildroot}/opt/%{name}
cp package.json %{buildroot}/opt/%{name}
cp -r python %{buildroot}/opt/%{name}
cp -r src %{buildroot}/opt/%{name}
cp -r static %{buildroot}/opt/%{name}
cp %{name} %{buildroot}%{_bindir}
cp %{SOURCE1} %{buildroot}%{_unitdir}
cp %{name}.sh %{buildroot}/etc/profile.d

%pre
getent group webthings >/dev/null || groupadd -f -r webthings
if ! getent passwd webthings > /dev/null ; then
  useradd -r -l -g webthings -d /var/run/%{name} -s /sbin/nologin -c "Mozilla WebThings Gateway" webthings
fi

%files
%license LICENSE
%dir /opt/%{name}/
/opt/%{name}/*
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
/etc/profile.d/%{name}.sh

%changelog
* Tue Feb 18 2020 Michael Stegeman <mstegeman@mozilla.com>
- Update to 0.12.
* Mon Dec 16 2019 Michael Stegeman <mstegeman@mozilla.com>
- First webthings-gateway package.
