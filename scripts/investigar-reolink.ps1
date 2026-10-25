# investigar-reolink.ps1
#
# Investigación de SOLO LECTURA de una cámara Reolink para MeteoCam.
# Ejecuta únicamente comandos Get... de la API HTTP de Reolink y guarda todas
# las respuestas en un JSON. No mueve la cámara ni cambia ninguna configuración.
#
# Credenciales: se leen de publisher.json (no se escriben en ningún sitio).
# Resultado: C:\ProgramData\MeteoCam\investigacion\reolink-<fecha>.json, con la
# contraseña y el token sustituidos por [OCULTO].
#
# Uso (PowerShell como administrador):
#   powershell -ExecutionPolicy Bypass -File investigar-reolink.ps1
#
# Ver docs/catalogo-comandos-reolink.md.

param(
    [string]$Config = "$env:ProgramData\MeteoCam\publisher.json",
    [string]$Salida = "$env:ProgramData\MeteoCam\investigacion",
    [int[]]$Canales = @(0, 1)
)

$ErrorActionPreference = "Stop"

$cfg = Get-Content $Config -Raw -Encoding UTF8 | ConvertFrom-Json
$camara = $cfg.camera_host
$usuario = $cfg.camera_username
$clave = $cfg.camera_password

New-Item -ItemType Directory -Force $Salida | Out-Null

function Invocar([string]$Base, [string]$Cmd, $Param, [string]$Token, [int]$Accion = 0) {
    $url = "${Base}?cmd=$Cmd"
    if ($Token) { $url += "&token=$Token" }
    $orden = [ordered]@{ cmd = $Cmd; action = $Accion; param = $Param }
    $cuerpo = ConvertTo-Json -InputObject @($orden) -Depth 20 -Compress
    $respuesta = Invoke-RestMethod -Uri $url -Method Post -Body $cuerpo `
        -ContentType "application/json" -TimeoutSec 20
    return @($respuesta)[0]
}

# 1. Localizar la API e iniciar sesión.
$login = @{ User = @{ Version = "0"; userName = $usuario; password = $clave } }
$base = $null
$token = $null
foreach ($ruta in @("/cgi-bin/api.cgi", "/api.cgi")) {
    $candidata = "http://$camara$ruta"
    try {
        $r = Invocar $candidata "Login" $login $null
        if ($r.code -eq 0) {
            $base = $candidata
            $token = $r.value.Token.name
            break
        }
        Write-Host "Login en $candidata respondió code=$($r.code): $($r.error.detail)"
    } catch {
        Write-Host "Sin respuesta en $candidata ($($_.Exception.Message))"
    }
}
if (-not $token) {
    Write-Host "ERROR: no se pudo iniciar sesión en la cámara $camara." -ForegroundColor Red
    Write-Host "Comprueba que la web http://$camara abre y que HTTP está activo en la cámara."
    exit 1
}
Write-Host "Sesión iniciada en $base" -ForegroundColor Green

# 2. Comandos de lectura.
$globales = @(
    @{ cmd = "GetDevInfo";       param = @{} },
    @{ cmd = "GetDevName";       param = @{ channel = 0 } },
    @{ cmd = "GetChannelstatus"; param = @{} },
    @{ cmd = "GetAbility";       param = @{ User = @{ userName = "" } } },
    @{ cmd = "GetTime";          param = @{} },
    @{ cmd = "GetNtp";           param = @{} },
    @{ cmd = "GetHddInfo";       param = @{} },
    @{ cmd = "GetAutoMaint";     param = @{} },
    @{ cmd = "GetAutoUpgrade";   param = @{} },
    @{ cmd = "GetLocalLink";     param = @{} },
    @{ cmd = "GetNetPort";       param = @{} },
    @{ cmd = "GetUpnp";          param = @{} },
    @{ cmd = "GetP2p";           param = @{} },
    @{ cmd = "GetOnline";        param = @{} },
    @{ cmd = "GetUser";          param = @{} },
    @{ cmd = "GetSysCfg";        param = @{} }
)
$porCanal = @(
    "GetEnc", "GetIsp", "GetImage", "GetOsd", "GetMask", "GetStitch",
    "GetPtzPreset", "GetPtzPatrol", "GetPtzGuard", "GetZoomFocus", "GetAutoFocus",
    "GetPtzCheckState", "GetIrLights", "GetWhiteLed", "GetPowerLed",
    "GetRec", "GetRecV20", "GetMdState", "GetAiState", "GetRtspUrl"
)

$resultados = [ordered]@{}
$resumen = @()

function Registrar([string]$Clave, [string]$Cmd, $Param) {
    try {
        # action=1: devuelve también rangos y valores iniciales.
        $r = Invocar $base $Cmd $Param $token 1
        $script:resultados[$Clave] = $r
        if ($r.code -eq 0) { $estado = "OK" }
        else { $estado = "code=$($r.code) $($r.error.rspCode) $($r.error.detail)" }
    } catch {
        $script:resultados[$Clave] = @{ excepcion = $_.Exception.Message }
        $estado = "EXCEPCION: $($_.Exception.Message)"
    }
    $script:resumen += [pscustomobject]@{ Comando = $Clave; Resultado = $estado }
}

foreach ($g in $globales) { Registrar $g.cmd $g.cmd $g.param }
foreach ($canal in $Canales) {
    foreach ($cmd in $porCanal) { Registrar "${cmd} (canal $canal)" $cmd @{ channel = $canal } }
}

# 3. Cerrar sesión.
try { Invocar $base "Logout" @{} $token | Out-Null } catch { }

# 4. Guardar sin secretos.
$texto = ConvertTo-Json -InputObject $resultados -Depth 20
foreach ($secreto in @($clave, [uri]::EscapeDataString($clave), $token)) {
    if ($secreto) { $texto = $texto.Replace($secreto, "[OCULTO]") }
}
$archivo = Join-Path $Salida ("reolink-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".json")
[System.IO.File]::WriteAllText($archivo, $texto, (New-Object System.Text.UTF8Encoding $false))

$resumen | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
Write-Host "Resultado guardado en: $archivo" -ForegroundColor Green

# Fin archivo: scripts/investigar-reolink.ps1
