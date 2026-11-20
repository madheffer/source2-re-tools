$S = $PSScriptRoot
# Visual Studio with the C++ tools, found by vswhere (VCVARS64 overrides: the full path to vcvars64.bat)
$vc = $env:VCVARS64
if (-not $vc) {
  $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
  $vs = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
  $vc = Join-Path $vs "VC\Auxiliary\Build\vcvars64.bat"
}
cmd /c "`"$vc`" >nul 2>&1 && cd /d `"$S`" && cl /nologo /O2 /EHsc /DUSE_SSE /DWIN32 /I hs atitest.cpp xcodec23.cpp /Fe:atitest.exe 2>&1" | Select-String -Pattern "error" | Select-Object -First 25
