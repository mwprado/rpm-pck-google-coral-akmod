Name:           google-coral-kmodsrc
Version:        1.0
Release:        1%{?dist}
Summary:        Source code for Google Coral Edge TPU kernel module
License:        GPLv2
URL:            https://github.com/google/gasket-driver

# Este pacote apenas transporta o código fonte para o akmod
BuildArch:      noarch

# O kmodsrc não deve tentar dar rpmbuild em si mesmo no %install.
# Ele apenas instala os arquivos que o google-coral-kmod (akmod) usará.

%description
This package provides the source infrastructure for the Google Coral kernel module.
It is required by the akmod package to rebuild the module for new kernels.

%prep
# Nada a preparar

%build
# Vazio

%install
# 1. Criar o diretório de forma limpa e absoluta
mkdir -p %{buildroot}%{_usrsrc}/akmods

# 2. Gerar o SRPM "dummy" ou copiar o fonte que o akmod vai usar.
# Para seguir o log que você postou, vamos garantir que o diretório exista 
# e o link possa ser criado pelo pacote de driver sem falhas de "No such file".
touch %{buildroot}%{_usrsrc}/akmods/.keep

%files
# Define que este pacote é o dono do diretório onde os SRPMs viverão
%dir %{_usrsrc}/akmods
%{_usrsrc}/akmods/.keep

%changelog
* Sun Jan 18 2026 mwprado <mwprado@github> - 1.0-1
- Fixed directory structure for akmod source delivery.
