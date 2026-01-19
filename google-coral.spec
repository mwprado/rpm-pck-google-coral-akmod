Name:           google-coral
Version:        1.0
Release:        1%{?dist}
Summary:        Userland support for Google Coral Edge TPU
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source0:        https://raw.githubusercontent.com/mwprado/rpm-pck-akmod-google-coral/main/99-google-coral.rules
Source1:        https://raw.githubusercontent.com/mwprado/rpm-pck-akmod-google-coral/main/google-coral.conf
Source2:        https://raw.githubusercontent.com/mwprado/rpm-pck-akmod-google-coral/main/google-coral-group.conf

BuildArch:      noarch

# Padrão MadWiFi de dependências
Provides:       google-coral-kmod-common = %{version}
Requires:       google-coral-kmod >= %{version}

BuildRequires:  systemd-rpm-macros

%description
Userland configuration for Google Coral Edge TPU.
Includes udev rules, group creation, and module loading configuration.

%prep
%setup -q -c -n %{name}-%{version} -T

%install
mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE0} %{buildroot}%{_udevrulesdir}/99-google-coral.rules

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
install -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf

mkdir -p %{buildroot}%{_sysusersdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
%sysusers_create_package %{name} %{SOURCE2}

%files
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Mon Jan 19 2026 mwprado <mwprado@github> - 1.0-1
- Final clean version based on split-package pattern.
