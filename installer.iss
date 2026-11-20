; Inno Setup script per l'installer di PhotoMatch
; Compilare con Inno Setup dopo `python -m PyInstaller build.spec`.
; La versione si puo' passare da riga di comando (usato dalla CI):
;   ISCC.exe /DMyAppVersion=0.3.0 installer.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.3.0"
#endif

[Setup]
AppName=PhotoMatch
AppVersion={#MyAppVersion}
AppPublisher=enkas79
DefaultDirName={autopf}\PhotoMatch
DefaultGroupName=PhotoMatch
OutputBaseFilename=PhotoMatch-{#MyAppVersion}-setup
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
