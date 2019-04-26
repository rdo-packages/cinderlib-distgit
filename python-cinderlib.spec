# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global pypi_name cinderlib
%global common_summary Python library for direct usage of Cinder drivers without the services
%global common_desc \
The Cinder Library, also known as cinderlib, is a Python library that leverages \
the Cinder project to provide an object oriented abstraction around Cinder's \
storage drivers to allow their usage directly without running any of the Cinder \
services or surrounding services, such as KeyStone, MySQL or RabbitMQ. \
\
The library is intended for developers who only need the basic CRUD \
functionality of the drivers and don't care for all the additional features \
Cinder provides such as quotas, replication, multi-tenancy, migrations, \
retyping, scheduling, backups, authorization, authentication, REST API, etc.

Name:           python-%{pypi_name}
Epoch:          1
Version:        XXX
Release:        XXX
Summary:        %{common_summary}

License:        ASL 2.0
URL:            https://docs.openstack.org/cinderlib/latest/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch
%description
%{common_desc}

%package -n python%{pyver}-%{pypi_name}
Summary:        %{common_summary}
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}
%if %{pyver} == 3
Obsoletes: python2-%{pypi_name} < %{version}-%{release}
%endif

Requires:       python%{pyver}-pbr
Requires:       openstack-cinder >= 12.0.0
Requires:       sudo

BuildRequires:  git
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-pbr
BuildRequires:  openstack-cinder
# Required for unit tests
BuildRequires:    python%{pyver}-ddt
BuildRequires:    python%{pyver}-os-testr
BuildRequires:    python%{pyver}-oslotest

%description -n python%{pyver}-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        Documentation for cinderlib

BuildRequires:  graphviz
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-openstackdocstheme
BuildRequires:  python%{pyver}-sphinxcontrib-apidoc

%description doc
This package contains the documentation files for %{pypi_name}.

%{common_desc}
%endif

%package -n python%{pyver}-%{pypi_name}-tests-unit
Summary:        Cinderlib unit tests

Requires:    python%{pyver}-%{pypi_name}
Requires:    python%{pyver}-ddt
Requires:    python%{pyver}-os-testr
Requires:    python%{pyver}-oslotest

%description -n python%{pyver}-%{pypi_name}-tests-unit
This package contains the unit tests for %{pypi_name}.

%{common_desc}

%package -n python%{pyver}-%{pypi_name}-tests-functional
Summary:        Cinderlib unit tests

Requires:    python%{pyver}-%{pypi_name}
Requires:    python%{pyver}-ddt
Requires:    python%{pyver}-os-testr
Requires:    python%{pyver}-oslotest

%description -n python%{pyver}-%{pypi_name}-tests-functional
This package contains the functional tests for %{pypi_name}.

%{common_desc}

%package -n python%{pyver}-%{pypi_name}-tests
Summary:        All cinderlib tests

Requires: python%{pyver}-%{pypi_name}-tests-unit
Requires: python%{pyver}-%{pypi_name}-tests-functional

%description -n python%{pyver}-%{pypi_name}-tests
Virtual package for all %{pypi_name} tests.

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info
# Remove the requirements file so that pbr hooks don't add its requirements
rm -rf {test-,}requirements.txt

# Remove the devstack plugin, gate playbooks, and CI tools
rm -rf devstack playbooks tools

%build
%{pyver_build}

%if 0%{?with_doc}
# generate html docs
sphinx-build-%{pyver} -b html doc/source doc/build/html
# remove the sphinx-build leftovers
rm -rf doc/build/html/{.doctrees,.buildinfo,.placeholder,_sources}
%endif

%check
%{pyver_bin} -m unittest2 discover -v -s cinderlib/tests/unit

%install
%{pyver_install}

%files -n python%{pyver}-%{pypi_name}
%license LICENSE
%{pyver_sitelib}/cinderlib*
%exclude %{pyver_sitelib}/%{pypi_name}/tests

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html
%endif

%files -n python%{pyver}-%{pypi_name}-tests-unit
%license LICENSE
%{pyver_sitelib}/%{pypi_name}/tests/unit/*

%files -n python%{pyver}-%{pypi_name}-tests-functional
%license LICENSE
%{pyver_sitelib}/%{pypi_name}/tests/functional/*

%files -n python%{pyver}-%{pypi_name}-tests
%exclude /*

%changelog
