%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

# Definição manual para o Copr
%global AkmodsBuildRequires gcc, make, kernel-devel, kmodtool, elfutils-libelf-devel

%global akmod_name google-coral
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           google-coral-kmod
Version:        1.0
Release:        46.git%{shortcommit}%{?dist}
Summary:        Módulos do kernel para Google Coral (Padrão NVIDIA/VirtualBox)

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

# O kmodtool faz a mágica de criar os subpacotes
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo %{repo_name} --akmod %{akmod_name} %{?kernels:--kmp %{?kernels}} 2>/dev/null)

%description
Driver Google Coral. Esta versão força a criação do link .latest e do SRPM.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name}
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

# A NVIDIA prepara o diretório desta forma para a macro akmod_install funcionar
mkdir -p %{akmod_name}-%{version}
cp -a src/* %{akmod_name}-%{version}/
# Criamos um tarball interno que a macro akmod_install vai converter em SRPM
tar -czf %{akmod_name}-%{version}.tar.gz %{akmod_name}-%{version}

%build
# Vazio

%install
# Em vez de copiar para /usr/src/akmods, usamos a macro que o RPM Fusion usa
# Ela exige que o tarball esteja no diretório atual
install -D -m 0644 %{akmod_name}-%{version}.tar.gz %{buildroot}%{_datadir}/%{akmod_name}/%{akmod_name}-%{version}.tar.gz

# Esta macro agora terá o "combustível" (tarball) para criar o SRPM e o link .latest
%{?akmod_install}

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
%license LICENSE
# A macro akmod_install adiciona automaticamente os itens em /usr/src/akmods/
%{_datadir}/%{akmod_name}/
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-46
- Versão 46: Preparação de tarball interno para forçar criação de SRPM e link .latest.
