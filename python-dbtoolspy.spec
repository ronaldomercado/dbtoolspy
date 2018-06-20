Name: python-dbtoolspy
Summary: Python Module to Read EPICS Database
Version: 1.0.0
Release: 1%{?dist}
Source0: https://pypi.io/packages/source/d/dbtoolspy/dbtoolspy-%{version}.tar.gz
License: BSD
Group: Development/Libraries
Vendor: Xiaoqiang Wang <xiaoqiang.wang AT psi DOT ch>
Url: https://github.com/paulscherrerinstitute/dbtoolspy

BuildRequires: python-setuptools

BuildArch: noarch

# Do not check .so files in the python_sitelib directory
# or any files in the application's directory for provides
%global __provides_exclude_from ^%{python_sitelib}/.*\\.so$
%global __requires_exclude_from ^%{python_sitelib}/.*\\.so$
%global _unpackaged_files_terminate_build      0
%global _binaries_in_noarch_packages_terminate_build   0

%description

This Python module provides functions to read EPICS substitution
and template file.

%prep

%setup -n dbtoolspy-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
