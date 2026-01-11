# 1. Definições de controle (Idêntico ao VirtualBox/NVIDIA)
%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Fallback para o Copr
%global AkmodsBuildRequires gcc, make, kernel-devel, kmodtool, elfutils-libelf-devel

%global akmod_name google-coral
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           google-coral-kmod
Version:        1.0
Release:        45.git%{shortcommit}%{?dist}
Summary:        Módulos do kernel para Google Coral (Padrão RPM Fusion)

License:        GPLv2
URL:            https://github.com/google/%{repo_name}
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros

# 2. Invocação do kmodtool (O "Cérebro" do processo)
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo %{repo_name} --akmod %{akmod_name} %{?kernels:--kmp %{?kernels}} 2>/dev/null)

%description
Pacote de driver para Google Coral. Esta versão usa a macro akmod_install 
para gerar o link simbólico .latest e o SRPM em /usr/src/akmods/.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
Código-fonte patcheado para compilação via akmods.

%prep
%{?kmodtool_check}
%setup -q -n %{repo_name}-%{commit}

# Aplicando os patches
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

# Criamos a pasta que o akmod_install vai usar para gerar o SRPM
mkdir -p _kmod_build_%{_target_cpu}
cp -r src/* _kmod_build_%{_target_cpu}/

%build
# O build real ocorre via akmods no cliente

%install
# A "MÁGICA" QUE ESTAVA FALTANDO:
# Esta macro gera o .src.rpm e o link .latest em /usr/src/akmods/
# Ela substitui o "mkdir -p %{buildroot}%{_usrsrc}/akmods/..."
%{?akmod_install}

# Instalação de arquivos de sistema
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
%license LICENSE
# Note: A macro akmod_install já adiciona os arquivos em /usr/src/akmods/ à lista de arquivos
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-45
- Versão 45: Adição da macro akmod_install.
- Agora gera o SRPM e o link .latest em /usr/src/akmods/, idêntico ao NVIDIA e VirtualBox.
