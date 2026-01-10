%global debug_package %{nil}
%global repo_name gasket-driver
%global commit      5815ee3908a46a415aac616ac7b9aedcb98a504c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapshotdate 20260105

# 1. Nomes idênticos ao padrão NVIDIA
%global akmod_name google-coral
%global kmod_name  google-coral

Name:           akmod-google-coral
Version:        1.0
Release:        22.%{snapshotdate}git%{shortcommit}%{?dist}
Summary:        Akmod package for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/%{repo_name}

Source0:        %{url}/archive/%{commit}/%{repo_name}-%{shortcommit}.tar.gz
# ... (Source1 a Source5 permanecem iguais)

BuildRequires:  make gcc kernel-devel kmodtool systemd-devel systemd-rpm-macros
Requires:       akmods kmodtool

# 2. As macros que a NVIDIA usa para gerar os subpacotes kmod-NOME
%{?akmod_global}
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo %{repo_name} --akmod %{akmod_name} %{?kernels:--kmp %{?kernels}} 2>/dev/null)

# Provides explícitos para o comando akmods --akmod google-coral-kmod funcionar
Provides: akmod(%{akmod_name}-kmod) = %{version}-%{release}
Provides: %{akmod_name}-kmod = %{version}-%{release}

%description
Google Coral driver akmod package. Follows the NVIDIA kmod packaging standard.

%prep
%setup -q -n %{repo_name}-%{commit}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}

%install
# 3. PASTA FIXA (Igual à NVIDIA)
# Em vez de pasta com versão, usamos o nome simples para o akmods não se perder
%global inst_dir %{_usrsrc}/akmods/%{akmod_name}
mkdir -p %{buildroot}%{inst_dir}
cp -r src/* %{buildroot}%{inst_dir}/

# 4. ARQUIVO .NM (Igual à NVIDIA)
# O arquivo se chama google-coral-kmod.nm para aceitar o comando com sufixo
mkdir -p %{buildroot}%{_sysconfdir}/akmods
echo "%{akmod_name}" > %{buildroot}%{_sysconfdir}/akmods/%{akmod_name}-kmod.nm

# ... (Instalação dos outros arquivos permanece igual)

%files
%license LICENSE
%{inst_dir}
%{_sysconfdir}/akmods/%{akmod_name}-kmod.nm
# ... (restante dos arquivos)
