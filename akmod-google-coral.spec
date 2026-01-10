%global debug_package %{nil}
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapshotdate 20260105
%global akmod_name google-coral

# Macro essencial para o ecossistema akmod no Fedora/Silverblue
%{?akmod_global}

Name:           akmod-google-coral
Version:        1.0
Release:        17.%{snapshotdate}git%{shortcommit}%{?dist}
Summary:        Akmod package for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/%{repo_name}

Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz

%global raw_url https://raw.githubusercontent.com/mwprado/rpm-pck-google-coral-akmod/main
Source1:        %{raw_url}/99-google-coral.rules
Source2:        %{raw_url}/google-coral.conf
Source3:        %{raw_url}/fix-for-no_llseek.patch
Source4:        %{raw_url}/fix-for-module-import-ns.patch
Source5:        %{raw_url}/google-coral-group.conf

# BuildRequires mínimos para não travar o build no Silverblue
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  kernel-devel
BuildRequires:  kmodtool
BuildRequires:  systemd-rpm-macros
# Removido systemd-devel para evitar erros de dependência no cliente

Requires:       akmods
Requires:       kmodtool

# Metadados necessários para o utilitário akmods localizar o pacote
Provides:       akmod(%{akmod_name}) = %{version}-%{release}
Provides:       %{akmod_name}-kmod-common = %{version}

%description
Pacote de fontes para o driver Gasket/Apex (Google Coral Edge TPU).
Esta versão v17 remove dependências de build pesadas para facilitar
a compilação automática no Fedora Silverblue.

%prep
%setup -q -n %{repo_name}-%{commit}
# Aplica os patches de compatibilidade com Kernel 6.12+
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

%build
# O build real ocorre na máquina do usuário via akmods

%install
# Define o diretório de destino seguindo estritamente o padrão akmod
%global akmod_inst_dir %{_usrsrc}/akmods/%{akmod_name}-%{version}-%{release}
mkdir -p %{buildroot}%{akmod_inst_dir}

# Copia apenas o conteúdo de 'src' para a raiz da pasta do akmod
cp
