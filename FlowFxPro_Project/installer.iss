[Setup]
AppName=FlowFx Pro
AppVersion=1.0
AppPublisher=FlowFx
DefaultDirName={autopf}\FlowFxPro
DefaultGroupName=FlowFx Pro
OutputBaseFilename=FlowFxPro_Setup
PrivilegesRequired=admin
Compression=lzma2
SolidCompression=yes
UninstallDisplayName=FlowFx Pro
[Files]
Source: "dist\FlowFxPro.exe"; DestDir: "{app}"
Source: "dist\ffmpeg.exe"; DestDir: "{app}"
Source: "dist\ffprobe.exe"; DestDir: "{app}"
[Icons]
Name: "{autodesktop}\FlowFx Pro"; Filename: "{app}\FlowFxPro.exe"
Name: "{group}\FlowFx Pro"; Filename: "{app}\FlowFxPro.exe"
[Run]
Filename: "{app}\FlowFxPro.exe"; Description: "Launch FlowFx Pro"; Flags: nowait postinstall skipifsilent
