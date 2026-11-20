; Inno Setup script per l'installer di PhotoMatch
; Compilare con Inno Setup dopo `python -m PyInstaller build.spec`
; (per exe singolo serve anche l'installer per l'autoupdate)

[Setup]
AppName=PhotoMatch
AppVersion=0.2.0
AppPublisher=enkas79
DefaultDirName={autopf}\PhotoMatch
DefaultGroupName=PhotoMatch
OutputBaseFilename=PhotoMatch-0.2.0-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\PhotoMatch.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PhotoMatch"; Filename: "{app}\PhotoMatch.exe"
Name: "{commondesktop}\PhotoMatch"; Filename: "{app}\PhotoMatch.exe"

[Tasks]
Name: "desktopicon"; Description: "Crea icona sul desktop"; GroupDescription: "Icone:"

[Run]
Filename: "{app}\PhotoMatch.exe"; Description: "Avvia PhotoMatch"; Flags: nowait postinstall skipifsilent
