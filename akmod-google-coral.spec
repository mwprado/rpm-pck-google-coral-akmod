%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Mantendo o padrão NVIDIA do seu arquivo
Name:           google-coral-kmod
Version:        1.0
Release:        28.20260105git5815ee3%{?dist}
Summary:        Google Coral Edge TPU kernel module
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source0:        %{url}/archive/5815ee3908a46a415aac616ac7b9aedcb98a504c/gasket-driver-5815ee3.tar.gz
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  systemd-devel, systemd-rpm-macros

# FORÇANDO OS PROVIDES QUE A NVIDIA GERA
# Se a macro falhar, o RPM ainda terá os metadados necessários
Provides:       akmod(%{name}) = %{version}-%{release}
Provides:       google-coral-kmod-common = %{version}

# Chamada da macro exatamente como no nvidia-kmod.spec (linha 39 do seu arquivo)
%{!?kernels:%{?buildforkernels: %{expand:%( %{_bindir}/kmodtool --target %{_target_cpu} --repo %{name} --akmod %{name} %{?buildforkernels:--%{buildforkernels}} 2>/dev/null )}}}

%description
Google Coral Edge TPU driver. Segue o padrão NVIDIA/RPM Fusion.

%prep
%setup -q -n gasket-driver-5815ee3908a46a415aac616ac7b9aedcb98a504c
%patch -P 3 -p1
%patch -P 4 -p1

# Estrutura de build idêntica à NVIDIA
mkdir -p _kmod_build_%{_target_cpu}
cp -r src/* _kmod_build_%{_target_cpu}/

%build
for kernel_version in %{?kernel_versions} ; do
    make -C /lib/modules/${kernel_version%%___*}/build M=$(pwd)/_kmod_build_${kernel_version##*___} modules
done

%install
# A NVIDIA instala os fontes numa pasta com o nome do pacote
install -d %{buildroot}%{_usrsrc}/akmods/google-coral
cp -r src/* %{buildroot}%{_usrsrc}/akmods/google-coral/

# O akmods precisa de um arquivo de controle se a macro falhar
install -d %{buildroot}%{_sysconfdir}/akmods
echo "google-coral" > %{buildroot}%{_sysconfdir}/akmods/%{name}.nm

install -D -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
install -D -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
%sysusers_create_package google-coral %{SOURCE5}

%files
%license LICENSE
%{_usrsrc}/akmods/google-coral
%{_sysconfdir}/akmods/%{name}.nm
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sat Jan 10 2026 mwprado <mwprado@github> - 1.0-28
- Provides akmod() adicionado manualmente para garantir detecção.
- Adicionado arquivo .nm como fallback caso a macro kmodtool não expanda no Copr.
