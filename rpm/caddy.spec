%global debug_package %{nil}

Name:           caddy
Version:        2.7.5
Release:        1%{?dist}
Summary:        Web server with automatic HTTPS
License:        Apache-2.0
URL:            https://caddyserver.com

# In order to build Caddy with version information, we need to import it as a
# go module.  To do that, we are going to forgo the traditional source tarball
# and instead use just this file from upstream.  This method requires that we
# allow networking in the build environment.
Source0:        https://raw.githubusercontent.com/caddyserver/caddy/v%{version}/cmd/caddy/main.go
# Use official resources for config, unit file, and welcome page.
# https://github.com/caddyserver/dist
Source10:       https://raw.githubusercontent.com/caddyserver/dist/master/config/Caddyfile
Source20:       https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy.service
Source21:       https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy-api.service
Source22:       https://raw.githubusercontent.com/caddyserver/dist/master/init/caddy.sysusers
Source30:       https://raw.githubusercontent.com/caddyserver/dist/master/welcome/index.html
# Since we are not using a traditional source tarball, we need to explicitly
# pull in the license file.
Source90:       https://raw.githubusercontent.com/caddyserver/caddy/v%{version}/LICENSE

# https://github.com/caddyserver/caddy/commit/f45a6de20dd19e82e58c85b37e03957b2203b544
BuildRequires:  golang >= 1.20
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
cp %{S:0} %{S:90} .


%build
# https://pagure.io/go-rpm-macros/c/1cc7f5d9026175bb6cb1b8c889355d0c4fc0e40a
%undefine _auto_set_build_flags

# Fedora diverges from upstream Go by disabling the proxy server.  Some of
# Caddy's dependencies reference commits that are no longer upstream, but are
# cached in the proxy.  As long as we are downloading dependencies during the
# build, reset the behavior to prefer the proxy.  This also avoid having a
# build requirement on bzr.
# https://fedoraproject.org/wiki/Changes/golang1.13#Detailed_Description
export GOPROXY='https://proxy.golang.org,direct'

# As of 2023-08-03, golang 1.21 in Fedora Rawhide requires this environment
# variable to be set for the build to work correctly.
# https://github.com/golang/go/issues/60145#issuecomment-1547921152
export GOSUMDB='sum.golang.org'

go mod init caddy
echo "require github.com/caddyserver/caddy/v2 v%{version}" >> go.mod
go mod tidy
go build \
    -buildmode pie \
    -compiler gc \
    %{!?suse_version: -tags="rpm_crashtraceback ${BUILDTAGS:-}"} \
    -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')%{?__global_ldflags: -extldflags '%__global_ldflags'}" \
    -a -v -x


%install
# command
install -D -p -m 0755 caddy %{buildroot}%{_bindir}/caddy

# man pages
./caddy manpage --directory %{buildroot}%{_mandir}/man8

# config
install -D -p -m 0644 %{S:10} %{buildroot}%{_sysconfdir}/caddy/Caddyfile

# systemd units
install -D -p -m 0644 %{S:20} %{buildroot}%{_unitdir}/caddy.service
install -D -p -m 0644 %{S:21} %{buildroot}%{_unitdir}/caddy-api.service

# sysusers
install -D -p -m 0644 %{S:22} %{buildroot}%{_sysusersdir}/caddy.conf

# data directory
install -d -m 0750 %{buildroot}%{_sharedstatedir}/caddy

# welcome page
install -D -p -m 0644 %{S:30} %{buildroot}%{_datadir}/caddy/index.html

# shell completions
install -d -m 0755 %{buildroot}%{_datadir}/bash-completion/completions
./caddy completion bash > %{buildroot}%{_datadir}/bash-completion/completions/caddy
install -d -m 0755 %{buildroot}%{_datadir}/zsh/site-functions
./caddy completion zsh > %{buildroot}%{_datadir}/zsh/site-functions/_caddy
install -d -m 0755 %{buildroot}%{_datadir}/fish/vendor_completions.d
./caddy completion fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/caddy.fish


%pre
%if 0%{?el7}
%sysusers_create_compat %{S:22}
%else
%sysusers_create_package %{name} %{S:22}
%endif


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
%{_mandir}/man8/caddy*.8*
%{_datadir}/caddy
%{_unitdir}/caddy.service
%{_unitdir}/caddy-api.service
%{_sysusersdir}/caddy.conf
%dir %{_sysconfdir}/caddy
%config(noreplace) %{_sysconfdir}/caddy/Caddyfile
%attr(0750,caddy,caddy) %dir %{_sharedstatedir}/caddy
%{_datadir}/bash-completion/completions/caddy
%{_datadir}/zsh/site-functions/_caddy
%{_datadir}/fish/vendor_completions.d/caddy.fish
