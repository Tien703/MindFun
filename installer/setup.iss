; Mindfun Installer — Inno Setup Script
; Builds MindfunSetup.exe from PyInstaller output

#define MyAppName "Mindfun"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Mindfun Open Source"
#define MyAppURL "https://github.com/mindfun"
#define MyAppExeName "mindfun.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=MindfunSetup-v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\icon.ico
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main executable (PyInstaller output)
Source: "..\dist\mindfun.exe"; DestDir: "{app}"; Flags: ignoreversion
; Icon
Source: "..\assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\icon.png"; DestDir: "{app}"; Flags: ignoreversion
; Default data files
Source: "..\data\config.json"; DestDir: "{userappdata}\Mindfun"; Flags: onlyifdoesntexist
Source: "..\data\questions.json"; DestDir: "{userappdata}\Mindfun"; Flags: onlyifdoesntexist
Source: "..\data\game_presets.json"; DestDir: "{userappdata}\Mindfun"; Flags: onlyifdoesntexist
Source: "..\data\report.json"; DestDir: "{userappdata}\Mindfun"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName} Settings"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
; Start Mindfun Settings after install
Filename: "{app}\{#MyAppExeName}"; Parameters: "--settings"; Description: "Launch Mindfun Settings"; Flags: nowait postinstall skipifsilent

[Registry]
; Auto-start main app
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Mindfun"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue

[UninstallRun]
; Kill any running instances
Filename: "taskkill"; Parameters: "/f /im mindfun.exe"; Flags: runhidden

[UninstallDelete]
; Clean up PID files
Type: files; Name: "{userappdata}\Mindfun\.main_pid"
Type: files; Name: "{userappdata}\Mindfun\.watchdog_pid"
; Clean up log files
Type: filesandordirs; Name: "{userappdata}\Mindfun\logs"

[Code]
// Ask user if they want to keep their settings on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Do you want to keep your Mindfun settings and logs?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      DelTree(ExpandConstant('{userappdata}\Mindfun'), True, True, True);
    end;
  end;
end;
