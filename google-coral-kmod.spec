%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%global akmod_name google-coral
%global kmodsrc_name google-coral-kmodsrc

Name:           google-coral-kmod
Version:        1.0
Release:        58%{?dist}
Summary:        Kernel module for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral-group.conf

# --- REQUIRES EXATAMENTE COMO O PADRÃO EXIGE ---
%global AkmodsBuildRequires %{_bindir}/kmodtool, %{kmodsrc_name} = %{version}, gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros

# O PONTO CRUCIAL: O kmodtool deve ser chamado aqui, 
# APÓS os BuildRequires e ANTES da %description.
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
This package installs the infrastructure to build Google Coral modules.

%prep
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# A macro akmod_install do RPM Fusion busca o tarball em /usr/share/
# instalado pelo pacote google-coral-kmodsrc.
%{?akmod_install}

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
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-58
- Version 58: Fixed kmodtool invocation placement to avoid 'Unknown tag %global' error.
