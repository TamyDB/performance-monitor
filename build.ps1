param([string]$Video = "$PSScriptRoot\bad-apple.mp4")
$ErrorActionPreference = 'Stop'
& python "$PSScriptRoot\build.py" --video $Video
if ($LASTEXITCODE -ne 0) { throw 'Falha na compilação. Consulte a saída acima.' }
