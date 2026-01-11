%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%global akmod_name google-coral
%global kmodsrc_name google-coral-kmodsrc

Name:           google-coral-kmod
Version:        1.0
Release:        55%{?dist}
Summary:        Kernel module for Google Coral Edge TPU

License:        GPLv2
URL:            https://github.com/google/gasket-driver
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral.conf

BuildRequires:  kmodtool
BuildRequires:  gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  systemd-devel
# O pacote kmodsrc deve estar no seu repositório Copr
BuildRequires:  %{kmodsrc_name} = %{version}

# Chamada mínima para evitar que o kmodtool injete lixo de RHEL
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --kmodname %{name} --akmod 2>/dev/null)

%description
Infrastructure for Google Coral Edge TPU kernel modules.
Manual implementation of the NVIDIA/VirtualBox link structure.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Requires:       %{kmodsrc_name} = %{version}
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
This package installs the source and symlink for Google Coral modules.

%prep
# Não usamos kmodtool_check aqui para evitar parsing de macros do RPM Fusion
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# --- IMPLEMENTAÇÃO MANUAL DO PADRÃO NVIDIA ---
# 1. Localizamos onde o kmodsrc instalou o tarball
# 2. Criamos o link .latest manualmente para garantir que ele apareça

%global akmod_inst_dir %{buildroot}%{_usrsrc}/akmods
mkdir -p %{akmod_inst_dir}

# Criamos um SRPM "falso" ou linkamos o tarball como o akmods espera
# Nota: O akmods no Fedora Workstation busca em /usr/src/akmods/
# Vamos copiar o tarball do kmodsrc para cá para simular o comportamento
cp /usr/share/%{kmodsrc_name}-%{version}/%{kmodsrc_name}-%{version}.tar.xz %{akmod_inst_dir}/%{name}-%{version}.tar.xz

# Criamos o link simbólico .latest exatamente como o da NVIDIA
ln -s %{name}-%{version}.tar.xz %{akmod_inst_dir}/%{akmod_name}.latest

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
%{_usrsrc}/akmods/%{name}-%{version}.tar.xz
%{_usrsrc}/akmods/%{akmod_name}.latest
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-55
- Manual creation of .latest symlink to bypass repository macro limitations.
