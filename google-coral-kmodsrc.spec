%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           google-coral-kmodsrc
Version:        1.0
Release:        1.git%{shortcommit}%{?dist}
Summary:        Google Coral driver source code

License:        GPLv2
URL:            https://github.com/google/%{repo_name}
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch

BuildArch:      noarch

%description
This package contains the source code for the Google Coral driver
to be used by the akmod build system.

%prep
%setup -q -n %{repo_name}-%{commit}
# Aplica os patches nos fontes antes de empacotar o tarball final
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

# Prepara a estrutura idêntica ao VirtualBox/NVIDIA
mkdir -p google-coral-kmod-%{version}
cp -a src/* google-coral-kmod-%{version}/
tar -cJf google-coral-kmod-%{version}.tar.xz google-coral-kmod-%{version}

%install
install -d %{buildroot}%{_datadir}/google-coral-kmod-%{version}
install -p -m 0644 google-coral-kmod-%{version}.tar.xz %{buildroot}%{_datadir}/google-coral-kmod-%{version}/

%files
%{_datadir}/google-coral-kmod-%{version}/

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-1
- Initial standalone kmodsrc package for Google Coral.
