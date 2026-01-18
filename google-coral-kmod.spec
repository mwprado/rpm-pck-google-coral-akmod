%global kmodname google-coral
%define buildforkernels akmod

Name:           google-coral-kmod
Version:        1.0
Release:        1%{?dist}
Summary:        Módulo de kernel para Google Coral Edge TPU
License:        GPLv2

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  google-coral-kmodsrc = %{version}
BuildRequires:  gcc, make, xz, time, kernel-devel, elfutils-libelf-devel
BuildRequires:  sharutils
%define AkmodsBuildRequires sharutils

# Expansão do kmodtool
%{expand:%(/usr/bin/kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Módulo de kernel (akmod) para Google Coral.

%prep
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# 1. Criar o diretório de destino
mkdir -p %{buildroot}%{_usrsrc}/akmods

# 2. Gerar o SRPM dentro do BUILDROOT
rpmbuild --define '_sourcedir %{_sourcedir}' \
         --define '_srcrpmdir %{buildroot}%{_usrsrc}/akmods/' \
         --define 'dist %{dist}' \
         -bs --nodeps %{_specdir}/%{name}.spec

# 3. Criar o link simbólico de forma segura (contexto local)
pushd %{buildroot}%{_usrsrc}/akmods
    # Encontra o nome real do ficheiro gerado
    SRPM_NAME=$(ls google-coral-kmod-*.src.rpm)
    # Cria o link: google-coral.latest -> ficheiro.src.rpm
    ln -sf "$SRPM_NAME" "%{kmodname}.latest"
popd

%{?akmod_install}

%files
%dir %{_usrsrc}/akmods
%{_usrsrc}/akmods/google-coral.latest
%{_usrsrc}/akmods/google-coral-kmod-*.src.rpm

%changelog
* Sun Jan 18 2026 mwprado <mwprado@github> - 1.0-1
- Fix ln: target error using pushd context.
- Separate userland files to google-coral.spec.
