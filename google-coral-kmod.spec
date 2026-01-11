# 1. Controle de Build
%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%global akmod_name google-coral
%global kmodsrc_name google-coral-kmodsrc

Name:           google-coral-kmod
Version:        1.0
Release:        51%{?dist}
Summary:        Kernel module for Google Coral Edge TPU

License:        GPLv2
URL:            https://github.com/google/gasket-driver
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral.conf

# 2. Dependências de Build (Padrão RPM Fusion)
BuildRequires:  kmodtool
BuildRequires:  gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  systemd-devel
# Exige que o pacote kmodsrc já esteja buildado no Copr
BuildRequires:  %{kmodsrc_name} = %{version}

# 3. Invocação do kmodtool
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)

%description
Infrastructure for Google Coral Edge TPU kernel modules.
Follows the two-package (kmodsrc + akmod) architecture of RPM Fusion.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Requires:       %{kmodsrc_name} = %{version}
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
This package installs the infrastructure to build Google Coral modules.

%prep
# Verifica o kmodtool
%{?kmodtool_check}
# Cria o diretório de build sem baixar fontes (eles vêm do kmodsrc)
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# A macro oficial que lê o tarball de /usr/share e gera o link .latest
%{?akmod_install}

# Arquivos de sistema
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre -n akmod-%{akmod_name}
%sysusers_create_package %{akmod_name} %{SOURCE5}

%post -n akmod-%{akmod_name}
%{_sbindir}/akmods --force --akmod %{akmod_name} &>/dev/null || :

%files -n akmod-%{akmod_name}
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-51
- Version 51: Absolute cleanup of RHEL/KABI macros to resolve Copr parse errors.
- Strict two-package architecture implementation.
