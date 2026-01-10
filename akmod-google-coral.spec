%global debug_package %{nil}
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapshotdate 20260105
%global akmod_name google-coral

# Macro essencial para o akmods reconhecer o pacote no Fedora/Silverblue
%{?akmod_global}

Name:           akmod-google-coral
Version:        1.0
Release:        15.%{snapshotdate}git%{shortcommit}%{?dist}
Summary:        Akmod package for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/%{repo_name}

# Source0: Código original do Google
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz

# Referências diretas do seu GitHub para ficheiros de suporte
%global raw_url https://raw.githubusercontent.com/mwprado/rpm-pck-google-coral-akmod/main
Source1:        %{raw_url}/99-google-coral.rules
Source2:        %{raw_url}/google-coral.conf
Source3:        %{raw_url}/fix-for-no_llseek.patch
Source4:        %{raw_url}/fix-for-module-import-ns.patch
Source5:        %{raw_url}/google-coral-group.conf

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  kernel-devel
BuildRequires:  kmodtool
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros

Requires:       akmods
Requires:       kmodtool

# Metadados que o utilitário akmods procura no banco de dados RPM
Provides:       akmod(%{akmod_name}) = %{version}-%{release}
Provides:       %{akmod_name}-kmod-common = %{version}

%description
Este pacote fornece o código fonte patcheado para o akmod gerar os drivers 
gasket e apex para o Google Coral Edge TPU.

%prep
# Extrai o código (a pasta terá o hash do commit aqui no build)
%setup -q -n %{repo_name}-%{commit}

# Aplica os patches ANTES da instalação para que o código fonte 
# que vai para o sistema já esteja compatível com kernels modernos.
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

%build
# Nada a fazer aqui

%install
# 1. Definir o nome da pasta de destino EXATAMENTE como o akmods espera:
# nome-versao-release (sem o hash do commit)
%global akmod_inst_dir %{_usrsrc}/akmods/%{akmod_name}-%{version}-%{release}
mkdir -p %{buildroot}%{akmod_inst_dir}

# Copia apenas o conteúdo da pasta 'src' do driver
cp -r src/* %{buildroot}%{akmod_inst_dir}/

# 2. Instala o ficheiro de registo .nm (Crítico para o Silverblue)
mkdir -p %{buildroot}%{_sysconfdir}/akmods
echo "%{akmod_name}" > %{buildroot}%{_sysconfdir}/akmods/%{akmod_name}.nm

# 3. Regras de Udev
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

# 4. Configuração de carregamento de módulos no boot
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d/
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

# 5. Configuração de grupo via sysusers.d
mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
# Gatilho para criação do grupo 'coral' no momento da instalação
%sysusers_create_package %{akmod_name} %{SOURCE5}

%post
# Recarrega regras udev e tenta disparar o build do akmod
/usr/bin/udevadm control --reload-rules && /usr/bin/udevadm trigger || :
%{_sbindir}/akmods --force --akmod %{akmod_name} &>/dev/null || :

%files
%license LICENSE
%{akmod_inst_dir}
%{_sysconfdir}/akmods/%{akmod_name}.nm
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sat Jan 10 2026 mwprado <mwprado@github> - 1.0-15
- Padronização total do nome para akmod-google-coral.
- Removido o commit hash da pasta de destino em /usr/src/akmods.
- Adicionado ficheiro .nm e Provides akmod() para suporte em Silverblue.
- Patches aplicados diretamente no código fonte empacotado.
