%define buildforkernels akmod

Name:           google-coral-kmod
Version:        1.0
Release:        1%{?dist}
Summary:        Kernel module for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

# Este pacote foca apenas no kmodtool e no código fonte
BuildRequires:  %{_bindir}/kmodtool [cite: 4]
BuildRequires:  google-coral-kmodsrc = %{version}
BuildRequires:  gcc, make, xz, time, kernel-devel, elfutils-libelf-devel
# Exigência para o funcionamento do akmod [cite: 26, 40]
BuildRequires:  sharutils [cite: 26, 40]
%define AkmodsBuildRequires sharutils [cite: 26]

# Injeção mágica do kmodtool (Padrão MadWiFi/RPM Fusion) [cite: 4, 31]
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
This package contains the akmod infrastructure for the Google Coral Edge TPU driver[cite: 5, 25].
It provides the source package for automatic kernel module building[cite: 1, 31].

%prep
%{?kmodtool_check} [cite: 6]
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio: o build real ocorre no cliente via akmods [cite: 3]

%install
mkdir -p %{buildroot}%{_usrsrc}/akmods
# Link .latest relativo apontando para o SRPM (Padrão NVIDIA/VirtualBox)
ln -sf %{name}-%{version}-%{release}.src.rpm %{buildroot}%{_usrsrc}/akmods/google-coral.latest

# Instalação via macro oficial [cite: 9]
%{?akmod_install} [cite: 9]

%files
# O kmodtool preenche esta seção automaticamente para o subpacote akmod [cite: 4]

%changelog
* Sun Jan 18 2026 mwprado <mwprado@github> - 1.0-1
- Clean kmod-only package based on MadWiFi template.
