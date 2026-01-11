%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Definições de nomes
%global akmod_name google-coral
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           google-coral-kmod
Version:        1.0
Release:        48.git%{shortcommit}%{?dist}
Summary:        Kernel module for Google Coral Edge TPU

License:        GPLv2
URL:            https://github.com/google/%{repo_name}
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

# Requisitos de Build idênticos à NVIDIA
%global AkmodsBuildRequires %{_bindir}/kmodtool, google-coral-kmodsrc = %{version}, gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-devel

# Mágica do kmodtool
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)

%description
Package to manage Google Coral Edge TPU kernel modules.

# --- PACOTE 1: O KMODSRC (Igual ao xorg-x11-drv-nvidia-kmodsrc) ---
%package -n google-coral-kmodsrc
Summary:        Google Coral kmodsrc package
BuildArch:      noarch

%description -n google-coral-kmodsrc
This package contains the source code for the Google Coral driver
to be used by the akmod build system.

# --- PACOTE 2: O AKMOD (Igual ao akmod-nvidia) ---
%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Requires:       google-coral-kmodsrc = %{version}
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
This package installs the infrastructure to build Google Coral modules.

%prep
%{?kmodtool_check}
%setup -q -n %{repo_name}-%{commit}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

# Prepara o diretório para o tarball do kmodsrc
mkdir -p %{name}-%{version}
cp -a src/* %{name}-%{version}/
tar -cJf %{name}-%{version}.tar.xz %{name}-%{version}

%build
# Vazio

%install
# 1. Instala o tarball no local esperado pelo VirtualBox/NVIDIA
install -d %{buildroot}%{_datadir}/%{name}-%{version}
install -p -m 0644 %{name}-%{version}.tar.xz %{buildroot}%{_datadir}/%{name}-%{version}/%{name}-%{version}.tar.xz

# 2. INVOCAÇÃO DA MACRO AKMOD_INSTALL
# Ela vai ler o tarball acima e criar o link .latest em /usr/src/akmods/
%{?akmod_install}

# 3. Arquivos de sistema
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

# --- ARQUIVOS DO KMODSRC ---
%files -n google-coral-kmodsrc
%{_datadir}/%{name}-%{version}/

# --- ARQUIVOS DO AKMOD ---
%files -n akmod-%{akmod_name}
%license LICENSE
# A macro akmod_install adiciona os links em /usr/src/akmods automaticamente
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-48
- Split into kmodsrc and akmod packages (Full NVIDIA/VirtualBox pattern).
- Mandatory xz tarball placement for akmod_install.
