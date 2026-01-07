%global debug_package %{nil}
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapshotdate 20260105
%global akmod_name google-coral

Name:           google-coral-akmod
Version:        1.0
Release:        7.%{snapshotdate}git%{shortcommit}%{?dist}
Summary:        Akmod package for Google Coral Edge TPU (Gasket & Apex)
License:        GPLv2
URL:            https://github.com/google/%{repo_name}

# Source0: Código fonte original do Google [cite: 1]
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz

# Referências diretas para os arquivos no seu GitHub (Raw) 
# Isso evita o erro de "No such file or directory" ao tentar extrair tarballs aninhados
%global raw_url https://raw.githubusercontent.com/mwprado/rpm-pck-google-coral-akmod/main
Source1:        %{raw_url}/99-google-coral.rules
Source2:        %{raw_url}/google-coral.conf
Source3:        %{raw_url}/fix-for-no_llseek.patch
Source4:        %{raw_url}/fix-for-module-import-ns.patch

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  kernel-devel
BuildRequires:  kmodtool
BuildRequires:  systemd-devel
Requires:       akmods
Requires:       kmodtool
Requires(pre):  shadow-utils

Provides:       %{akmod_name}-kmod-common = %{version}
Requires:       %{akmod_name}-kmod-common = %{version}

%description
Este pacote fornece o código fonte para o akmod gerar os drivers gasket e apex 
para o Google Coral[cite: 3]. Patches e configs aplicados via repositório mwprado.

%prep
# Extrai apenas o código do Google 
%setup -q -n %{repo_name}-%{commit}

# Aplica os patches usando as referências de Source diretas do RPM 
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

%build
# Preparado para o runtime do akmod

%install
# 1. Instalar fontes para o akmod 
dest_dir=%{buildroot}%{_usrsrc}/akmods/%{akmod_name}-%{version}-%{release}
mkdir -p $dest_dir
cp -r src/* $dest_dir/

# 2. Instalar arquivos de configuração usando as macros %{SOURCE} 
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d/
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

%pre
getent group coral >/dev/null || groupadd -r coral [cite: 5]
exit 0

%post
/usr/bin/udevadm control --reload-rules && /usr/bin/udevadm trigger || : [cite: 6]
%{_sbindir}/akmods --force --akmod %{akmod_name} &>/dev/null || : [cite: 6]

%files
%license LICENSE
%{_usrsrc}/akmods/%{akmod_name}-%{version}-%{release}
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf

%changelog
* Wed Jan 07 2026 mwprado <mwprado@github> - 1.0-7
- Correção do erro de diretório no %prep usando caminhos Raw do GitHub.
