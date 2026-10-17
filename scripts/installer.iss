; Inno Setup script — compile on Windows with Inno Setup 6: ISCC scripts\installer.iss
[Setup]
AppName=ColorSnap Studio
AppVersion=1.0.0
DefaultDirName={autopf}\ColorSnapStudio
DefaultGroupName=ColorSnap Studio
OutputBaseFilename=ColorSnapStudio-Setup-1.0.0
Compression=lzma
SolidCompression=yes
[Files]
Source: "..\dist\ColorSnapStudio.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\ColorSnap Studio"; Filename: "{app}\ColorSnapStudio.exe"
Name: "{autodesktop}\ColorSnap Studio"; Filename: "{app}\ColorSnapStudio.exe"
