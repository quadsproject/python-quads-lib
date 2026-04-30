Name:           quads-lib
Version:        0.1.9
Release:        1%{?dist}
Summary:        Python client library for interacting with the QUADS API

License:        LGPL-3.0-only
URL:            https://github.com/quadsproject/python-quads-lib
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3-requests >= 2.31.0

%description
Python client library for interacting with the QUADS (Automated Scheduling
and Delivery System) API. Provides QuadsApi class for REST API communication
with QUADS servers.

%prep
%autosetup -n quads_lib-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.rst CHANGELOG.rst
%{python3_sitelib}/quads_lib/
%{python3_sitelib}/quads_lib-*.egg-info/

%changelog
* Wed Apr 30 2026 Will Foster <wfoster@redhat.com> - 0.1.9-1
- Initial RPM package for quads-lib
- Provides QuadsApi client for QUADS API v3
- Required dependency for quads-client TUI
