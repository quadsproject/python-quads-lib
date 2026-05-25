#### NOTE: if building locally you may need to do the following:
####
#### yum install rpmdevtools -y
#### spectool -g -R rpm/quads-lib.spec
####
#### At this point you can use rpmbuild -ba quads-lib.spec
#### this is because our Source0 is a remote Github location
####
#### Our upstream repository is located here:
#### https://copr.fedorainfracloud.org/coprs/quadsdev/QUADS

%define name quads-lib
%define reponame python-quads-lib
%define branch development
%define version 0.1.13
%define build_timestamp %{lua: print(os.date("%Y%m%d"))}

Summary: Python client library for interacting with the QUADS API
Name: %{name}
Version: %{version}
Release: %{build_timestamp}
Source0: https://github.com/quadsproject/%{reponame}/archive/%{branch}.tar.gz#/%{name}-%{version}-%{release}.tar.gz
License: LGPL-3.0-only
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArch: noarch
Vendor: QUADS Project
Packager: QUADS Project
BuildRequires: python3-devel
BuildRequires: python3-setuptools
Requires: python3 >= 3.9
Requires: python3-requests >= 2.31.0

AutoReq: no

Url: https://quads.dev

%description

Python client library for interacting with the QUADS (Automated Scheduling
and Delivery System) API. Provides QuadsApi class for REST API communication
with QUADS servers.

%prep
%autosetup -n %{reponame}-%{branch}

%build
%py3_build

%install
%py3_install

%clean
rm -rf %{buildroot}

%files
%doc README.rst CHANGELOG.rst
%license LICENSE
%{python3_sitelib}/quads_lib/
%{python3_sitelib}/quads_lib-*.egg-info/

%changelog

* Wed Apr 30 2026 Will Foster <wfoster@redhat.com>
- 0.1.9 release
- Initial RPM package for quads-lib
- Provides QuadsApi client for QUADS API v3
- Required dependency for quads-client TUI
