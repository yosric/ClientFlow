; ===============================================
; ClientFlow Installer – SAFE UPDATE READY
; ===============================================

#define MyAppName "ClientFlow"
#define MyAppVersion "1.3.1"
#define MyAppPublisher "Yosri Saadi"
#define MyAppExeName "ClientFlowApp.exe"

[Setup]
AppId={{C5529200-3941-4316-85A0-F49C7DC7D560}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

UninstallDisplayIcon={app}\{#MyAppExeName}

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableProgramGroupPage=yes
WizardStyle=modern
SolidCompression=yes
Compression=lzma

CloseApplications=yes
CloseApplicationsFilter={#MyAppExeName}

OutputBaseFilename=ClientFlow_Setup_{#MyAppVersion}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; ===============================================
; DATA SAFETY — NEVER DELETE USER DATA
; ===============================================
[Dirs]
Name: "{userappdata}\ClientFlow"; Flags: uninsneveruninstall

; ===============================================
; FILES (Main Application)
; ===============================================
[Files]
Source: "C:\Users\saadi\OneDrive\Desktop\Clients\dist\ClientFlowApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; ===============================================
; SHORTCUTS
; ===============================================
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ===============================================
; RUN AFTER INSTALL
; ===============================================
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
