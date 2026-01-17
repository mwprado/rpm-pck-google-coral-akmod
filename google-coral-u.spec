Name:           google-coral
Version:        1.0
Release:        1%{?dist}
Summary:        User-space tools and udev rules for Google Coral Edge TPU

License:        ASL 2.0
URL:            https://github.com/google/gasket-driver
# Usaremos o mesmo source ou um específico para ferramentas, se houver
Source0:        https://github.com/google/gasket-driver/archive/refs/heads/main.tar.gz

BuildArch:      noarch

# Dependência crucial para o Silverblue:
# Ao instalar as regras de usuário, o sistema traz o akmod automaticamente.
Requires:       akmod-google-coral-kmod >= %{version}

# Fornece a tag comum que o padrão Kmods2 espera
Provides:       google-coral-kmod-common = %{version}

%description
Provides the udev rules and configuration files required to use 
Google Coral Edge TPU devices without needing root privileges.

%prep
%setup -q -n gasket-driver-main

%build
# Geralmente aqui não há compilação se forem apenas regras de udev e scripts.
# Se houver ferramentas em C do Google, o 'make' viria aqui.

%install
rm -rf ${RPM_BUILD_ROOT}

# 1. Instalar regras do udev (Caminho padrão no Fedora/Silverblue)
mkdir -p ${RPM_BUILD_ROOT}%{_udevrulesdir}
cat <<EOF > ${RPM_BUILD_ROOT}%{_udevrulesdir}/60-google-coral.rules
# Gasket driver permissions para Coral Edge TPU
SUBSYSTEM=="gasket", KERNEL=="gasket*", GROUP="plugdev", MODE="0660"
SUBSYSTEM=="apex", KERNEL=="apex*", GROUP="plugdev", MODE="0660"
EOF

# 2. Criar o grupo plugdev se necessário (comum em setups de hardware)
# Nota: No Fedora moderno, recomenda-se usar o grupo 'video' ou 'render'
# mas manteremos um padrão customizável ou usaremos 'uaccess' via TAG.

%files
%license LICENSE
%doc README.md
%{_udevrulesdir}/60-google-coral.rules

%changelog
* Sat Jan 17 2026 Seu Nome <seu@email.com> - 1.0-1
- Initial user-space package with udev rules.
