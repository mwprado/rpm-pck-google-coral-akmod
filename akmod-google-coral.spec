%global akmod_name google-coral
%global _internal_name kmod-google-coral

Name:           akmod-google-coral
Version:        1.0
Release:        47.20260105git5815ee3%{?dist}
Summary:        Akmod package for Google Coral Edge TPU driver
License:        GPLv2
URL:            https://github.com/google/gasket-driver

Source0:        %{url}/archive/5815ee3908a46a415aac616ac7b9aedcb98a504c/gasket-driver-5815ee3.tar.gz
Source1:        99-google-coral.rules
Source2:        google-coral.conf
Source3:        fix-for-no_llseek.patch
Source4:        fix-for-module-import-ns.patch
Source5:        google-coral-group.conf

# Ferramentas para o Inception (gerar o SRPM dentro do build)
BuildRequires:  rpm-build, gcc, make, sed
BuildRequires:  systemd-rpm-macros

# O Provide que o comando 'akmods' usa para te encontrar
Provides:       akmod(%{akmod_name}) = %{version}-%{release}

%description
Este pacote contém o SRPM do driver Google Coral. O utilitário akmods 
utilizará este arquivo para reconstruir o kmod binário para o seu kernel.

%prep
%setup -q -n gasket-driver-5815ee3908a46a415aac616ac7b9aedcb98a504c
%patch -P 3 -p1
%patch -P 4 -p1

%build
# === PASSO 1: Criar o SPEC do kmod que irá dentro do SRPM ===
cat << 'EOF' > %{_internal_name}.spec
Name:           %{_internal_name}
Version:        %{version}
Release:        %{release}
Summary:        Google Coral Edge TPU kernel module
License:        GPLv2
Source0:        google-coral-src.tar.gz

%description
Módulo de kernel compilado pelo sistema akmods.

%prep
%setup -q -n google-coral-src

%build
make -C /lib/modules/%{?kver}/build M=$(pwd)/src modules

%install
install -D -m 0644 src/gasket.ko %{buildroot}/lib/modules/%{?kver}/extra/gasket/gasket.ko
install -D -m 0644 src/apex.ko %{buildroot}/lib/modules/%{?kver}/extra/gasket/apex.ko
EOF

%install
# === PASSO 2: Gerar o SRPM Real ===
mkdir -p rpmbuild/{SOURCES,SPECS,SRPMS}
# Criamos o tarball com o código patcheado
tar -czf rpmbuild/SOURCES/google-coral-src.tar.gz .
cp %{_internal_name}.spec rpmbuild/SPECS/

# Comando de build do SRPM interno
rpmbuild -bs rpmbuild/SPECS/%{_internal_name}.spec \
    --define "_topdir $(pwd)/rpmbuild" \
    --define "kver %{kernel_version}"

# === PASSO 3: Instalar o SRPM e o link .latest ===
install -d %{buildroot}%{_usrsrc}/akmods/
install -p -m 0644 rpmbuild/SRPMS/%{_internal_name}-*.src.rpm %{buildroot}%{_usrsrc}/akmods/%{_internal_name}.src.rpm

# O link crucial que evita o erro 'É um diretório'
pushd %{buildroot}%{_usrsrc}/akmods/
ln -s %{_internal_name}.src.rpm %{akmod_name}.latest
popd

# Configurações de hardware
install -D -m 0644 %{SOURCE1} %{buildroot}%{_udevrulesdir}/99-google-coral.rules
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modules-load.d/google-coral.conf
install -D -m 0644 %{SOURCE5} %{buildroot}%{_sysusersdir}/google-coral.conf

%pre
%sysusers_create_package google-coral %{SOURCE5}

%files
%license LICENSE
%{_usrsrc}/akmods/%{_internal_name}.src.rpm
%{_usrsrc}/akmods/%{akmod_name}.latest
%{_udevrulesdir}/99-google-coral.rules
%{_sysconfdir}/modules-load.d/google-coral.conf
%{_sysusersdir}/google-coral.conf

%changelog
* Sat Jan 10 2026 mwprado <mwprado@github> - 1.0-47
- Arquitetura idêntica ao RPM Fusion: akmod transportando o SRPM do kmod.
