/** @file
  UniXNULib internal definitions.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#ifndef UNIXNU_INTERNAL_H_
#define UNIXNU_INTERNAL_H_

#include <Uefi.h>
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/UniXNULib.h>
#include <Library/DebugLib.h>
#include <Library/DevicePathLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/PcdLib.h>
#include <Library/PrintLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Protocol/GraphicsOutput.h>
#include <Protocol/UniXNUMenuPlugin.h>
#include <Protocol/UniXNULoader.h>
#include <Protocol/LoadedImage.h>
#include <Protocol/SimpleFileSystem.h>
#include <Protocol/SimpleTextIn.h>
#include <Protocol/SimpleTextOut.h>

#define UNIXNU_VERSION_STRING  "0.1.0"

//
// Schema version understood by this build (`version = N` in the config,
// `schema = N` in a kit manifest).
//
#define UNIXNU_SCHEMA_VERSION  1

// ---------------------------------------------------------------------------
// Logging. Every line goes to DEBUG() and, when the platform exposes one, to
// the first EFI_SERIAL_IO_PROTOCOL instance. Lines are prefixed "UNIXNU: "
// so test harnesses can grep for them.
// ---------------------------------------------------------------------------

VOID
UniXNULogInit (
  VOID
  );

VOID
EFIAPI
UniXNULog (
  IN CONST CHAR8  *Format,
  ...
  );

// ---------------------------------------------------------------------------
// TOML subset (Toml.c)
// ---------------------------------------------------------------------------

typedef enum {
  TomlString,
  TomlInteger,
  TomlBoolean,
  TomlArray,
  TomlTable
} TOML_TYPE;

typedef struct TOML_NODE TOML_NODE;

struct TOML_NODE {
  TOML_TYPE    Type;
  CHAR8        *Key;        ///< Member name inside a table; NULL for array items.
  UINTN        Line;        ///< Source line, for diagnostics.
  CHAR8        *String;
  INT64        Integer;
  BOOLEAN      Boolean;
  BOOLEAN      Defined;     ///< Table was opened by an explicit [header].
  BOOLEAN      TableArray;  ///< Array created by [[header]].
  TOML_NODE    *Child;      ///< First member / item.
  TOML_NODE    *LastChild;
  TOML_NODE    *Next;
};

/**
  Parse TOML text. On failure *Root is NULL and ErrorBuffer holds a message.
**/
EFI_STATUS
TomlParse (
  IN  CONST CHAR8  *Text,
  IN  UINTN        Length,
  OUT TOML_NODE    **Root,
  OUT CHAR8        *ErrorBuffer,
  IN  UINTN        ErrorBufferSize
  );

VOID
TomlFree (
  IN TOML_NODE  *Node
  );

TOML_NODE *
TomlGet (
  IN TOML_NODE    *Table,
  IN CONST CHAR8  *Key
  );

CONST CHAR8 *
TomlGetString (
  IN TOML_NODE    *Table,
  IN CONST CHAR8  *Key,
  IN CONST CHAR8  *Default
  );

INT64
TomlGetInteger (
  IN TOML_NODE    *Table,
  IN CONST CHAR8  *Key,
  IN INT64        Default
  );

BOOLEAN
TomlGetBoolean (
  IN TOML_NODE    *Table,
  IN CONST CHAR8  *Key,
  IN BOOLEAN      Default
  );

UINTN
TomlCount (
  IN TOML_NODE  *Array
  );

// ---------------------------------------------------------------------------
// Configuration model (Config.c)
// ---------------------------------------------------------------------------

typedef enum {
  UniXNUDtSet,
  UniXNUDtDeleteProp,
  UniXNUDtAddNode,
  UniXNUDtDeleteNode,
  UniXNUDtOverlay
} UNIXNU_DT_OP;

typedef struct {
  UNIXNU_DT_OP    Op;
  CHAR8       *Node;       ///< Absolute node path.
  CHAR8       *Prop;       ///< Property name (set / delete-prop).
  VOID        *Value;      ///< Encoded property bytes (set), overlay blob (overlay).
  UINTN       ValueSize;
  CHAR8       *Origin;     ///< "config", "entry <id>" or "kit <name>", for logs.
} UNIXNU_DT_PATCH;

typedef struct {
  EFI_HANDLE    Volume;    ///< Volume holding File.
  CHAR16        *File;
  CHAR16        *Args;
  BOOLEAN       Connect;
  CHAR8         *Origin;
} UNIXNU_DRIVER;

typedef struct {
  EFI_HANDLE    Volume;
  CHAR16        *File;
  CHAR8         *Origin;
} UNIXNU_ACPI_TABLE;

typedef struct {
  EFI_HANDLE  Volume;
  CHAR8       *EntryId;        ///< Required for kit kexts; NULL for entry kexts.
  CHAR16      *BundlePath;
  CHAR16      *PlistPath;
  CHAR16      *ExecutablePath;
  BOOLEAN     Invalid;
} UNIXNU_KEXT;

typedef struct {
  EFI_GUID    Guid;
  CHAR16      *Name;
  VOID        *Data;
  UINTN       DataSize;
  UINT32      Attributes;
} UNIXNU_VARIABLE;

typedef struct {
  CHAR16     *Partition;   ///< GPT partition name.
  CHAR16     *Name;        ///< Label, also stored in the device path.
  UINT64     Offset;       ///< Bytes from the start of the partition.
  UINT64     Length;       ///< Bytes; 0 = to the end of the partition.
  BOOLEAN    Writable;
} UNIXNU_BLOCK_SLICE;

typedef enum {
  UniXNUEntryEfi,
  UniXNUEntryLinux,
  UniXNUEntryAction,
  UniXNUEntryXnu
} UNIXNU_ENTRY_TYPE;

typedef enum {
  UniXNUActionNone,
  UniXNUActionReset,
  UniXNUActionShutdown,
  UniXNUActionExit,
  UniXNUActionTools
} UNIXNU_ACTION;

typedef struct {
  CHAR8            *Id;
  CHAR16           *Title;
  UNIXNU_ENTRY_TYPE    Type;
  UNIXNU_ACTION        Action;
  EFI_HANDLE       Volume;      ///< Volume for Path/Dtb/Initrd.
  CHAR16           *Path;       ///< "\\EFI\\x.efi" or "fv:<GUID>".
  CHAR16           *Args;
  CHAR16           *Confirm;    ///< NULL, or the question shown before this entry boots (it never boots by countdown).
  CHAR16           **ConfirmTitles;  ///< Optional choices offered with the question; each adds ConfirmArgs[i] to Args.
  CHAR16           **ConfirmArgs;
  UINTN            ConfirmCount;
  CHAR16           *Dtb;        ///< NULL, L"firmware" or a file path.
  CHAR16           *Initrd;
  UNIXNU_DT_PATCH      *Patches;    ///< Entry patches, chosen properties last.
  UINTN            PatchCount;
  UNIXNU_VARIABLE      *Variables;
  UINTN            VariableCount;
  UNIXNU_KEXT          *Kexts;
  UINTN            KextCount;
  BOOLEAN          KextConfigError;
} UNIXNU_ENTRY;

typedef enum {
  UniXNUConsoleAuto,
  UniXNUConsoleGraphics,
  UniXNUConsoleText,
  UniXNUConsoleNone
} UNIXNU_CONSOLE;

//
// [ui] layout: landscape (the original arrangement) or portrait (a column
// laid out for a tall panel). Auto picks portrait when width / height is below
// PortraitBelow.
//
typedef enum {
  UniXNULayoutAuto,
  UniXNULayoutLandscape,
  UniXNULayoutPortrait
} UNIXNU_LAYOUT;

#define UNIXNU_PORTRAIT_BELOW_DEFAULT  800   ///< width/height in thousandths.

typedef struct {
  //
  // [boot]
  //
  INTN           Timeout;          ///< Seconds; <0 waits for input; 0 boots at once.
  UINTN          DefaultIndex;
  UINTN          RotateSeconds;    ///< Idle highlight rotation step, 0 = off.
  UINTN          FallbackTimeout;  ///< Used when Timeout < 0 and no input exists.
  BOOLEAN        ConnectAll;       ///< ConnectController all handles after drivers.
  //
  // [ui]
  //
  UNIXNU_CONSOLE     Console;
  CHAR16         *Title;
  UINTN          Scale;            ///< 0 = automatic.
  BOOLEAN        ShowLogo;
  UNIXNU_LAYOUT      Layout;
  UINTN          PortraitBelow;    ///< Auto threshold, width/height in thousandths.
  //
  // Injection, after kits are merged in.
  //
  UNIXNU_DRIVER      *Drivers;
  UINTN          DriverCount;
  UNIXNU_DT_PATCH    *Patches;         ///< Global patches (config + kits).
  UINTN          PatchCount;
  UNIXNU_ACPI_TABLE  *AcpiTables;
  UINTN          AcpiCount;
  UNIXNU_BLOCK_SLICE *Slices;
  UINTN          SliceCount;
  UNIXNU_KEXT        *Kexts;           ///< Kit kexts, selected by entry id.
  UINTN          KextCount;
  BOOLEAN        KextConfigError;
  UNIXNU_ENTRY       *Entries;
  UINTN          EntryCount;
  //
  // Provenance and diagnostics shown on screen.
  //
  EFI_HANDLE     Volume;           ///< Volume the config came from (NULL = built-in).
  CHAR16         *SourceLabel;
  CHAR8          Error[160];       ///< First config/kit error, empty if none.
  CHAR8          Notice[96];       ///< Note for the menu that is not an error, empty if none.
  UINTN          KitsLoaded;
  UINTN          KitsSkipped;
} UNIXNU_CONFIG;

/**
  Find a config file on the boot volume or any other volume and parse it;
  fall back to the built-in configuration. Never fails.
**/
VOID
UniXNUConfigLoad (
  IN  EFI_HANDLE  ImageHandle,
  OUT UNIXNU_CONFIG   *Config
  );

// ---------------------------------------------------------------------------
// Volumes and files (Volume.c)
// ---------------------------------------------------------------------------

EFI_STATUS
UniXNUReadFile (
  IN  EFI_HANDLE    Volume,
  IN  CONST CHAR16  *Path,
  OUT VOID          **Buffer,
  OUT UINTN         *Size
  );

BOOLEAN
UniXNUFileExists (
  IN EFI_HANDLE    Volume,
  IN CONST CHAR16  *Path
  );

/**
  List the names of the entries of a directory. Caller frees each name and
  the array.
**/
EFI_STATUS
UniXNUListDirectory (
  IN  EFI_HANDLE    Volume,
  IN  CONST CHAR16  *Path,
  OUT CHAR16        ***Names,
  OUT UINTN         *Count
  );

/**
  Turn "a/b", "\\a\\b" or "/a/b" into a newly allocated "\\a\\b". When Base is
  given and Path is relative, the result is Base\\Path.
**/
CHAR16 *
UniXNUNormalizePath (
  IN CONST CHAR16  *Base OPTIONAL,
  IN CONST CHAR8   *Path
  );

/**
  ASCII case-insensitive CHAR16 comparison (FAT names, fallback paths).
**/
INTN
UniXNUStriCmp (
  IN CONST CHAR16  *A,
  IN CONST CHAR16  *B
  );

CHAR16 *
UniXNUAsciiToUnicode (
  IN CONST CHAR8  *String
  );

/**
  Build the device path for "\\file" on Volume or "fv:<GUID>" in any FV.
**/
EFI_DEVICE_PATH_PROTOCOL *
UniXNUResolveImagePath (
  IN EFI_HANDLE    Volume,
  IN CONST CHAR16  *Path
  );

// ---------------------------------------------------------------------------
// Injection (Inject.c)
// ---------------------------------------------------------------------------

typedef struct {
  UINTN    DriversLoaded;
  UINTN    DriversFailed;
  UINTN    AcpiInstalled;
  UINTN    AcpiFailed;
} UNIXNU_INJECT_STATS;

/**
  ConnectController() every handle, recursively.
**/
VOID
UniXNUConnectAll (
  VOID
  );

VOID
UniXNUInjectDrivers (
  IN  EFI_HANDLE       ImageHandle,
  IN  UNIXNU_CONFIG        *Config,
  OUT UNIXNU_INJECT_STATS  *Stats
  );

VOID
UniXNUInjectAcpi (
  IN  UNIXNU_CONFIG        *Config,
  OUT UNIXNU_INJECT_STATS  *Stats
  );

EFI_STATUS
UniXNUStageKexts (
  IN  UNIXNU_CONFIG           *Config,
  IN  UNIXNU_ENTRY            *Entry,
  OUT UNIXNU_LOADER_KEXT  **Kexts,
  OUT UINTN               *Count
  );

VOID
UniXNUFreeKexts (
  IN UNIXNU_LOADER_KEXT  *Kexts OPTIONAL,
  IN UINTN               Count
  );

/**
  Apply DT patches to a writable FDT that has room to grow.
**/
EFI_STATUS
UniXNUApplyDtPatches (
  IN OUT VOID         *Fdt,
  IN     UNIXNU_DT_PATCH  *Patches,
  IN     UINTN        Count
  );

/**
  Build the entry's DTB (base + global patches + entry patches) and install it
  as the EFI_DTB_TABLE configuration table. No-op when the entry has no dtb.
**/
EFI_STATUS
UniXNUPrepareDeviceTree (
  IN  UNIXNU_CONFIG  *Config,
  IN  UNIXNU_ENTRY   *Entry,
  OUT VOID       **Fdt OPTIONAL,
  OUT UINTN      *FdtSize OPTIONAL
  );

EFI_STATUS
UniXNUInstallInitrd (
  IN  VOID        *Data,
  IN  UINTN       Size,
  OUT EFI_HANDLE  *Handle
  );

VOID
UniXNUUninstallInitrd (
  IN EFI_HANDLE  Handle
  );

EFI_STATUS
UniXNUSetEntryVariables (
  IN UNIXNU_ENTRY  *Entry
  );

/**
  Return the root "compatible" list of the firmware's DTB table, or NULL.
**/
CONST CHAR8 *
UniXNUFirmwareCompatible (
  OUT UINTN  *Length
  );

// ---------------------------------------------------------------------------
// Block slices (Slice.c)
// ---------------------------------------------------------------------------

/**
  Publish every configured [[block_slice]] as a block device.
**/
VOID
UniXNUPublishSlices (
  IN UNIXNU_CONFIG  *Config
  );

// ---------------------------------------------------------------------------
// Boot (Boot.c)
// ---------------------------------------------------------------------------

EFI_STATUS
UniXNUBootEntry (
  IN EFI_HANDLE  ImageHandle,
  IN UNIXNU_CONFIG   *Config,
  IN UNIXNU_ENTRY    *Entry
  );

// ---------------------------------------------------------------------------
// User interface (Ui.c, Font.c, Logo.c)
// ---------------------------------------------------------------------------

#define UNIXNU_GLYPH_WIDTH   8
#define UNIXNU_GLYPH_HEIGHT  19

extern CONST UINT8  gCaFontGlyphs[95][UNIXNU_GLYPH_HEIGHT];

typedef enum {
  UniXNUUiGraphics,
  UniXNUUiText,
  UniXNUUiHeadless
} UNIXNU_UI_MODE;

typedef struct {
  UNIXNU_UI_MODE                      Mode;
  EFI_GRAPHICS_OUTPUT_PROTOCOL    *Gop;
  UINT32                          Width;
  UINT32                          Height;
  UINTN                           Scale;
  BOOLEAN                         Portrait;         ///< Column layout for a tall panel.
  UINTN                           Margin;           ///< Portrait side margin.
  UINTN                           CardHeight;       ///< Portrait entry card height.
  UINTN                           StatusLines;      ///< Portrait status lines in use.
  UINTN                           MenuTop;
  UINTN                           RowHeight;
  UINTN                           MenuLeft;
  UINTN                           MenuWidth;
  UINTN                           FooterTop;
  UINTN                           ContentTop;       ///< Top of the plugin content region.
  UINTN                           ContentBottom;    ///< Bottom of the plugin content region.
  UINTN                           VisibleRows;
  UINTN                           TextColumns;      ///< Text mode only.
  UINTN                           TextRows;
  CHAR16                          Info[96];         ///< Injection summary line.
  CHAR16                          Notice[96];       ///< Result of the last boot attempt.
} UNIXNU_UI;

/**
  Decide whether the menu uses the portrait layout. Landscape never does and
  portrait always does. Auto does when Width * 1000 < PortraitBelow * Height,
  an exact integer comparison of the aspect ratio.
**/
BOOLEAN
UniXNUUiChoosePortrait (
  IN UNIXNU_LAYOUT  Layout,
  IN UINTN          PortraitBelow,
  IN UINT32         Width,
  IN UINT32         Height
  );

VOID
UniXNUUiInit (
  IN  UNIXNU_CONFIG  *Config,
  OUT UNIXNU_UI      *Ui
  );

VOID
UniXNUUiDrawFrame (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  );

VOID
UniXNUUiDrawEntry (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN UINTN      Index,
  IN BOOLEAN    Selected
  );

VOID
UniXNUUiDrawStatus (
  IN UNIXNU_UI         *Ui,
  IN UINTN         Line,
  IN CONST CHAR16  *Text
  );

VOID
UniXNULogoRender (
  OUT EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer,
  IN  UINTN                          Size,
  IN  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Background
  );

// ---------------------------------------------------------------------------
// Menu (Menu.c)
// ---------------------------------------------------------------------------

/**
  Show the menu and return the chosen entry index.

  @param[in] Countdown  FALSE disables the timeout (after a failed boot).
**/
UINTN
UniXNUMenuRun (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN BOOLEAN    Countdown
  );

/**
  Show the Tools menu, run the selected plugin, and return when the user
  chooses Back. Tools are discovered through the menu plugin protocol, so no
  tool is hardcoded here.
**/
VOID
UniXNUMenuRunTools (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  );

/**
  Ask the user to confirm an entry that has a `confirm` text. Without choices only the Enter key (the power key on a device with
  hardware keys) confirms and any other key cancels. With choices, Up/Down step through them and a final Cancel (selected first),
  Enter picks the shown one. No input device at all cancels. Keys pressed before the question appeared are discarded.

  @retval TRUE   Confirmed.
  @retval FALSE  Cancelled.
**/
BOOLEAN
UniXNUMenuConfirm (
  IN  UNIXNU_UI      *Ui,
  IN  UNIXNU_ENTRY   *Entry,
  OUT UINTN      *Choice
  );

#endif
