@echo off
setlocal
set ROOT=%~dp0

where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%ROOT%tools\nova_cli.ud" %*
) else (
  python "%ROOT%tools\nova_cli.ud" %*
)

exit /b %errorlevel%
