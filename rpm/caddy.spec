# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0

Name:           caddy
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_versioning_prereleases_with_tilde
Version:        2.0.0~beta6
%global tag     v2.0.0-beta6
Release:        1%{?dist}
Summary:        HTTP/2 web server with automatic HTTPS
License:        ASL 2.0
URL:            https://caddyserver.com

# In order to build Caddy with version information, we need to import it as a
# go module.  To do that, we are going to forgo the traditional source tarball
# and instead use this simple go file.  This method requires that we allow
# networking in the build environment.
Source0:        main.go
# Use official resources for config, unit file, and welcome page.
# https://github.com/caddyserver/dist
Source1:        https://raw.githubusercontent.com/caddyserver/dist/master/config/Caddyfile
Source2:        https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy.service
Source3:        https://raw.githubusercontent.com/caddyserver/dist/master/welcome/index.html
# Since we are not using a traditional source tarball, we need to explicitly
# pull in the license file.
Source4:        https://raw.githubusercontent.com/caddyserver/caddy/%{tag}/LICENSE

BuildRequires:  golang >= 1.13
BuildRequires:  git-core
BuildRequires:  systemd
%{?systemd_requires}
Provides:       webserver


%description
Caddy is the HTTP/2 web server with automatic HTTPS.


%prep
%setup -q -c -T
# Copy main.go and LICENSE into the build directory.
cp %{S:0} %{S:4} .


%build
go mod init caddy
echo "require github.com/caddyserver/caddy/v2 %{tag}" >> go.mod
go build \
    -buildmode pie \
    -compiler gc \
    -tags="rpm_crashtraceback ${BUILDTAGS:-}" \
    -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') -extldflags '%__global_ldflags'" \
    -a -v


%install
install -D -m 0755 caddy %{buildroot}%{_bindir}/caddy
install -D -m 0644 %{S:1} %{buildroot}%{_sysconfdir}/caddy/Caddyfile
install -D -m 0644 %{S:2} %{buildroot}%{_unitdir}/caddy.service
install -D -m 0644 %{S:3} %{buildroot}%{_datadir}/caddy/index.html
install -d -m 0750 %{buildroot}%{_sharedstatedir}/caddy


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
%dir %{_sysconfdir}/caddy
%config(noreplace) %{_sysconfdir}/caddy/Caddyfile
%attr(0750,caddy,caddy) %dir %{_sharedstatedir}/caddy


%changelog
* Sat Oct 19 2019 Carl George <carl@george.computer> - 2.0.0~beta6-1
- Initial Caddy v2 package
