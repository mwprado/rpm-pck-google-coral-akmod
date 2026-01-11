%global kmodname google-coral
%global kmodsrc_name google-coral-kmodsrc

%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

Name:           %{kmodname}-kmod
Version:        1.0
Release:        86%{?dist}
Summary:        Kernel module for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral-group.conf

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  %{kmodsrc_name} = %{version}
BuildRequires:  gcc, make, xz, time, kernel-devel, elfutils-libelf-devel, systemd-devel, systemd-rpm-macros

# 1. Injeção dinâmica do kmodtool
%{expand:%(/usr/bin/kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Google Coral Edge TPU kernel module infrastructure.

%prep
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# 2. O LINK .LATEST (Rigorosamente conforme seus exemplos)
mkdir -p %{buildroot}%{_usrsrc}/akmods
# Criamos o link relativo para o SRPM que reside na mesma pasta
ln -sf %{name}-%{version}-%{release}.src.rpm %{buildroot}%{_usrsrc}/akmods/%{kmodname}.latest

# Instalação de ficheiros extras
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

# 3. A SOLUÇÃO FINAL PARA O COPR:
# O kmodtool injetou o pacote akmod-google-coral. 
# Para adicionar arquivos sem usar "-n" (duplicata), usamos a expansão da lista de arquivos
# que o próprio kmodtool preparou na variável de ambiente.
%{?kmodtool_files}

# Se a macro acima falhar no Copr, usamos a forma manual que o VirtualBox 
# às vezes usa em forks: anexar ao final da lista dinâmica.
%files -f %{name}-%{_target_cpu}.files
%{_usrsrc}/akmods/%{kmodname}.latest
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-86
- Version 86: Used -f flag with the kmodtool generated file list to avoid -n conflicts.
- Fixed unpackaged files error by merging manual files with dynamic list.
