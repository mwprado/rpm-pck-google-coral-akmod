%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

%global akmod_name google-coral
%global kmodsrc_name google-coral-kmodsrc

Name:           google-coral-kmod
Version:        1.0
Release:        57%{?dist}
Summary:        Kernel module for Google Coral Edge TPU

License:        GPLv2
URL:            https://github.com/google/gasket-driver
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source5:        google-coral.conf

# --- REQUIRES EXATAMENTE COMO VOCÊ QUER ---
%global AkmodsBuildRequires %{_bindir}/kmodtool, %{kmodsrc_name} = %{version}, gcc, make, kernel-devel, elfutils-libelf-devel
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros

# --- O PULO DO GATO: FILTRANDO O OUTPUT DO KMODTOOL ---
# Executamos o kmodtool, mas filtramos (via sed) qualquer linha que contenha 'rhel'
# Isso impede que o erro de 'Unknown tag' aconteça no Fedora 43.
%{?kmodtool_prefix}
%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed '/rhel/d')

%description
Infrastructure for Google Coral Edge TPU kernel modules.
Filtered kmodtool output to support Fedora 43 strict parsing.

%package -n akmod-%{akmod_name}
Summary:        Akmod package for %{akmod_name} kernel module(s)
Requires:       akmods kmodtool
Requires:       %{kmodsrc_name} = %{version}
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description -n akmod-%{akmod_name}
This package installs the infrastructure to build Google Coral modules.

%prep
# Mantemos o kmodtool_check agora que o output está limpo
%{?kmodtool_check}
%setup -q -T -c -n %{name}-%{version}

%build
# Vazio

%install
# Agora que usamos --repo rpmfusion no kmodtool acima, a macro akmod_install 
# deve funcionar corretamente para gerar o link .latest
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
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sun Jan 11 2026 mwprado <mwprado@github> - 1.0-57
- Version 57: Filtered kmodtool output to remove problematic RHEL tags.
- Restored --repo rpmfusion flag for proper akmod_install integration.
