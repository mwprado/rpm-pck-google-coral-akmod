# 1. Definições de Nome (Rigor VirtualBox)
%global kmodname google-coral
%global kmodsrc_name google-coral-kmodsrc

%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

Name:           %{kmodname}-kmod
Version:        1.0
Release:        79%{?dist}
Summary:        Kernel module for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral-group.conf

# 2. BuildRequires (Cópia fiel do VirtualBox)
BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  %{kmodsrc_name} = %{version}
BuildRequires:  gcc, make, xz, time, kernel-devel, elfutils-libelf-devel, systemd-devel, systemd-rpm-macros

# 3. A "Mágica" do VirtualBox (Injeção de Código)
# Esta linha gera o %package, %description, %post e %files do akmod-google-coral
%{expand:%(/usr/bin/kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Google Coral Edge TPU kernel module infrastructure.
Ficheiro SPEC baseado rigorosamente no modelo VirtualBox-kmod do RPM Fusion.

%prep
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# 4. Expansão Manual da Instalação (Para garantir o .latest no Copr)
mkdir -p %{buildroot}%{_usrsrc}/akmods
ln -sf %{_datadir}/%{kmodsrc_name}-%{version}/%{name}-%{version}.tar.xz \
    %{buildroot}%{_usrsrc}/akmods/%{kmodname}.latest

# Ficheiros de sistema (Udev, Modules-load, Sysusers)
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

# 5. O SEGREDO: O VirtualBox usa esta macro para "pescar" os ficheiros extras
# para dentro do pacote que o kmodtool gerou.
%{?kmodtool_files}

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-79
- Version 79: Strict VirtualBox-kmod clone.
- Removed all manual package naming and script sections.
- Uses kmodtool_files macro to handle extra configurations.
