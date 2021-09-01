package manpages

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"text/template"
	"time"

	"github.com/caddyserver/caddy/v2"
	caddycmd "github.com/caddyserver/caddy/v2/cmd"
)

func init() {

	caddy.RegisterModule(Manpages{})

	caddycmd.RegisterCommand(caddycmd.Command{
		Name:  "man",
		Func:  cmdMan,
		Short: "Print manual pages for Caddy",
		Long: `
Creates subfolder "man" in current directory and prints manual pages for Caddy and its available subcommands into.
`,
	})
}

type Manpages struct {
}

func (Manpages) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "caddy.manpages",
		New: func() caddy.Module { return new(Manpages) },
	}
}

func cmdMan(fl caddycmd.Flags) (int, error) {

	// Macros to be evaluated by template parser
	type Macro struct {
		App     string
		Name    string
		Date    string
		Long    string
		Title   string
		Short   string
		Usage   string
		Version string
		Flags   []*flag.Flag
		Other   []caddycmd.Command
	}

	const DateFormat = "January 2006"

	// Template passed to Template.Parse()
	// - Paragraphs with macros that might return `nil`
	//   are enclosed in {{ if . }}-conditions
	// - {{ if ne .Name .App }} and {{ if eq .Name .App }} check weither
	//   current command is os.Args[0] or a subcommand
	// - TODO: Possible arguments to flags, like <string> or <path>, are documented
	//   in paragraph SYNOPSIS, but not yet for each flag in paragraph OPTIONS
	const manpageTemplate = `.TH "{{ toUpper .Title }}" "1" "{{ .Date }}"
.SH NAME
.HP
{{ .Title }} \- {{ .Short }}
.SH SYNOPSIS
.HP
{{ .App }} {{if ne .Name .App}}{{ .Name }} {{ end }}{{ .Usage }}{{ if .Long }}
.SH DESCRIPTION
.PP
{{ .Long }}{{ end }}
{{ if .Flags}}.SH OPTIONS{{ range .Flags }}
.HP
\fB--{{ .Name }}\fR
.RS
{{ .Usage }}
.RE{{ end }}{{ end }}{{ if eq .Name .App }}
.SH COMMANDS
.PP
These are available commands to use with caddy.
See their manpages for usage and available flags.{{ range .Other }}
.HP
\fB{{ .Name }}\fR
.RS
{{ .Short }}. See \fBcaddy-{{ .Name }}\fR(1)
.RE{{ end }}{{ end }}{{if ne .Name .App}}
.SH SEE ALSO
.PP
{{ range .Other }}\fBcaddy-{{ .Name }}\fR(1), {{ end }}\fBcaddy\fR(1){{ end }}
.SH DOCUMENTATION
.HP
Full documentation is available at: https://caddyserver.com/docs/
.SH VERSION
.HP
{{ .Version }}
.SH BUGS
.HP
Report Bugs to: https://github.com/caddyserver/caddy
.SH COPYRIGHT
.HP
(c) Matthew Holt and The Caddy Authors`

	// Create dummy function for os.Args[0]
	cmdCaddy := caddycmd.Command{
		Name:  os.Args[0],
		Short: "an extensible server platform",
		Usage: "<command> [<args...>]",
	}

	// Get list of subcommands
	commands := caddycmd.Commands()

	// Abort if os.Args[0] matches the name of a registered subcommand
	if _, exists := commands[cmdCaddy.Name]; exists {
		return caddy.ExitCodeFailedStartup,
			errors.New("Main command is named similar as subcommand: " + cmdCaddy.Name + "\nAborting")
	}

	// Create dummy commands list and append dummy function for os.Args[0]
	all := commands
	all[cmdCaddy.Name] = cmdCaddy

	// Create "man" subdirectory in current directory
	curDir, err := os.Getwd()
	if err != nil {
		return caddy.ExitCodeFailedStartup, err
	}
	manDir := filepath.Join(curDir, "man")
	err = os.MkdirAll(manDir, 0775)
	if err != nil {
		return caddy.ExitCodeFailedStartup, err
	}

	fmt.Printf("Printing manual pages for " + os.Args[0] + " into " + manDir + "...\n")

	// Iterate through dummy command list
	for _, cmd := range all {
		// Allocate macros to be passed to the template parser
		m := Macro{
			App:     os.Args[0],
			Name:    cmd.Name,
			Date:    time.Now().Format(DateFormat),
			Long:    strings.TrimSuffix(strings.TrimPrefix(cmd.Long, "\n"), "\n"),
			Short:   strings.TrimSuffix(cmd.Short, "."),
			Usage:   cmd.Usage,
			Version: caddycmd.CaddyVersion(),
		}

		// Title of man page will be be os.Args[0]-subcommand
		// except for os.Args[0] itself
		if m.Name == m.App {
			m.Title = m.App
		} else {
			m.Title = m.App + "-" + m.Name
		}

		// Collect available cli flags for command
		if cmd.Flags != nil {
			cmd.Flags.VisitAll(func(f *flag.Flag) {
				m.Flags = append(m.Flags, f)
			})
		}

		// Collect list of "other" subcommands then itself
		keys := make([]string, 0, len(commands))
		for k := range commands {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		for _, k := range keys {
			if k != m.Name {
				m.Other = append(m.Other, commands[k])
			}
		}

		// Create file
		output := m.Title + ".1"
		f, err := os.Create(filepath.Join(manDir, output))
		if err != nil {
			return caddy.ExitCodeFailedStartup, err
		}

		// Initialize template
		t := template.New(output)

		// Make toUpper function available to template parser
		t = t.Funcs(template.FuncMap{"toUpper": strings.ToUpper})

		// Parse template
		t, err = t.Parse(manpageTemplate)
		if err != nil {
			return caddy.ExitCodeFailedStartup, err
		}

		// Write template into file
		err = t.Execute(f, m)
		if err != nil {
			return caddy.ExitCodeFailedStartup, err
		}
	}
	fmt.Printf("Done.\nTo inspect a files content as rendered manual page, use 'nroff -man <manpage>.1' or a similar text formatter\n")
	return caddy.ExitCodeSuccess, nil
}
