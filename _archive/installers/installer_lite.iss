; Inno Setup Script for M3U Matrix Pro - LITE Package
; Minimal installation without sample playlists, optimized for size

#define MyAppName "M3U Matrix Pro Lite"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Liberty Express"
#define MyAppExeName "M3U_Matrix_Pro.exe"
#define MyAppIcon "logo.ico"

[Setup]
AppId={{F9C5B6D4-2E3G-5F0C-9D8B-7G6E5F4D3C2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installers
OutputBaseFilename=M3U_Matrix_Pro_Setup_v{#MyAppVersion}_LITE
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startmenu"; Description: "Create Start Menu shortcut"; GroupDescription: "Shortcuts:";

[Files]
; Main executable and dependencies ONLY
Source: "dist\M3U_Matrix_Pro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Templates (critical for page generation)
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data files
Source: "src\data\rumble_channels.json"; DestDir: "{app}\src\data"; Flags: ignoreversion

; Minimal documentation
Source: "M3U_MATRIX_README.md"; DestDir: "{app}"; Flags: ignoreversion

; Icon
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Sample Playlists NOT included in LITE version

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: startmenu
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu

; Desktop shortcut (optional)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Run]
; Launch app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
{ Taskbar Pinning Code - Best-effort attempt (Windows 10/11) }
const
  SHELL32_STRING_ID_PIN_TO_TASKBAR = 5386;

function PinToTaskbar(const Filename: string): Boolean;
var
  Shell: Variant;
  Folder: Variant;
  Item: Variant;
  Verb: Variant;
  i: Integer;
begin
  Result := False;
  try
    Shell := CreateOleObject('Shell.Application');
    Folder := Shell.NameSpace(ExtractFileDir(Filename));
    Item := Folder.ParseName(ExtractFileName(Filename));
    
    for i := 0 to Item.Verbs.Count - 1 do
    begin
      Verb := Item.Verbs.Item(i);
      // Look for taskbar pin verb
      if (Pos('taskbar', LowerCase(Verb.Name)) > 0) or 
         (Pos('pin', LowerCase(Verb.Name)) > 0) then
      begin
        Verb.DoIt;
        Result := True;
        Exit;
      end;
    end;
  except
    // Silent fail - taskbar pinning is optional
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Attempt to pin to taskbar (may require user confirmation on Win11)
    PinToTaskbar(ExpandConstant('{app}\{#MyAppExeName}'));
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\generated_pages"
Type: filesandordirs; Name: "{app}\src\videos\logs"
Type: filesandordirs; Name: "{app}\src\videos\m3u"
