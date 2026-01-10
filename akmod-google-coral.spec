%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Definições de nome iguais ao da NVIDIA
%global kmod_name google-coral

Name:           google-coral-kmod
Version:        1.0
Release:        26.20260105git5815ee3%{?dist}
Summary:        Google Coral Edge TPU kernel module
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source0:        %{url}/archive/5815ee3908a46a415aac616ac7b9aedcb98a504c/gasket-driver-5815ee3.tar.gz
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

# O pulo do gato da NVIDIA: BuildRequires dinâmico
%global AkmodsBuildRequires %{_bindir}/kmodtool
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  systemd-devel, systemd-rpm-macros

# ESTA É A LINHA QUE DEU ERRO - Ajustada para o padrão exato da NVIDIA
# Ela gera os subpacotes akmod-google-coral-kmod e kmod-google-coral-kmod
%{!?kernels:%{?buildforkernels: %%{expand:%%( %{_bindir}/kmodtool --target %{_target_cpu} --repo %{name} --akmod %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--kmp %{?kernels}} 2>/dev/null )}}}

%description
Este pacote segue o padrão exato do driver NVIDIA (RPM Fusion).
Fornece suporte para o hardware Google Coral Edge TPU.

%prep
%setup -q -n gasket-driver-5815ee3908a46a415aac616ac7b9aedcb98a504c
%patch -P 3 -p1
%patch -P 4 -p1

# Prepara a estrutura de build como a NVIDIA faz
mkdir -p _kmod_build_%{_target_cpu}
cp -r src/* _kmod_build_%{_target_cpu}/

%build
# Build para os kernels detectados
for kernel_version in %{?kernel_versions} ; do
    make -C /lib/modules/${kernel_version%%___*}/build M=$(pwd)/_kmod_build_${kernel_version##*___} modules
done

%install
# Instalação dos fontes para o akmod
install -d %{buildroot}%{_usrsrc}/akmods/google-coral
cp -r src/* %{buildroot}%{_usrsrc}/akmods/google-coral/

# Arquivos auxiliares
install -D -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
install -D -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
%sysusers_create_package google-coral %{SOURCE5}

%files
%license LICENSE
%{_usrsrc}/akmods/google-coral
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sat Jan 10 2026 mwprado <mwprado@github> - 1.0-26
- Correção da macro kmodtool para evitar erro de parse no Copr/rpkg.
- Sincronização estrita com a lógica de expansão do nvidia-kmod.spec.
