The shell completion scripts are generated using the tool [@completely/cli](https://github.com/fvictorio/completely). The `caddy.json` file contains the spec of the caddy command. The shell completion scripts are generated based on the spec as defined in the JSON file.

## How

- Install `completely`
	- yarn: `yarn global add @completely/cli`
	- npm: `npm i -g @completely/cli`

- Run `./generate.sh`

- Place the generated files in the designated directories:
	- bash: `mv bash-completion /etc/bash_completion.d/caddy`
	- zsh: `fpath=(/path/to/completion/script/dir $fpath)`
