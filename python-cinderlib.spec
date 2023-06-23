%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order

%global with_doc 1

%global pypi_name cinderlib
%global __brp_mangle_shebangs_exclude_from ^%{python3_sitelib}/cinderlib/bin/venv-privsep-helper$
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

License:        Apache-2.0
URL:            https://docs.openstack.org/cinderlib/latest/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
# We need to patch tox.ini to make pyproject tox based macros work fine
Patch01:        0001-Adapt-tox.ini-for-pyproject-macros.patch
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif
%description
%{common_desc}

%package -n python3-%{pypi_name}
Summary:        %{common_summary}

Requires:       sudo
BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description -n python3-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        Documentation for cinderlib

BuildRequires:  graphviz
%description doc
This package contains the documentation files for %{pypi_name}.

%{common_desc}
%endif

%package -n python3-%{pypi_name}-tests-unit
Summary:        Cinderlib unit tests

# Keep manual requirements in tests subpackages for now
Requires:    python3-%{pypi_name}
Requires:    python3-ddt
Requires:    python3-os-testr
Requires:    python3-oslotest

%description -n python3-%{pypi_name}-tests-unit
This package contains the unit tests for %{pypi_name}.

%{common_desc}

%package -n python3-%{pypi_name}-tests-functional
Summary:        Cinderlib unit tests

# Keep manual requirements in tests subpackages for now
Requires:    python3-%{pypi_name}
Requires:    python3-ddt
Requires:    python3-os-testr
Requires:    python3-oslotest

%description -n python3-%{pypi_name}-tests-functional
This package contains the functional tests for %{pypi_name}.

%{common_desc}

%package -n python3-%{pypi_name}-tests
Summary:        All cinderlib tests

Requires: python3-%{pypi_name}-tests-unit
Requires: python3-%{pypi_name}-tests-functional

%description -n python3-%{pypi_name}-tests
Virtual package for all %{pypi_name} tests.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

# Remove the devstack plugin, gate playbooks, and CI tools
rm -rf devstack playbooks tools

sed -i /.*-c{env:TOX_CONSTRAINTS_FILE.*/d tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs};do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build leftovers
rm -rf doc/build/html/{.doctrees,.buildinfo,.placeholder,_sources}
%endif

%check
%tox -e %{default_toxenv}

%install
%pyproject_install

%files -n python3-%{pypi_name}
%license LICENSE
%{python3_sitelib}/cinderlib*
%exclude %{python3_sitelib}/%{pypi_name}/tests

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html
%endif

%files -n python3-%{pypi_name}-tests-unit
%license LICENSE
%{python3_sitelib}/%{pypi_name}/tests/unit/*

%files -n python3-%{pypi_name}-tests-functional
%license LICENSE
%{python3_sitelib}/%{pypi_name}/tests/functional/*

%files -n python3-%{pypi_name}-tests
%exclude /*

%changelog
