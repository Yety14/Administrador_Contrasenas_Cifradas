[Setup]
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
; Python embebido base (sin site-packages)
Source: "..\python-3.11.9-embed-amd64\*"; DestDir: "{app}\Python";  Flags: ignoreversion recursesubdirs
Source: "..\..\dist\Launcher\Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion

; ----- Dependencias principales -----    Excludes: "Lib\site-packages\*";
; Cryptography y dependencias obligatorias
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\cryptography\*"; DestDir: "{app}\Python\Lib\site-packages\cryptography"; Flags: ignoreversion recursesubdirs
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\cffi\*"; DestDir: "{app}\Python\Lib\site-packages\cffi"; Flags: ignoreversion recursesubdirs
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\pycparser\*"; DestDir: "{app}\Python\Lib\site-packages\pycparser"; Flags: ignoreversion recursesubdirs

; Kivy y dependencias esenciales
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\kivy\*"; DestDir: "{app}\Python\Lib\site-packages\kivy"; Flags: ignoreversion recursesubdirs
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\certifi\*"; DestDir: "{app}\Python\Lib\site-packages\certifi"; Flags: ignoreversion recursesubdirs

; ----- Metadatos específicos -----
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\cryptography-*.dist-info\*"; DestDir: "{app}\Python\Lib\site-packages"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
;Source: "..\python-3.11.9-embed-amd64\Lib\site-packages\kivy-*.dist-info\*"; DestDir: "{app}\Python\Lib\site-packages"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist

; ----- Archivos críticos del sistema -----
;Source: "..\python-3.11.9-embed-amd64\python311._pth"; DestDir: "{app}\Python"; Flags: ignoreversion

[Icons]
Name: "{group}\Password Manager"; Filename: "{app}\Launcher.exe"
Name: "{commondesktop}\Password Manager"; Filename: "{app}\Launcher.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\Launcher.exe"; Description: "{cm:LaunchProgram,Password Manager}"; Flags: nowait postinstall skipifsilent
