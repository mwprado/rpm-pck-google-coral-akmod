%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%global akmod_name google-coral
# Nome do pacote de fontes que criamos separadamente
%global kmodsrc_name google-coral-kmodsrc

Name:           google-coral-kmod
Version:        1.0
Release:        50%{?dist}
Summary:        Kernel module for Google Coral Edge TPU

License:        GPLv2
URL:            https://github.com/google/gasket-driver
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral-group.conf

# Requisitos de Build - Padrão exato do RPM Fusion
BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  systemd-devel
# O kmodsrc deve estar no repositório Copr para este build passar
BuildRequires:  %{kmodsrc_name} = %{version}

# Mágica do kmodtool para gerar os subpacotes kmod
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)

%description
Package to manage Google Coral Edge TPU kernel modules.
This package follows the RPM Fusion guidelines for akmod infrastructure.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Requires:       %{kmodsrc_name} = %{version}
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
This package installs the infrastructure to build Google Coral modules
using the sources provided by the kmodsrc package.

%prep
# Verifica se o kmodtool funcionou
%{?kmodtool_check}
# Cria o diretório de build vazio (o akmod_install buscará os fontes em /usr/share)
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio: akmods constroem no cliente

%install
# A macro akmod_install busca o tarball em /usr/share/google-coral-kmod-1.0/
# que deve ter sido instalado pelo pacote google-coral-kmodsrc
%{?akmod_install}

# Instalação de arquivos de sistema (Udev, Modules-load, Groups)
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre -n akmod-%{akmod_name}
%sysusers_create_package %{akmod_name} %{SOURCE5}

%post -n akmod-%{akmod_name}
# Dispara o build do akmod imediatamente após a instalação
%{_sbindir}/akmods --force --akmod %{akmod_name} &>/dev/null || :

%files -n akmod-%{akmod_name}
%license
# O akmod_install cuida dos arquivos em /usr/src/akmods/
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-50
- Version 50: Cleaned up RHEL macros to fix Copr parsing error.
- Verified akmod_install and kmodsrc dependency.
