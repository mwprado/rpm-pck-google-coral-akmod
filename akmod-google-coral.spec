# 1. Configurações de controle de build (Padrão RPM Fusion/VirtualBox)
%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Definição manual da macro para evitar erro no Copr (Extraído do padrão Nvidia/VirtualBox)
%global AkmodsBuildRequires gcc, make, kernel-devel, kmodtool, elfutils-libelf-devel

%global akmod_name google-coral
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           google-coral-kmod
Version:        1.0
Release:        29.git%{shortcommit}%{?dist}
Summary:        Módulos do kernel para Google Coral Edge TPU (Padrão RPM Fusion)

License:        GPLv2
URL:            https://github.com/google/%{repo_name}
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz

# Arquivos de suporte (Certifique-se que estão no mesmo nível do spec no git)
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

# 2. Dependências de Build usando a macro definida acima
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros

# 3. Invocação do kmodtool (O "Cérebro" do VirtualBox-kmod.spec)
# Esta macro gera dinamicamente os sub-pacotes kmod para o Silverblue
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo %{repo_name} --akmod %{akmod_name} %{?kernels:--kmp %{?kernels}} 2>/dev/null)

%description
Este pacote fornece os módulos do kernel Gasket e Apex para o Google Coral.
Segue o padrão de infraestrutura akmod utilizado pela NVIDIA e VirtualBox.

# --- SEÇÃO DO PACOTE AKMOD (Fontes) ---
%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
Este pacote contém o código-fonte patcheado do driver Coral para que o 
akmods possa compilar o binário automaticamente para o seu kernel.

%prep
# Verifica o ambiente de kernel (Macro do VirtualBox)
%{?kmodtool_check}
%setup -q -n %{repo_name}-%{commit}

# Aplica os patches de compatibilidade (importante para kernels 6.12+)
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

# Prepara a pasta de build isolada por arquitetura (Padrão Nvidia)
mkdir -p _kmod_build_%{_target_cpu}
cp -r src/* _kmod_build_%{_target_cpu}/

%build
# Vazio: o build real acontece no computador do usuário via akmods

%install
# 1. Instalação dos fontes para o akmod
%global inst_dir %{_usrsrc}/akmods/%{akmod_name}-%{version}-%{release}
mkdir -p %{buildroot}%{inst_dir}
cp -r _kmod_build_%{_target_cpu}/* %{buildroot}%{inst_dir}/

# 2. Arquivo de controle .nm (Vital para o Silverblue reconhecer o akmod)
mkdir -p %{buildroot}%{_sysconfdir}/akmods
echo "%{akmod_name}" > %{buildroot}%{_sysconfdir}/akmods/%{akmod_name}.nm

# 3. Regras de sistema, carga de módulos e grupos
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre -n akmod-%{akmod_name}
# Cria o grupo 'coral' antes da instalação
%sysusers_create_package %{akmod_name} %{SOURCE5}

%post -n akmod-%{akmod_name}
# Dispara a compilação local imediata se possível
%{_sbindir}/akmods --force --akmod %{akmod_name} &>/dev/null || :

%files -n akmod-%{akmod_name}
%license LICENSE
%{inst_dir}
%{_sysconfdir}/akmods/%{akmod_name}.nm
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-29
- Fix no erro de parsing do Copr definindo a macro AkmodsBuildRequires globalmente.
- Sincronização total com os padrões extraídos dos specs Nvidia e VirtualBox.
