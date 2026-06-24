$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 "$Root\tools\nova_cli.ud" @args
} else {
    python "$Root\tools\nova_cli.ud" @args
}

exit $LASTEXITCODE
