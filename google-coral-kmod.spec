%global kmodname google-coral
%global kmodsrc_name google-coral-kmodsrc

%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

Name:           %{kmodname}-kmod
Version:        1.0
Release:        90%{?dist}
Summary:        Kernel module for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral-group.conf

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  %{kmodsrc_name} = %{version}
BuildRequires:  gcc, make, xz, time, kernel-devel, elfutils-libelf-devel, systemd-devel, systemd-rpm-macros

# 1. Injeção do kmodtool (Define o pacote akmod-google-coral)
%{expand:%(/usr/bin/kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Google Coral Edge TPU kernel module infrastructure.
Rigorously follows VirtualBox-kmod and Kmods2 documentation.

%prep
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# 2. Instalação (Rigor VirtualBox)
mkdir -p %{buildroot}%{_usrsrc}/akmods
# Link relativo para o SRPM no mesmo diretório
ln -sf %{name}-%{version}-%{release}.src.rpm %{buildroot}%{_usrsrc}/akmods/%{kmodname}.latest

mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

# 3. SOLUÇÃO DEFINITIVA PARA O ERRO DE EXECUÇÃO:
# Em vez de chamar a macro que o shell tenta executar, nós anexamos os arquivos
# manualmente no arquivo de lista que o kmodtool gerou para o akmod.
# O arquivo de lista chama-se 'akmod-%{kmodname}.files' (ou similar)
echo "%{_usrsrc}/akmods/%{kmodname}.latest" >> akmod-%{kmodname}.files
echo "%{_udevrulesdir}/99-google-coral.rules" >> akmod-%{kmodname}.files
echo "%{_sysconfdir}/modules-load.d/google-coral.conf" >> akmod-%{kmodname}.files
echo "%{_sysusersdir}/google-coral.conf" >> akmod-%{kmodname}.files

%files -f akmod-%{kmodname}.files
# Esta seção herda a lista gerada pelo kmodtool + nossos arquivos extras.

%changelog
* Tue Jan 13 2026 mwprado <mwprado@github> - 1.0-90
- Version 90: Fixed shell execution error in %install.
- Manually appended extra files to the kmodtool generated file list.
- Strictly followed NVIDIA/VirtualBox symlink pattern.
