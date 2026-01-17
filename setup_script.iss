; Script generated for ReFlow Studio v0.3.1
; SPLIT INSTALLER VERSION (Disk Spanning Enabled)

#define MyAppName "ReFlow Studio"
#define MyAppVersion "0.3.1"
#define MyAppPublisher "ReFlow AI"
#define MyAppExeName "ReFlowStudio.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=ReFlow_Setup_v0.3.1
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

; --- DISK SPANNING (Splits the 5GB file) ---
DiskSpanning=yes
DiskSliceSize=1500000000 
; Creates setup.exe, setup-1.bin, etc. (1.5GB chunks)

WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Ensure you did the 'Manual Copy' of models/ffmpeg before running this!
Source: "dist\ReFlowStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent