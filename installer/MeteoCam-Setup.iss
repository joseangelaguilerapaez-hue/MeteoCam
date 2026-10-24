; MeteoCam-Setup.iss
;
; Instalador del servicio MeteoCam Publisher para el mini PC de la estación.
; Lo compila GitHub Actions (.github/workflows/instalador.yml) a partir de la
; carpeta dist\MeteoCamPublisher que genera PyInstaller.
;
; Configuración privada (credenciales de la cámara):
;   - Si junto a MeteoCam-Setup.exe hay un publisher.json, se copia tal cual a
;     C:\ProgramData\MeteoCam\publisher.json y no se pregunta nada.
;   - Si no lo hay pero ya existe en ProgramData (reinstalación), se conserva.
;   - Si no hay ninguno, el asistente pide los datos y crea el archivo.
;   En todos los casos el archivo queda legible solo por SYSTEM y Administradores.
;   Las credenciales nunca forman parte del instalador ni del repositorio.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define ServiceName "MeteoCamPublisher"
#define ServiceExe "MeteoCamPublisher.exe"

[Setup]
AppId={{8F3C2A51-6B4E-4D2A-9C1F-3E7A5B9D2C10}
AppName=MeteoCam Publisher
AppVersion={#AppVersion}
AppPublisher=MeteoArchidona
DefaultDirName={autopf}\MeteoCam\Publisher
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist-installer
OutputBaseFilename=MeteoCam-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=MeteoCam Publisher
SetupLogging=yes

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Dirs]
Name: "{commonappdata}\MeteoCam"
Name: "{commonappdata}\MeteoCam\logs"

[Files]
Source: "..\dist\MeteoCamPublisher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; publisher.json junto al instalador (por ejemplo, en el pendrive).
Source: "{src}\publisher.json"; DestDir: "{commonappdata}\MeteoCam"; Flags: external skipifsourcedoesntexist ignoreversion

[UninstallRun]
Filename: "{sys}\net.exe"; Parameters: "stop {#ServiceName}"; Flags: runhidden waituntilterminated; RunOnceId: "DetenerServicio"
Filename: "{app}\{#ServiceExe}"; Parameters: "remove"; Flags: runhidden waituntilterminated; RunOnceId: "QuitarServicio"

[Code]
var
  DatosPage: TInputQueryWizardPage;

function RutaConfig(): String;
begin
  Result := ExpandConstant('{commonappdata}\MeteoCam\publisher.json');
end;

function HayConfigJuntoAlInstalador(): Boolean;
begin
  Result := FileExists(ExpandConstant('{src}\publisher.json'));
end;

function ServicioExiste(): Boolean;
var
  Codigo: Integer;
begin
  Result := Exec(ExpandConstant('{sys}\sc.exe'), 'query {#ServiceName}', '',
    SW_HIDE, ewWaitUntilTerminated, Codigo) and (Codigo = 0);
end;

procedure InitializeWizard();
begin
  DatosPage := CreateInputQueryPage(wpWelcome,
    'Datos de la cámara',
    'No se ha encontrado publisher.json junto al instalador.',
    'Escribe los datos de conexión. Se guardarán solo en este equipo, en ' +
    'C:\ProgramData\MeteoCam\publisher.json, legible únicamente por el sistema ' +
    'y los administradores.');
  DatosPage.Add('IP de la cámara:', False);
  DatosPage.Add('Usuario de la cámara:', False);
  DatosPage.Add('Contraseña de la cámara:', True);
  DatosPage.Add('IP del VPS:', False);
  DatosPage.Values[0] := '192.168.1.100';
  DatosPage.Values[1] := 'admin';
  DatosPage.Values[3] := '187.124.114.42';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = DatosPage.ID) and
    (HayConfigJuntoAlInstalador() or FileExists(RutaConfig()));
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  I: Integer;
begin
  Result := True;
  if CurPageID = DatosPage.ID then
    for I := 0 to 3 do
      if Trim(DatosPage.Values[I]) = '' then
      begin
        MsgBox('Rellena todos los datos de la cámara y del VPS.', mbError, MB_OK);
        Result := False;
        Exit;
      end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  Codigo: Integer;
begin
  Result := '';
  { Actualización: parar el servicio antes de sustituir sus archivos. }
  if ServicioExiste() then
    Exec(ExpandConstant('{sys}\net.exe'), 'stop {#ServiceName}', '',
      SW_HIDE, ewWaitUntilTerminated, Codigo);
end;

function JsonTexto(const Valor: String): String;
begin
  Result := Valor;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
  Result := '"' + Result + '"';
end;

procedure EscribirConfigDesdeAsistente();
var
  Lineas: TArrayOfString;
begin
  SetArrayLength(Lineas, 6);
  Lineas[0] := '{';
  Lineas[1] := '  "camera_host": ' + JsonTexto(Trim(DatosPage.Values[0])) + ',';
  Lineas[2] := '  "camera_username": ' + JsonTexto(Trim(DatosPage.Values[1])) + ',';
  Lineas[3] := '  "camera_password": ' + JsonTexto(DatosPage.Values[2]) + ',';
  Lineas[4] := '  "vps_host": ' + JsonTexto(Trim(DatosPage.Values[3]));
  Lineas[5] := '}';
  SaveStringsToUTF8File(RutaConfig(), Lineas, False);
end;

procedure Ejecutar(const Programa, Parametros, Descripcion: String);
var
  Codigo: Integer;
begin
  if not Exec(Programa, Parametros, '', SW_HIDE, ewWaitUntilTerminated, Codigo)
     or (Codigo <> 0) then
    Log(Format('Aviso: %s terminó con código %d', [Descripcion, Codigo]))
  else
    Log(Format('OK: %s', [Descripcion]));
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Exe, Sc: String;
  Codigo: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;

  if not FileExists(RutaConfig()) then
    EscribirConfigDesdeAsistente();

  { Solo SYSTEM (S-1-5-18) y Administradores (S-1-5-32-544) pueden leerla. }
  Ejecutar(ExpandConstant('{sys}\icacls.exe'),
    '"' + RutaConfig() + '" /inheritance:r /grant:r *S-1-5-18:F *S-1-5-32-544:F',
    'proteger publisher.json');

  Exe := ExpandConstant('{app}\{#ServiceExe}');
  Sc := ExpandConstant('{sys}\sc.exe');

  if ServicioExiste() then
    Ejecutar(Exe, '--startup auto update', 'actualizar servicio')
  else
    Ejecutar(Exe, '--startup auto install', 'instalar servicio');

  { Si se cae, Windows lo relanza a los 10 s, 30 s y 60 s. }
  Ejecutar(Sc, 'failure {#ServiceName} reset= 86400 actions= restart/10000/restart/30000/restart/60000',
    'configurar recuperación');
  Ejecutar(Sc, 'failureflag {#ServiceName} 1', 'activar recuperación ante errores');

  if not Exec(Exe, 'start', '', SW_HIDE, ewWaitUntilTerminated, Codigo) or (Codigo <> 0) then
    MsgBox('El servicio se ha instalado, pero no ha arrancado.' + #13#10 +
      'Revisa el registro en C:\ProgramData\MeteoCam\logs\publisher.log',
      mbError, MB_OK);
end;

// Fin archivo: installer/MeteoCam-Setup.iss
