%global debug_package %{nil}

%global basever 2.4.6
#global prerel rc
#global prerelnum 3
%global tag v%{basever}%{?prerel:-%{prerel}.%{prerelnum}}

Name:           caddy
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_versioning_prereleases_with_tilde
Version:        %{basever}%{?prerel:~%{prerel}%{prerelnum}}
Release:        1%{?dist}
Summary:        Web server with automatic HTTPS
License:        ASL 2.0
URL:            https://caddyserver.com

# In order to build Caddy with version information, we need to import it as a
# go module.  To do that, we are going to forgo the traditional source tarball
# and instead use just this file from upstream.  This method requires that we
# allow networking in the build environment.
Source0:        https://raw.githubusercontent.com/caddyserver/caddy/%{tag}/cmd/caddy/main.go
# Use official resources for config, unit file, and welcome page.
# https://github.com/caddyserver/dist
Source1:        https://raw.githubusercontent.com/caddyserver/dist/master/config/Caddyfile
Source2:        https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy.service
Source3:        https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy-api.service
Source4:        https://raw.githubusercontent.com/caddyserver/dist/master/welcome/index.html
Source5:        https://raw.githubusercontent.com/caddyserver/dist/master/scripts/completions/bash-completion
Source6:        https://raw.githubusercontent.com/caddyserver/dist/master/scripts/completions/_caddy
# Since we are not using a traditional source tarball, we need to explicitly
# pull in the license file.
Source10:       https://raw.githubusercontent.com/caddyserver/caddy/%{tag}/LICENSE

# https://github.com/caddyserver/caddy/commit/6bc87ea2ff50a962f16dfafeb125f0f947c1a885
BuildRequires:  golang >= 1.16
BuildRequires:  git-core
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires:  systemd
%else
BuildRequires:  systemd-rpm-macros
%endif
%{?systemd_requires}
Provides:       webserver


%description
Caddy is the web server with automatic HTTPS.


%prep
%setup -q -c -T
# Copy main.go and LICENSE into the build directory.
cp %{S:0} %{S:10} .


%build
# Fedora diverges from upstream Go by disabling the proxy server.  Some of
# Caddy's dependencies reference commits that are no longer upstream, but are
# cached in the proxy.  As long as we are downloading dependencies during the
# build, reset the behavior to prefer the proxy.  This also avoid having a
# build requirement on bzr.
# https://fedoraproject.org/wiki/Changes/golang1.13#Detailed_Description
export GOPROXY='https://proxy.golang.org,direct'

go mod init caddy
echo "require github.com/caddyserver/caddy/v2 %{tag}" >> go.mod
go mod tidy
go build \
    -buildmode pie \
    -compiler gc \
    %{!?suse_version: -tags="rpm_crashtraceback ${BUILDTAGS:-}"} \
    -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')%{?__global_ldflags: -extldflags '%__global_ldflags'}" \
    -a -v


%install
# command
install -D -p -m 0755 caddy %{buildroot}%{_bindir}/caddy

# config
install -D -p -m 0644 %{S:1} %{buildroot}%{_sysconfdir}/caddy/Caddyfile

# systemd units
install -D -p -m 0644 %{S:2} %{buildroot}%{_unitdir}/caddy.service
install -D -p -m 0644 %{S:3} %{buildroot}%{_unitdir}/caddy-api.service

# data directory
install -d -m 0750 %{buildroot}%{_sharedstatedir}/caddy

# welcome page
install -D -p -m 0644 %{S:4} %{buildroot}%{_datadir}/caddy/index.html

# shell completion
install -D -p -m 0644 %{S:5} %{buildroot}%{_datadir}/bash-completion/completions/caddy
install -D -p -m 0644 %{S:6} %{buildroot}%{_datadir}/zsh/site-functions/_caddy


%pre
getent group caddy &> /dev/null || \
groupadd -r caddy &> /dev/null
getent passwd caddy &> /dev/null || \
useradd -r -g caddy -d %{_sharedstatedir}/caddy -s /sbin/nologin -c 'Caddy web server' caddy &> /dev/null
exit 0


%post
%systemd_post caddy.service

if [ -x /usr/sbin/getsebool ]; then
    # connect to ACME endpoint to request certificates
    setsebool -P httpd_can_network_connect on
fi
if [ -x /usr/sbin/semanage -a -x /usr/sbin/restorecon ]; then
    # file contexts
    semanage fcontext --add --type httpd_exec_t        '%{_bindir}/caddy'               2> /dev/null || :
    semanage fcontext --add --type httpd_sys_content_t '%{_datadir}/caddy(/.*)?'        2> /dev/null || :
    semanage fcontext --add --type httpd_config_t      '%{_sysconfdir}/caddy(/.*)?'     2> /dev/null || :
    semanage fcontext --add --type httpd_var_lib_t     '%{_sharedstatedir}/caddy(/.*)?' 2> /dev/null || :
    restorecon -r %{_bindir}/caddy %{_datadir}/caddy %{_sysconfdir}/caddy %{_sharedstatedir}/caddy || :
fi
if [ -x /usr/sbin/semanage ]; then
    # QUIC
    semanage port --add --type http_port_t --proto udp 80   2> /dev/null || :
    semanage port --add --type http_port_t --proto udp 443  2> /dev/null || :
    # admin endpoint
    semanage port --add --type http_port_t --proto tcp 2019 2> /dev/null || :
fi


%preun
%systemd_preun caddy.service


%postun
%systemd_postun_with_restart caddy.service

if [ $1 -eq 0 ]; then
    if [ -x /usr/sbin/getsebool ]; then
        # connect to ACME endpoint to request certificates
        setsebool -P httpd_can_network_connect off
    fi
    if [ -x /usr/sbin/semanage ]; then
        # file contexts
        semanage fcontext --delete --type httpd_exec_t        '%{_bindir}/caddy'               2> /dev/null || :
        semanage fcontext --delete --type httpd_sys_content_t '%{_datadir}/caddy(/.*)?'        2> /dev/null || :
        semanage fcontext --delete --type httpd_config_t      '%{_sysconfdir}/caddy(/.*)?'     2> /dev/null || :
        semanage fcontext --delete --type httpd_var_lib_t     '%{_sharedstatedir}/caddy(/.*)?' 2> /dev/null || :
        # QUIC
        semanage port     --delete --type http_port_t --proto udp 80   2> /dev/null || :
        semanage port     --delete --type http_port_t --proto udp 443  2> /dev/null || :
        # admin endpoint
        semanage port     --delete --type http_port_t --proto tcp 2019 2> /dev/null || :
    fi
fi


%files
%license LICENSE
%{_bindir}/caddy
%{_datadir}/caddy
%{_unitdir}/caddy.service
%{_unitdir}/caddy-api.service
%dir %{_sysconfdir}/caddy
%config(noreplace) %{_sysconfdir}/caddy/Caddyfile
%attr(0750,caddy,caddy) %dir %{_sharedstatedir}/caddy
# filesystem owns all the parent directories here
%{_datadir}/bash-completion/completions/caddy
# own parent directories in case zsh is not installed
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_caddy


%changelog
* Mon Nov 08 2021 Neal Gompa <ngompa13@gmail.com> - 2.4.6-1
- Latest upstream

* Tue Oct 26 2021 Carl George <carl@george.computer> - 2.4.5-1
- Latest upstream

* Thu Jun 17 2021 Carl George <carl@george.computer> - 2.4.3-1
- Latest upstream

* Sat Jun 12 2021 Carl George <carl@george.computer> - 2.4.2-1
- Latest upstream

* Fri May 21 2021 Carl George <carl@george.computer> - 2.4.1-1
- Latest upstream

* Tue May 11 2021 Carl George <carl@george.computer> - 2.4.0-1
- Latest upstream

* Mon Jan 18 2021 Carl George <carl@george.computer> - 2.3.0-1
- Latest upstream

* Fri Oct 30 2020 Carl George <carl@george.computer> - 2.2.1-1
- Latest upstream

* Sat Sep 26 2020 Carl George <carl@george.computer> - 2.2.0-1
- Latest upstream

* Sat Sep 19 2020 Carl George <carl@george.computer> - 2.2.0~rc3-1
- Latest upstream

* Wed Sep 09 2020 Neal Gompa <ngompa13@gmail.com> - 2.2.0~rc1-2
- Fix systemd build dependency for RHEL/CentOS

* Mon Aug 31 2020 Carl George <carl@george.computer> - 2.2.0~rc1-1
- Latest upstream
- Add bash and zsh completion support

* Wed Jul 08 2020 Neal Gompa <ngompa13@gmail.com> - 2.1.1-1
- Latest upstream

* Tue May 26 2020 Neal Gompa <ngompa13@gmail.com> - 2.0.0-2
- Adapt for SUSE distributions

* Wed May 06 2020 Neal Gompa <ngompa13@gmail.com> - 2.0.0-1
- Update to v2.0.0 final

* Sat Apr 18 2020 Carl George <carl@george.computer> - 2.0.0~rc3-1
- Latest upstream

* Sun Feb 02 2020 Carl George <carl@george.computer> - 2.0.0~beta13-1
- Latest upstream

* Mon Jan 06 2020 Carl George <carl@george.computer> - 2.0.0~beta12-1
- Update to beta12

* Tue Nov 19 2019 Carl George <carl@george.computer> - 2.0.0~beta10-1
- Update to beta10

* Wed Nov 06 2019 Carl George <carl@george.computer> - 2.0.0~beta9-1
- Update to beta9
- Use upstream main.go file

* Sun Nov 03 2019 Carl George <carl@george.computer> - 2.0.0~beta8-1
- Update to beta8

* Sat Oct 19 2019 Carl George <carl@george.computer> - 2.0.0~beta6-1
- Initial Caddy v2 package
