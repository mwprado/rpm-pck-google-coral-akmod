%global debug_package %{nil}
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapshotdate 20260105

# 1. PADRÃO NVIDIA: Nome curto para o akmod e comando
%global akmod_name google-coral

Name:           akmod-google-coral
Version:        1.0
Release:        22.%{snapshotdate}git%{shortcommit}%{?dist}
Summary:        Akmod package for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/%{repo_name}

Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz

%global raw_url https://raw.githubusercontent.com/mwprado/rpm-pck-akmod-google-coral/main
Source1:        %{raw_url}/99-google-coral.rules
Source2:        %{raw_url}/google-coral.conf
Source3:        %{raw_url}/fix-for-no_llseek.patch
Source4:        %{raw_url}/fix-for-module-import-ns.patch
Source5:        %{raw_url}/google-coral-group.conf

BuildRequires:  make gcc kernel-devel kmodtool systemd-devel systemd-rpm-macros
Requires:       akmods kmodtool

# 2. INFRAESTRUTURA AKMOD: Mesmas macros usadas pelo driver NVIDIA
%{?akmod_global}

# Força o Provides que o comando 'akmods --akmod google-coral-kmod' busca
Provides:       akmod(%{akmod_name}-kmod) = %{version}-%{release}
Provides:       %{akmod_name}-kmod-common = %{version}

# Invoca o kmodtool para gerar os metadados de kernel dinâmicos
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo %{repo_name} --akmod %{akmod_name} %{?kernels:--kmp %{?kernels}} 2>/dev/null)

%description
Este pacote provê o driver Gasket/Apex para Google Coral TPU.
Seguindo o padrão NVIDIA, ele instala os fontes em um diretório fixo
e configura o mapeamento para o utilitário akmods.

%prep
%setup -q -n %{repo_name}-%{commit}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

%build
# Processado via akmods no cliente

%install
# 3. DIRETÓRIO FIXO (Igual NVIDIA): /usr/src/akmods/google-coral
# Isso garante que o akmods sempre encontre o código, independente da versão
%global akmod_inst_dir %{_usrsrc}/akmods/%{akmod_name}
mkdir -p %{buildroot}%{akmod_inst_dir}
cp -r src/* %{buildroot}%{akmod_inst_dir}/

# 4. ARQUIVO .NM (Mapeamento NVIDIA):
# O arquivo google-coral-kmod.nm aponta para a pasta google-coral
mkdir -p %{buildroot}%{_sysconfdir}/akmods
echo "%{akmod_name}" > %{buildroot}%{_sysconfdir}/akmods/%{akmod_name}-kmod.nm

# Arquivos de suporte e permissões
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d/
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
%sysusers_create_package %{akmod_name} %{SOURCE5}

%post
# Gatilho de build usando o novo padrão de nome
%{_sbindir}/akmods --force --akmod %{akmod_name}-kmod &>/dev/null || :
/usr/bin/udevadm control --reload-rules && /usr/bin/udevadm trigger || :

%files
%license LICENSE
%{akmod_inst_dir}
%{_sysconfdir}/akmods/%{akmod_name}-kmod.nm
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sat Jan 10 2026 mwprado <mwprado@github> - 1.0-22
- Implementação do diretório de fontes fixo (estilo NVIDIA).
- Arquivo .nm renomeado para google-coral-kmod.nm para consistência de comando.
- Provides akmod(google-coral-kmod) adicionado explicitamente.
