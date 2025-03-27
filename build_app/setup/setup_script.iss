[Setup]
; Información básica del instalador
AppName=Password Manager
AppVersion=1.0
DefaultDirName={pf}\PasswordManager
DefaultGroupName=Password Manager
OutputDir=.
OutputBaseFilename=PasswordManagerInstaller
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Incluye el ejecutable del lanzador y los archivos necesarios
Source: "dist\Launcher\Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\code\main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\code\password_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\code\password_manager.kv"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Crear accesos directos en el menú de inicio y escritorio
Name: "{group}\Password Manager"; Filename: "{app}\Launcher.exe"
Name: "{commondesktop}\Password Manager"; Filename: "{app}\Launcher.exe"; Tasks: desktopicon

[Tasks]
; Tareas opcionales durante la instalación
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Ejecuta la aplicación después de la instalación
Filename: "{app}\Launcher.exe"; Description: "{cm:LaunchProgram,Password Manager}"; Flags: nowait postinstall skipifsilent