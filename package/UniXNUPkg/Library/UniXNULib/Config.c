/** @file
  Configuration discovery and the TOML -> UNIXNU_CONFIG mapping, including kit
  bundles. The schema is documented in Docs/Configuration.md and
  Docs/Kits.md; keep them in sync with this file.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include "Internal.h"

#include <Library/FdtLib.h>

//
// UniXNU targets AArch64 UEFI only.
//
#if !defined (MDE_CPU_AARCH64)
#error "UniXNU supports AARCH64 only"
#endif

#define UNIXNU_ARCH_NAME        "AARCH64"
#define UNIXNU_FALLBACK_LOADER  L"\\EFI\\BOOT\\BOOTAA64.EFI"

#define UNIXNU_CONFIG_DIR  L"\\EFI\\UniXNU"
#define UNIXNU_KITS_DIR    "Kits"
#define UNIXNU_KIT_MANIFEST  L"Kit.toml"

//
// Used when no configuration file is found. Parsed with the same code path
// as a file; removable-media loaders found on other volumes are added in
// front of the action entries. With no loader, the default is "Return to
// firmware": the least surprising thing for an unattended machine, since
// the platform's boot manager then carries on as if UniXNU were absent.
//
STATIC CONST CHAR8  mBuiltinConfig[] =
  "version = 1\n"
  "[boot]\n"
  "timeout = 10\n"
  "rotate = 2\n"
  "[ui]\n"
  "title = \"UniXNU\"\n"
  "[[entry]]\n"
  "id = \"exit\"\n"
  "title = \"Return to firmware\"\n"
  "type = \"action\"\n"
  "action = \"exit\"\n"
  "[[entry]]\n"
  "id = \"reset\"\n"
  "title = \"Restart\"\n"
  "type = \"action\"\n"
  "action = \"reset\"\n"
  "[[entry]]\n"
  "id = \"shutdown\"\n"
  "title = \"Power off\"\n"
  "type = \"action\"\n"
  "action = \"shutdown\"\n"
  "[[entry]]\n"
  "id = \"tools\"\n"
  "title = \"Tools\"\n"
  "type = \"action\"\n"
  "action = \"tools\"\n";

STATIC
VOID
ConfigError (
  IN UNIXNU_CONFIG    *Config,
  IN CONST CHAR8  *Format,
  ...
  )
{
  VA_LIST  Args;
  CHAR8    Message[160];

  VA_START (Args, Format);
  AsciiVSPrint (Message, sizeof (Message), Format, Args);
  VA_END (Args);

  UniXNULog ("config: %a", Message);
  if (Config->Error[0] == '\0') {
    AsciiStrCpyS (Config->Error, sizeof (Config->Error), Message);
  }
}

//
// Grow *Array (of ElementSize items, *Count used) by one zeroed element.
//
STATIC
VOID *
GrowArray (
  IN OUT VOID   **Array,
  IN OUT UINTN  *Count,
  IN     UINTN  ElementSize
  )
{
  VOID  *New;

  New = ReallocatePool (*Count * ElementSize, (*Count + 1) * ElementSize, *Array);
  if (New == NULL) {
    return NULL;
  }

  *Array = New;
  ZeroMem ((UINT8 *)New + *Count * ElementSize, ElementSize);
  (*Count)++;
  return (UINT8 *)New + (*Count - 1) * ElementSize;
}

STATIC
CHAR8 *
AsciiDup (
  IN CONST CHAR8  *String
  )
{
  return (String == NULL) ? NULL : AllocateCopyPool (AsciiStrSize (String), String);
}

//
// Config/kit relative path -> absolute volume path. "fv:<GUID>" is kept as
// "\fv:<GUID>" and resolved at load time.
//
STATIC
CHAR16 *
MakePath (
  IN CONST CHAR16  *BaseDir,
  IN CONST CHAR8   *Path
  )
{
  if (Path == NULL) {
    return NULL;
  }

  if (AsciiStrnCmp (Path, "fv:", 3) == 0) {
    return UniXNUNormalizePath (NULL, Path);
  }

  return UniXNUNormalizePath (BaseDir, Path);
}

// ---------------------------------------------------------------------------
// Value encoding
// ---------------------------------------------------------------------------

STATIC
VOID
PutBe32 (
  IN UINT8   *Out,
  IN UINT32  Value
  )
{
  Out[0] = (UINT8)(Value >> 24);
  Out[1] = (UINT8)(Value >> 16);
  Out[2] = (UINT8)(Value >> 8);
  Out[3] = (UINT8)Value;
}

STATIC
BOOLEAN
ParseHexBytes (
  IN  CONST CHAR8  *Text,
  OUT UINT8        **Bytes,
  OUT UINTN        *Size
  )
{
  UINTN  Len;
  UINTN  Index;
  UINTN  Count;
  UINT8  *Out;
  INTN   High;
  UINT8  V;
  CHAR8  C;

  if ((Text[0] == '0') && ((Text[1] == 'x') || (Text[1] == 'X'))) {
    Text += 2;
  }

  Len = AsciiStrLen (Text);
  Out = AllocateZeroPool (Len / 2 + 1);
  if (Out == NULL) {
    return FALSE;
  }

  Count = 0;
  High  = -1;
  for (Index = 0; Index < Len; Index++) {
    C = Text[Index];
    if ((C == ' ') || (C == ':') || (C == '-') || (C == '_')) {
      continue;
    }

    if ((C >= '0') && (C <= '9')) {
      V = (UINT8)(C - '0');
    } else if ((C >= 'a') && (C <= 'f')) {
      V = (UINT8)(C - 'a' + 10);
    } else if ((C >= 'A') && (C <= 'F')) {
      V = (UINT8)(C - 'A' + 10);
    } else {
      FreePool (Out);
      return FALSE;
    }

    if (High < 0) {
      High = V;
    } else {
      Out[Count++] = (UINT8)((High << 4) | V);
      High         = -1;
    }
  }

  if (High >= 0) {
    FreePool (Out);
    return FALSE;
  }

  *Bytes = Out;
  *Size  = Count;
  return TRUE;
}

//
// Encode a TOML value as FDT property bytes. Type may be NULL (inferred).
//
STATIC
BOOLEAN
EncodeFdtValue (
  IN  TOML_NODE    *Value,
  IN  CONST CHAR8  *Type,
  OUT VOID         **Bytes,
  OUT UINTN        *Size
  )
{
  TOML_NODE  *Item;
  UINTN      Count;
  UINTN      Total;
  UINT8      *Out;
  UINTN      O;
  BOOLEAN    Wide;

  *Bytes = NULL;
  *Size  = 0;

  if (Value == NULL) {
    return (Type != NULL && AsciiStrCmp (Type, "empty") == 0);
  }

  if (Type == NULL) {
    switch (Value->Type) {
      case TomlString:
        Type = "string";
        break;
      case TomlInteger:
        Type = ((UINT64)Value->Integer > MAX_UINT32) ? "u64" : "u32";
        break;
      case TomlBoolean:
        if (!Value->Boolean) {
          return FALSE;
        }

        Type = "empty";
        break;
      case TomlArray:
        Type = (Value->Child != NULL && Value->Child->Type == TomlString) ? "stringlist" : "u32";
        break;
      default:
        return FALSE;
    }
  }

  if (AsciiStrCmp (Type, "empty") == 0) {
    return TRUE;
  }

  if ((AsciiStrCmp (Type, "string") == 0) && (Value->Type == TomlString)) {
    *Size  = AsciiStrSize (Value->String);
    *Bytes = AllocateCopyPool (*Size, Value->String);
    return *Bytes != NULL;
  }

  if (AsciiStrCmp (Type, "stringlist") == 0) {
    if (Value->Type == TomlString) {
      return EncodeFdtValue (Value, "string", Bytes, Size);
    }

    Total = 0;
    for (Item = Value->Child; Item != NULL; Item = Item->Next) {
      if (Item->Type != TomlString) {
        return FALSE;
      }

      Total += AsciiStrSize (Item->String);
    }

    Out = AllocateZeroPool (Total + 1);
    if (Out == NULL) {
      return FALSE;
    }

    O = 0;
    for (Item = Value->Child; Item != NULL; Item = Item->Next) {
      CopyMem (Out + O, Item->String, AsciiStrSize (Item->String));
      O += AsciiStrSize (Item->String);
    }

    *Bytes = Out;
    *Size  = Total;
    return TRUE;
  }

  if ((AsciiStrCmp (Type, "u32") == 0) || (AsciiStrCmp (Type, "u64") == 0)) {
    Wide  = (Type[1] == '6');
    Count = (Value->Type == TomlArray) ? TomlCount (Value) : 1;
    Out   = AllocateZeroPool (Count * (Wide ? 8 : 4) + 1);
    if (Out == NULL) {
      return FALSE;
    }

    O    = 0;
    Item = (Value->Type == TomlArray) ? Value->Child : Value;
    for ( ; Item != NULL; Item = (Value->Type == TomlArray) ? Item->Next : NULL) {
      if (Item->Type != TomlInteger) {
        FreePool (Out);
        return FALSE;
      }

      if (Wide) {
        PutBe32 (Out + O, (UINT32)RShiftU64 ((UINT64)Item->Integer, 32));
        O += 4;
      }

      PutBe32 (Out + O, (UINT32)Item->Integer);
      O += 4;
    }

    *Bytes = Out;
    *Size  = O;
    return TRUE;
  }

  if (AsciiStrCmp (Type, "bytes") == 0) {
    if (Value->Type == TomlString) {
      return ParseHexBytes (Value->String, (UINT8 **)Bytes, Size);
    }

    if (Value->Type != TomlArray) {
      return FALSE;
    }

    Count = TomlCount (Value);
    Out   = AllocateZeroPool (Count + 1);
    if (Out == NULL) {
      return FALSE;
    }

    O = 0;
    for (Item = Value->Child; Item != NULL; Item = Item->Next) {
      if ((Item->Type != TomlInteger) || ((UINT64)Item->Integer > 0xFF)) {
        FreePool (Out);
        return FALSE;
      }

      Out[O++] = (UINT8)Item->Integer;
    }

    *Bytes = Out;
    *Size  = O;
    return TRUE;
  }

  return FALSE;
}

//
// Encode a TOML value as UEFI variable data (little endian).
//
STATIC
BOOLEAN
EncodeVariableValue (
  IN  TOML_NODE    *Value,
  IN  CONST CHAR8  *Type,
  OUT VOID         **Bytes,
  OUT UINTN        *Size
  )
{
  CHAR16  *Wide;

  if (Value == NULL) {
    return FALSE;
  }

  if (Type == NULL) {
    Type = (Value->Type == TomlString) ? "ascii" : ((Value->Type == TomlInteger) ? "u32" : "bytes");
  }

  if ((AsciiStrCmp (Type, "ascii") == 0) && (Value->Type == TomlString)) {
    *Size  = AsciiStrLen (Value->String);
    *Bytes = AllocateCopyPool (*Size + 1, Value->String);
    return *Bytes != NULL;
  }

  if ((AsciiStrCmp (Type, "ucs2") == 0) && (Value->Type == TomlString)) {
    Wide = UniXNUAsciiToUnicode (Value->String);
    if (Wide == NULL) {
      return FALSE;
    }

    *Bytes = Wide;
    *Size  = StrSize (Wide);
    return TRUE;
  }

  if ((Value->Type == TomlInteger) &&
      ((AsciiStrCmp (Type, "u8") == 0) || (AsciiStrCmp (Type, "u16") == 0) ||
       (AsciiStrCmp (Type, "u32") == 0) || (AsciiStrCmp (Type, "u64") == 0)))
  {
    *Size  = (Type[1] == '8') ? 1 : ((Type[1] == '1') ? 2 : ((Type[1] == '3') ? 4 : 8));
    *Bytes = AllocateZeroPool (8);
    if (*Bytes == NULL) {
      return FALSE;
    }

    CopyMem (*Bytes, &Value->Integer, *Size);
    return TRUE;
  }

  if (AsciiStrCmp (Type, "bytes") == 0) {
    //
    // Same rules as FDT bytes; byte order does not apply.
    //
    return EncodeFdtValue (Value, "bytes", Bytes, Size);
  }

  return FALSE;
}

// ---------------------------------------------------------------------------
// Sections shared by the config file and kit manifests
// ---------------------------------------------------------------------------

STATIC
BOOLEAN
ParseDtOp (
  IN  CONST CHAR8  *Op,
  OUT UNIXNU_DT_OP     *Out
  )
{
  if (AsciiStrCmp (Op, "set") == 0) {
    *Out = UniXNUDtSet;
  } else if (AsciiStrCmp (Op, "delete-prop") == 0) {
    *Out = UniXNUDtDeleteProp;
  } else if (AsciiStrCmp (Op, "add-node") == 0) {
    *Out = UniXNUDtAddNode;
  } else if (AsciiStrCmp (Op, "delete-node") == 0) {
    *Out = UniXNUDtDeleteNode;
  } else if (AsciiStrCmp (Op, "overlay") == 0) {
    *Out = UniXNUDtOverlay;
  } else {
    return FALSE;
  }

  return TRUE;
}

//
// Append one [[dt_patch]] table to (*Patches, *Count).
//
STATIC
VOID
AddDtPatch (
  IN     UNIXNU_CONFIG     *Config,
  IN     TOML_NODE     *Table,
  IN     EFI_HANDLE    Volume,
  IN     CONST CHAR16  *BaseDir,
  IN     CONST CHAR8   *Origin,
  IN OUT UNIXNU_DT_PATCH   **Patches,
  IN OUT UINTN         *Count
  )
{
  UNIXNU_DT_PATCH  Patch;
  UNIXNU_DT_PATCH  *Slot;
  CONST CHAR8  *OpName;
  CONST CHAR8  *File;
  CHAR16       *FilePath;
  EFI_STATUS   Status;

  ZeroMem (&Patch, sizeof (Patch));
  OpName = TomlGetString (Table, "op", "set");
  if (!ParseDtOp (OpName, &Patch.Op)) {
    ConfigError (Config, "%a: unknown dt_patch op '%a' (line %u)", Origin, OpName, (UINT32)Table->Line);
    return;
  }

  Patch.Node   = AsciiDup (TomlGetString (Table, "node", NULL));
  Patch.Prop   = AsciiDup (TomlGetString (Table, "prop", NULL));
  Patch.Origin = AsciiDup (Origin);

  switch (Patch.Op) {
    case UniXNUDtOverlay:
      File = TomlGetString (Table, "file", NULL);
      if (File == NULL) {
        ConfigError (Config, "%a: overlay needs 'file' (line %u)", Origin, (UINT32)Table->Line);
        return;
      }

      FilePath = MakePath (BaseDir, File);
      Status   = UniXNUReadFile (Volume, FilePath, &Patch.Value, &Patch.ValueSize);
      if (EFI_ERROR (Status)) {
        ConfigError (Config, "%a: cannot read overlay %s: %r", Origin, FilePath, Status);
        FreePool (FilePath);
        return;
      }

      FreePool (FilePath);
      break;

    case UniXNUDtSet:
      if ((Patch.Node == NULL) || (Patch.Prop == NULL) ||
          !EncodeFdtValue (TomlGet (Table, "value"), TomlGetString (Table, "type", NULL), &Patch.Value, &Patch.ValueSize))
      {
        ConfigError (Config, "%a: dt_patch set needs node, prop and a valid value (line %u)", Origin, (UINT32)Table->Line);
        return;
      }

      break;

    case UniXNUDtDeleteProp:
      if ((Patch.Node == NULL) || (Patch.Prop == NULL)) {
        ConfigError (Config, "%a: delete-prop needs node and prop (line %u)", Origin, (UINT32)Table->Line);
        return;
      }

      break;

    default:
      if (Patch.Node == NULL) {
        ConfigError (Config, "%a: dt_patch needs node (line %u)", Origin, (UINT32)Table->Line);
        return;
      }

      break;
  }

  Slot = GrowArray ((VOID **)Patches, Count, sizeof (UNIXNU_DT_PATCH));
  if (Slot != NULL) {
    CopyMem (Slot, &Patch, sizeof (Patch));
  }
}

STATIC
VOID
AddDriver (
  IN UNIXNU_CONFIG     *Config,
  IN TOML_NODE     *Table,
  IN EFI_HANDLE    Volume,
  IN CONST CHAR16  *BaseDir,
  IN CONST CHAR8   *Origin,
  IN CONST CHAR8   *PathKey
  )
{
  UNIXNU_DRIVER    *Driver;
  CONST CHAR8  *Path;

  if (!TomlGetBoolean (Table, "enabled", TRUE)) {
    return;
  }

  Path = TomlGetString (Table, PathKey, NULL);
  if (Path == NULL) {
    ConfigError (Config, "%a: driver needs '%a' (line %u)", Origin, PathKey, (UINT32)Table->Line);
    return;
  }

  Driver = GrowArray ((VOID **)&Config->Drivers, &Config->DriverCount, sizeof (UNIXNU_DRIVER));
  if (Driver == NULL) {
    return;
  }

  Driver->Volume  = Volume;
  Driver->File    = MakePath (BaseDir, Path);
  Driver->Args    = UniXNUAsciiToUnicode (TomlGetString (Table, "args", NULL));
  Driver->Connect = TomlGetBoolean (Table, "connect", TRUE);
  Driver->Origin  = AsciiDup (Origin);
}

STATIC
VOID
AddAcpi (
  IN UNIXNU_CONFIG     *Config,
  IN EFI_HANDLE    Volume,
  IN CONST CHAR16  *BaseDir,
  IN CONST CHAR8   *Path,
  IN CONST CHAR8   *Origin
  )
{
  UNIXNU_ACPI_TABLE  *Table;

  Table = GrowArray ((VOID **)&Config->AcpiTables, &Config->AcpiCount, sizeof (UNIXNU_ACPI_TABLE));
  if (Table != NULL) {
    Table->Volume = Volume;
    Table->File   = MakePath (BaseDir, Path);
    Table->Origin = AsciiDup (Origin);
  }
}

// ---------------------------------------------------------------------------
// Kits
// ---------------------------------------------------------------------------

STATIC
BOOLEAN
BundleRelativePath (
  IN CONST CHAR8  *Path
  )
{
  CONST CHAR8  *Part;
  CONST CHAR8  *End;
  UINTN        Length;

  Part = Path;
  while (*Part != '\0') {
    End = Part;
    while ((*End != '\0') && (*End != '/') && (*End != '\\')) {
      if (((UINT8)*End < 0x20) || ((UINT8)*End >= 0x7F) || (*End == ':')) {
        return FALSE;
      }

      End++;
    }

    Length = (UINTN)(End - Part);
    if ((Length == 0) || ((Length == 1) && (Part[0] == '.')) ||
        ((Length == 2) && (Part[0] == '.') && (Part[1] == '.')))
    {
      return FALSE;
    }

    if (*End == '\0') {
      return TRUE;
    }

    Part = End + 1;
  }

  return FALSE;
}

STATIC
VOID
AddKext (
  IN     UNIXNU_CONFIG     *Config,
  IN     TOML_NODE     *Table,
  IN     EFI_HANDLE    Volume,
  IN     CONST CHAR16  *BaseDir,
  IN     CONST CHAR8   *Origin,
  IN     BOOLEAN       FromKit,
  IN OUT UNIXNU_KEXT       **Kexts,
  IN OUT UINTN         *Count,
  IN OUT BOOLEAN       *Error
  )
{
  CONST CHAR8  *Bundle;
  CONST CHAR8  *Plist;
  CONST CHAR8  *Executable;
  CONST CHAR8  *EntryId;
  TOML_NODE    *Value;
  UNIXNU_KEXT      *Kext;
  UINTN        Index;
  CONST CHAR8  *StringKeys[] = { "bundle", "plist", "executable", "entry" };

  Value = TomlGet (Table, "enabled");
  if ((Value != NULL) && (Value->Type != TomlBoolean)) {
    ConfigError (Config, "%a: kext enabled must be boolean", Origin);
    *Error = TRUE;
    return;
  }

  if (!TomlGetBoolean (Table, "enabled", TRUE)) {
    return;
  }

  for (Index = 0; Index < ARRAY_SIZE (StringKeys); Index++) {
    Value = TomlGet (Table, StringKeys[Index]);
    if ((Value != NULL) && (Value->Type != TomlString)) {
      ConfigError (Config, "%a: kext %a must be a string", Origin, StringKeys[Index]);
      *Error = TRUE;
      return;
    }
  }

  Bundle     = TomlGetString (Table, "bundle", NULL);
  Plist      = TomlGetString (Table, "plist", "Contents/Info.plist");
  Executable = TomlGetString (Table, "executable", "");
  EntryId    = TomlGetString (Table, "entry", NULL);
  if ((Bundle == NULL) || (AsciiStrLen (Bundle) < 6) ||
      (AsciiStrCmp (Bundle + AsciiStrLen (Bundle) - 5, ".kext") != 0) ||
      !BundleRelativePath (Bundle + ((Bundle[0] == '/') || (Bundle[0] == '\\'))) ||
      !BundleRelativePath (Plist) ||
      ((Executable[0] != '\0') && !BundleRelativePath (Executable)) ||
      (FromKit && ((EntryId == NULL) || (EntryId[0] == '\0'))) ||
      (!FromKit && (EntryId != NULL)))
  {
    ConfigError (Config, "%a: kext needs a .kext bundle, relative file paths and valid entry scope", Origin);
    *Error = TRUE;
    return;
  }

  Kext = GrowArray ((VOID **)Kexts, Count, sizeof (UNIXNU_KEXT));
  if (Kext == NULL) {
    *Error = TRUE;
    return;
  }

  Kext->Volume     = Volume;
  Kext->EntryId    = AsciiDup (EntryId);
  Kext->BundlePath = MakePath (BaseDir, Bundle);
  if (Kext->BundlePath != NULL) {
    Kext->PlistPath = MakePath (Kext->BundlePath, Plist);
    if (Executable[0] != '\0') {
      Kext->ExecutablePath = MakePath (Kext->BundlePath, Executable);
    }
  }

  Kext->Invalid = (Kext->BundlePath == NULL) || (Kext->PlistPath == NULL) ||
                  (FromKit && (Kext->EntryId == NULL)) ||
                  ((Executable[0] != '\0') && (Kext->ExecutablePath == NULL));
}

STATIC
BOOLEAN
AnyStringMatches (
  IN TOML_NODE  *Value,
  IN BOOLEAN (*Predicate)(IN CONST CHAR8 *Candidate)
  )
{
  TOML_NODE  *Item;

  if (Value->Type == TomlString) {
    return Predicate (Value->String);
  }

  if (Value->Type != TomlArray) {
    return FALSE;
  }

  for (Item = Value->Child; Item != NULL; Item = Item->Next) {
    if ((Item->Type == TomlString) && Predicate (Item->String)) {
      return TRUE;
    }
  }

  return FALSE;
}

STATIC
BOOLEAN
MatchCompatible (
  IN CONST CHAR8  *Candidate
  )
{
  CONST CHAR8  *List;
  UINTN        Length;
  UINTN        Offset;

  List = UniXNUFirmwareCompatible (&Length);
  if (List == NULL) {
    return FALSE;
  }

  for (Offset = 0; Offset < Length; Offset += AsciiStrSize (List + Offset)) {
    if (AsciiStrCmp (List + Offset, Candidate) == 0) {
      return TRUE;
    }
  }

  return FALSE;
}

STATIC
BOOLEAN
MatchVendor (
  IN CONST CHAR8  *Candidate
  )
{
  CHAR16   *Wide;
  BOOLEAN  Found;

  if (gST->FirmwareVendor == NULL) {
    return FALSE;
  }

  Wide = UniXNUAsciiToUnicode (Candidate);
  if (Wide == NULL) {
    return FALSE;
  }

  Found = (StrStr (gST->FirmwareVendor, Wide) != NULL);
  FreePool (Wide);
  return Found;
}

STATIC
BOOLEAN
MatchProtocol (
  IN CONST CHAR8  *Candidate
  )
{
  EFI_GUID  Guid;
  VOID      *Interface;

  if (RETURN_ERROR (AsciiStrToGuid (Candidate, &Guid))) {
    return FALSE;
  }

  return !EFI_ERROR (gBS->LocateProtocol (&Guid, NULL, &Interface));
}

//
// All present [match] keys must be satisfied; within a key, any listed value.
//
STATIC
BOOLEAN
KitMatches (
  IN  TOML_NODE  *Manifest,
  OUT CHAR8      *Reason,
  IN  UINTN      ReasonSize
  )
{
  TOML_NODE  *Match;
  TOML_NODE  *Value;
  TOML_NODE  *Item;

  Match = TomlGet (Manifest, "match");
  if (Match == NULL) {
    return TRUE;
  }

  Value = TomlGet (Match, "arch");
  if (Value != NULL) {
    BOOLEAN  Ok = FALSE;
    if (Value->Type == TomlString) {
      Ok = (AsciiStrCmp (Value->String, UNIXNU_ARCH_NAME) == 0);
    } else {
      for (Item = Value->Child; Item != NULL; Item = Item->Next) {
        Ok = Ok || (Item->Type == TomlString && AsciiStrCmp (Item->String, UNIXNU_ARCH_NAME) == 0);
      }
    }

    if (!Ok) {
      AsciiStrCpyS (Reason, ReasonSize, "arch");
      return FALSE;
    }
  }

  Value = TomlGet (Match, "fdt_compatible");
  if ((Value != NULL) && !AnyStringMatches (Value, MatchCompatible)) {
    AsciiStrCpyS (Reason, ReasonSize, "fdt_compatible");
    return FALSE;
  }

  Value = TomlGet (Match, "firmware_vendor");
  if ((Value != NULL) && !AnyStringMatches (Value, MatchVendor)) {
    AsciiStrCpyS (Reason, ReasonSize, "firmware_vendor");
    return FALSE;
  }

  //
  // requires_protocol: every GUID must be present.
  //
  Value = TomlGet (Match, "requires_protocol");
  if (Value != NULL) {
    if (Value->Type == TomlString) {
      if (!MatchProtocol (Value->String)) {
        AsciiStrCpyS (Reason, ReasonSize, "requires_protocol");
        return FALSE;
      }
    } else {
      for (Item = Value->Child; Item != NULL; Item = Item->Next) {
        if ((Item->Type != TomlString) || !MatchProtocol (Item->String)) {
          AsciiStrCpyS (Reason, ReasonSize, "requires_protocol");
          return FALSE;
        }
      }
    }
  }

  return TRUE;
}

//
// Load <KitDir>\Kit.toml and merge its contents into Config.
//
STATIC
VOID
LoadKit (
  IN UNIXNU_CONFIG     *Config,
  IN EFI_HANDLE    Volume,
  IN CONST CHAR16  *KitDir
  )
{
  EFI_STATUS   Status;
  CHAR16       *ManifestPath;
  CHAR8        *Text;
  UINTN        Size;
  TOML_NODE    *Manifest;
  TOML_NODE    *Kit;
  TOML_NODE    *List;
  TOML_NODE    *Item;
  CHAR8        Error[96];
  CHAR8        Origin[80];
  CHAR8        Reason[32];
  CONST CHAR8  *Name;

  ManifestPath = AllocateZeroPool (StrSize (KitDir) + StrSize (UNIXNU_KIT_MANIFEST));
  if (ManifestPath == NULL) {
    return;
  }

  StrCpyS (ManifestPath, StrSize (KitDir) / sizeof (CHAR16) + StrLen (UNIXNU_KIT_MANIFEST) + 1, KitDir);
  StrCatS (ManifestPath, StrSize (KitDir) / sizeof (CHAR16) + StrLen (UNIXNU_KIT_MANIFEST) + 1, L"\\");
  StrCatS (ManifestPath, StrSize (KitDir) / sizeof (CHAR16) + StrLen (UNIXNU_KIT_MANIFEST) + 1, UNIXNU_KIT_MANIFEST);

  Status = UniXNUReadFile (Volume, ManifestPath, (VOID **)&Text, &Size);
  if (EFI_ERROR (Status)) {
    ConfigError (Config, "kit %s: no Kit.toml (%r)", KitDir, Status);
    FreePool (ManifestPath);
    Config->KitsSkipped++;
    return;
  }

  FreePool (ManifestPath);
  Status = TomlParse (Text, Size, &Manifest, Error, sizeof (Error));
  FreePool (Text);
  if (EFI_ERROR (Status)) {
    ConfigError (Config, "kit %s: %a", KitDir, Error);
    Config->KitsSkipped++;
    return;
  }

  Kit  = TomlGet (Manifest, "kit");
  Name = TomlGetString (Kit, "name", NULL);
  if ((Name == NULL) || (TomlGetInteger (Manifest, "schema", 0) != UNIXNU_SCHEMA_VERSION)) {
    ConfigError (Config, "kit %s: needs [kit] name and schema = %d", KitDir, UNIXNU_SCHEMA_VERSION);
    TomlFree (Manifest);
    Config->KitsSkipped++;
    return;
  }

  AsciiSPrint (Origin, sizeof (Origin), "kit %a", Name);
  if (!KitMatches (Manifest, Reason, sizeof (Reason))) {
    UniXNULog ("kit %a %a: not loaded, [match] %a not satisfied", Name, TomlGetString (Kit, "version", "?"), Reason);
    TomlFree (Manifest);
    Config->KitsSkipped++;
    return;
  }

  List = TomlGet (Manifest, "driver");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddDriver (Config, Item, Volume, KitDir, Origin, "file");
  }

  List = TomlGet (Manifest, "overlay");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    UNIXNU_DT_PATCH  *Patch;
    CHAR16       *Path;
    CONST CHAR8  *File;

    File = TomlGetString (Item, "file", NULL);
    if (File == NULL) {
      ConfigError (Config, "%a: [[overlay]] needs 'file'", Origin);
      continue;
    }

    Path  = MakePath (KitDir, File);
    Patch = GrowArray ((VOID **)&Config->Patches, &Config->PatchCount, sizeof (UNIXNU_DT_PATCH));
    if ((Path == NULL) || (Patch == NULL)) {
      continue;
    }

    Patch->Op     = UniXNUDtOverlay;
    Patch->Origin = AsciiDup (Origin);
    Status        = UniXNUReadFile (Volume, Path, &Patch->Value, &Patch->ValueSize);
    if (EFI_ERROR (Status)) {
      ConfigError (Config, "%a: cannot read %s: %r", Origin, Path, Status);
      Config->PatchCount--;
    }

    FreePool (Path);
  }

  List = TomlGet (Manifest, "dt_patch");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddDtPatch (Config, Item, Volume, KitDir, Origin, &Config->Patches, &Config->PatchCount);
  }

  List = TomlGet (Manifest, "acpi");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    if (TomlGetString (Item, "file", NULL) != NULL) {
      AddAcpi (Config, Volume, KitDir, TomlGetString (Item, "file", NULL), Origin);
    }
  }

  List = TomlGet (Manifest, "kext");
  if ((List != NULL) && ((List->Type != TomlArray) || !List->TableArray)) {
    ConfigError (Config, "%a: kext must be an array of tables", Origin);
    Config->KextConfigError = TRUE;
  } else {
    for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
      AddKext (Config, Item, Volume, KitDir, Origin, TRUE,
               &Config->Kexts, &Config->KextCount, &Config->KextConfigError);
    }
  }

  UniXNULog ("kit %a %a: loaded", Name, TomlGetString (Kit, "version", "?"));
  Config->KitsLoaded++;
  TomlFree (Manifest);
}

STATIC
INTN
EFIAPI
CompareNames (
  IN CONST VOID  *A,
  IN CONST VOID  *B
  )
{
  return UniXNUStriCmp (*(CHAR16 **)A, *(CHAR16 **)B);
}

STATIC
VOID
LoadKits (
  IN UNIXNU_CONFIG  *Config,
  IN TOML_NODE  *Root
  )
{
  TOML_NODE    *List;
  TOML_NODE    *Item;
  TOML_NODE    *Kits;
  CHAR16       *Dir;
  CHAR16       **Names;
  UINTN        Count;
  UINTN        Index;
  UINTN        Len;
  CHAR16       *KitDir;

  //
  // Explicit [[kit]] entries first, in file order.
  //
  List = TomlGet (Root, "kit");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    if (!TomlGetBoolean (Item, "enabled", TRUE) || (TomlGetString (Item, "path", NULL) == NULL)) {
      continue;
    }

    KitDir = MakePath (UNIXNU_CONFIG_DIR, TomlGetString (Item, "path", NULL));
    if (KitDir != NULL) {
      LoadKit (Config, Config->Volume, KitDir);
      FreePool (KitDir);
    }
  }

  //
  // Then every *.kit directory under [kits] directory, sorted by name.
  //
  Kits = TomlGet (Root, "kits");
  if (!TomlGetBoolean (Kits, "autoload", FALSE)) {
    return;
  }

  Dir = MakePath (UNIXNU_CONFIG_DIR, TomlGetString (Kits, "directory", UNIXNU_KITS_DIR));
  if ((Dir == NULL) || EFI_ERROR (UniXNUListDirectory (Config->Volume, Dir, &Names, &Count))) {
    if (Dir != NULL) {
      FreePool (Dir);
    }

    return;
  }

  if (Count > 1) {
    CHAR16  *Swap;
    QuickSort (Names, Count, sizeof (CHAR16 *), CompareNames, &Swap);
  }

  for (Index = 0; Index < Count; Index++) {
    Len = StrLen (Names[Index]);
    if ((Len > 4) && (UniXNUStriCmp (Names[Index] + Len - 4, L".kit") == 0)) {
      UINTN  Chars = StrLen (Dir) + Len + 2;
      KitDir = AllocateZeroPool (Chars * sizeof (CHAR16));
      if (KitDir != NULL) {
        UnicodeSPrint (KitDir, Chars * sizeof (CHAR16), L"%s\\%s", Dir, Names[Index]);
        LoadKit (Config, Config->Volume, KitDir);
        FreePool (KitDir);
      }
    }

    FreePool (Names[Index]);
  }

  FreePool (Names);
  FreePool (Dir);
}

// ---------------------------------------------------------------------------
// Entries
// ---------------------------------------------------------------------------

STATIC
VOID
AddEntry (
  IN UNIXNU_CONFIG  *Config,
  IN TOML_NODE  *Table
  )
{
  UNIXNU_ENTRY     *Entry;
  CONST CHAR8  *Type;
  CONST CHAR8  *Action;
  CONST CHAR8  *Path;
  TOML_NODE    *List;
  TOML_NODE    *Item;
  CHAR8        Origin[64];
  UNIXNU_DT_PATCH  *Patch;

  if (!TomlGetBoolean (Table, "enabled", TRUE)) {
    return;
  }

  Entry = GrowArray ((VOID **)&Config->Entries, &Config->EntryCount, sizeof (UNIXNU_ENTRY));
  if (Entry == NULL) {
    return;
  }

  Entry->Id     = AsciiDup (TomlGetString (Table, "id", NULL));
  Entry->Title  = UniXNUAsciiToUnicode (TomlGetString (Table, "title", TomlGetString (Table, "id", "Untitled")));
  Entry->Volume = Config->Volume;
  AsciiSPrint (Origin, sizeof (Origin), "entry %a", (Entry->Id != NULL) ? Entry->Id : "?");

  Type = TomlGetString (Table, "type", "efi");
  if (AsciiStrCmp (Type, "efi") == 0) {
    Entry->Type = UniXNUEntryEfi;
  } else if (AsciiStrCmp (Type, "linux") == 0) {
    Entry->Type = UniXNUEntryLinux;
  } else if (AsciiStrCmp (Type, "xnu") == 0) {
    Entry->Type = UniXNUEntryXnu;
  } else if (AsciiStrCmp (Type, "action") == 0) {
    Entry->Type = UniXNUEntryAction;
    Action      = TomlGetString (Table, "action", "");
    if (AsciiStrCmp (Action, "reset") == 0) {
      Entry->Action = UniXNUActionReset;
    } else if (AsciiStrCmp (Action, "shutdown") == 0) {
      Entry->Action = UniXNUActionShutdown;
    } else if (AsciiStrCmp (Action, "exit") == 0) {
      Entry->Action = UniXNUActionExit;
    } else if (AsciiStrCmp (Action, "tools") == 0) {
      Entry->Action = UniXNUActionTools;
    } else {
      ConfigError (Config, "%a: unknown action '%a'", Origin, Action);
    }
  } else {
    ConfigError (Config, "%a: unknown type '%a'", Origin, Type);
  }

  Path = TomlGetString (Table, "path", NULL);
  if ((Entry->Type != UniXNUEntryAction) && (Path == NULL)) {
    ConfigError (Config, "%a: needs 'path'", Origin);
  }

  Entry->Path   = MakePath (UNIXNU_CONFIG_DIR, Path);
  Entry->Args   = UniXNUAsciiToUnicode (TomlGetString (Table, "args", NULL));
  Entry->Confirm = UniXNUAsciiToUnicode (TomlGetString (Table, "confirm", NULL));
  {
    TOML_NODE  *Titles = TomlGet (Table, "confirm_titles");
    TOML_NODE  *Extra  = TomlGet (Table, "confirm_args");
    TOML_NODE  *T;
    TOML_NODE  *A;
    UINTN      N;

    if ((Titles != NULL) && (Extra != NULL) && (Titles->Type == TomlArray) && (Extra->Type == TomlArray) &&
        (TomlCount (Titles) == TomlCount (Extra)) && (TomlCount (Titles) > 0) && (Entry->Confirm != NULL))
    {
      N                    = TomlCount (Titles);
      Entry->ConfirmTitles = AllocateZeroPool (N * sizeof (CHAR16 *));
      Entry->ConfirmArgs   = AllocateZeroPool (N * sizeof (CHAR16 *));
      if ((Entry->ConfirmTitles != NULL) && (Entry->ConfirmArgs != NULL)) {
        for (T = Titles->Child, A = Extra->Child; (T != NULL) && (A != NULL); T = T->Next, A = A->Next) {
          if ((T->Type != TomlString) || (A->Type != TomlString)) {
            break;
          }

          Entry->ConfirmTitles[Entry->ConfirmCount] = UniXNUAsciiToUnicode (T->String);
          Entry->ConfirmArgs[Entry->ConfirmCount]   = UniXNUAsciiToUnicode (A->String);
          Entry->ConfirmCount++;
        }
      }
    } else if ((Titles != NULL) || (Extra != NULL)) {
      ConfigError (Config, "entry '%a': confirm_titles and confirm_args must be arrays of strings of equal length, with confirm", (Entry->Id != NULL) ? Entry->Id : "?");
    }
  }
  Entry->Initrd = MakePath (UNIXNU_CONFIG_DIR, TomlGetString (Table, "initrd", NULL));
  List = TomlGet (Table, "kext");
  if (List != NULL) {
    if ((Entry->Type != UniXNUEntryXnu) || (List->Type != TomlArray) || !List->TableArray) {
      ConfigError (Config, "%a: [[entry.kext]] requires type xnu and an array of tables", Origin);
      Entry->KextConfigError = TRUE;
    } else {
      for (Item = List->Child; Item != NULL; Item = Item->Next) {
        AddKext (Config, Item, Config->Volume, UNIXNU_CONFIG_DIR, Origin, FALSE,
                 &Entry->Kexts, &Entry->KextCount, &Entry->KextConfigError);
      }
    }
  }

  if (TomlGetString (Table, "dtb", NULL) != NULL) {
    if (AsciiStrCmp (TomlGetString (Table, "dtb", NULL), "firmware") == 0) {
      Entry->Dtb = AllocateCopyPool (sizeof (L"firmware"), L"firmware");
    } else {
      Entry->Dtb = MakePath (UNIXNU_CONFIG_DIR, TomlGetString (Table, "dtb", NULL));
    }
  }

  List = TomlGet (Table, "dt_patch");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddDtPatch (Config, Item, Config->Volume, UNIXNU_CONFIG_DIR, Origin, &Entry->Patches, &Entry->PatchCount);
  }

  //
  // [entry.chosen]: each key becomes a /chosen property, applied last.
  //
  List = TomlGet (Table, "chosen");
  for (Item = (List != NULL && List->Type == TomlTable) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    VOID   *Bytes;
    UINTN  Size;

    if (!EncodeFdtValue (Item, NULL, &Bytes, &Size)) {
      ConfigError (Config, "%a: bad chosen value '%a'", Origin, Item->Key);
      continue;
    }

    Patch = GrowArray ((VOID **)&Entry->Patches, &Entry->PatchCount, sizeof (UNIXNU_DT_PATCH));
    if (Patch != NULL) {
      Patch->Op        = UniXNUDtSet;
      Patch->Node      = AsciiDup ("/chosen");
      Patch->Prop      = AsciiDup (Item->Key);
      Patch->Value     = Bytes;
      Patch->ValueSize = Size;
      Patch->Origin    = AsciiDup (Origin);
    }
  }

  List = TomlGet (Table, "variable");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    UNIXNU_VARIABLE  Var;
    UNIXNU_VARIABLE  *Slot;

    ZeroMem (&Var, sizeof (Var));
    if ((TomlGetString (Item, "guid", NULL) == NULL) || (TomlGetString (Item, "name", NULL) == NULL) ||
        RETURN_ERROR (AsciiStrToGuid (TomlGetString (Item, "guid", NULL), &Var.Guid)) ||
        !EncodeVariableValue (TomlGet (Item, "value"), TomlGetString (Item, "type", NULL), &Var.Data, &Var.DataSize))
    {
      ConfigError (Config, "%a: variable needs guid, name and a valid value (line %u)", Origin, (UINT32)Item->Line);
      continue;
    }

    Var.Name       = UniXNUAsciiToUnicode (TomlGetString (Item, "name", NULL));
    Var.Attributes = EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS;
    if (!TomlGetBoolean (Item, "volatile", TRUE)) {
      Var.Attributes |= EFI_VARIABLE_NON_VOLATILE;
    }

    Slot = GrowArray ((VOID **)&Entry->Variables, &Entry->VariableCount, sizeof (UNIXNU_VARIABLE));
    if (Slot != NULL) {
      CopyMem (Slot, &Var, sizeof (Var));
    }
  }
}

//
// Add an entry for the removable-media loader of every other volume and
// return how many were found.
//
STATIC
UINTN
AddFallbackLoaders (
  IN UNIXNU_CONFIG   *Config,
  IN EFI_HANDLE  ImageHandle
  )
{
  EFI_STATUS                 Status;
  EFI_HANDLE                 *Handles;
  UINTN                      Count;
  UINTN                      Index;
  EFI_LOADED_IMAGE_PROTOCOL  *Self;
  CHAR16                     *SelfPath;
  UNIXNU_ENTRY                   *Entry;
  UNIXNU_ENTRY                   Saved[3];
  UINTN                      Actions;
  UINTN                      Found;
  CHAR16                     Title[48];

  Self     = NULL;
  SelfPath = NULL;
  if (!EFI_ERROR (gBS->HandleProtocol (ImageHandle, &gEfiLoadedImageProtocolGuid, (VOID **)&Self)) &&
      (Self->FilePath != NULL))
  {
    SelfPath = ConvertDevicePathToText (Self->FilePath, FALSE, FALSE);
  }

  Status = gBS->LocateHandleBuffer (ByProtocol, &gEfiSimpleFileSystemProtocolGuid, NULL, &Count, &Handles);
  if (EFI_ERROR (Status)) {
    Count   = 0;
    Handles = NULL;
  }

  //
  // The built-in action entries stay at the end of the list.
  //
  Actions = MIN (Config->EntryCount, ARRAY_SIZE (Saved));
  CopyMem (Saved, Config->Entries + Config->EntryCount - Actions, Actions * sizeof (UNIXNU_ENTRY));
  Config->EntryCount -= Actions;

  Found = 0;
  for (Index = 0; Index < Count; Index++) {
    if (!UniXNUFileExists (Handles[Index], UNIXNU_FALLBACK_LOADER)) {
      continue;
    }

    if ((Self != NULL) && (Handles[Index] == Self->DeviceHandle) && (SelfPath != NULL) &&
        (UniXNUStriCmp (SelfPath, UNIXNU_FALLBACK_LOADER) == 0))
    {
      continue;
    }

    Entry = GrowArray ((VOID **)&Config->Entries, &Config->EntryCount, sizeof (UNIXNU_ENTRY));
    if (Entry == NULL) {
      break;
    }

    Found++;
    UnicodeSPrint (Title, sizeof (Title), L"EFI loader on volume %u", (UINT32)Found);
    Entry->Id     = AsciiDup ("removable");
    Entry->Title  = AllocateCopyPool (StrSize (Title), Title);
    Entry->Type   = UniXNUEntryEfi;
    Entry->Volume = Handles[Index];
    Entry->Path   = AllocateCopyPool (sizeof (UNIXNU_FALLBACK_LOADER), UNIXNU_FALLBACK_LOADER);
  }

  for (Index = 0; Index < Actions; Index++) {
    Entry = GrowArray ((VOID **)&Config->Entries, &Config->EntryCount, sizeof (UNIXNU_ENTRY));
    if (Entry != NULL) {
      CopyMem (Entry, &Saved[Index], sizeof (UNIXNU_ENTRY));
    }
  }

  if (Handles != NULL) {
    FreePool (Handles);
  }

  if (SelfPath != NULL) {
    FreePool (SelfPath);
  }

  return Found;
}

// ---------------------------------------------------------------------------
// Top level
// ---------------------------------------------------------------------------

STATIC
VOID
ApplyRoot (
  IN UNIXNU_CONFIG  *Config,
  IN TOML_NODE  *Root
  )
{
  TOML_NODE    *Boot;
  TOML_NODE    *Ui;
  TOML_NODE    *List;
  TOML_NODE    *Item;
  TOML_NODE    *Acpi;
  TOML_NODE    *Default;
  CONST CHAR8  *Console;
  CONST CHAR8  *Layout;
  UINTN        Index;

  if (TomlGetInteger (Root, "version", 0) != UNIXNU_SCHEMA_VERSION) {
    ConfigError (Config, "expected 'version = %d'", UNIXNU_SCHEMA_VERSION);
  }

  Boot                    = TomlGet (Root, "boot");
  Config->Timeout         = (INTN)TomlGetInteger (Boot, "timeout", 5);
  Config->RotateSeconds   = (UINTN)MAX (0, TomlGetInteger (Boot, "rotate", 0));
  Config->FallbackTimeout = (UINTN)MAX (1, TomlGetInteger (Boot, "fallback_timeout", 10));
  Config->ConnectAll      = TomlGetBoolean (Boot, "connect_all", TRUE);

  Ui              = TomlGet (Root, "ui");
  Config->Title   = UniXNUAsciiToUnicode (TomlGetString (Ui, "title", "UniXNU"));
  Config->Scale   = (UINTN)MAX (0, TomlGetInteger (Ui, "scale", 0));
  Config->ShowLogo = TomlGetBoolean (Ui, "logo", TRUE);
  Layout          = TomlGetString (Ui, "layout", "auto");
  if (AsciiStrCmp (Layout, "landscape") == 0) {
    Config->Layout = UniXNULayoutLandscape;
  } else if (AsciiStrCmp (Layout, "portrait") == 0) {
    Config->Layout = UniXNULayoutPortrait;
  } else {
    Config->Layout = UniXNULayoutAuto;
    if (AsciiStrCmp (Layout, "auto") != 0) {
      ConfigError (Config, "[ui] layout '%a' is not auto, landscape or portrait", Layout);
    }
  }

  Config->PortraitBelow = (UINTN)MAX (1, TomlGetInteger (Ui, "portrait_below", UNIXNU_PORTRAIT_BELOW_DEFAULT));
  Console         = TomlGetString (Ui, "console", "auto");
  if (AsciiStrCmp (Console, "graphics") == 0) {
    Config->Console = UniXNUConsoleGraphics;
  } else if (AsciiStrCmp (Console, "text") == 0) {
    Config->Console = UniXNUConsoleText;
  } else if (AsciiStrCmp (Console, "none") == 0) {
    Config->Console = UniXNUConsoleNone;
  } else {
    Config->Console = UniXNUConsoleAuto;
  }

  List = TomlGet (Root, "driver");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddDriver (Config, Item, Config->Volume, UNIXNU_CONFIG_DIR, "config", "path");
  }

  List = TomlGet (Root, "dt_patch");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddDtPatch (Config, Item, Config->Volume, UNIXNU_CONFIG_DIR, "config", &Config->Patches, &Config->PatchCount);
  }

  List = TomlGet (Root, "block_slice");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    UNIXNU_BLOCK_SLICE  *Slice;
    CONST CHAR8     *Partition;
    INT64           Offset;
    INT64           Length;

    if (!TomlGetBoolean (Item, "enabled", TRUE)) {
      continue;
    }

    Partition = TomlGetString (Item, "partition", NULL);
    Offset    = TomlGetInteger (Item, "offset", 0);
    Length    = TomlGetInteger (Item, "length", 0);
    if ((Partition == NULL) || (Offset < 0) || (Length < 0)) {
      ConfigError (Config, "block_slice needs 'partition' and non-negative offset/length (line %u)", (UINT32)Item->Line);
      continue;
    }

    Slice = GrowArray ((VOID **)&Config->Slices, &Config->SliceCount, sizeof (UNIXNU_BLOCK_SLICE));
    if (Slice != NULL) {
      Slice->Partition = UniXNUAsciiToUnicode (Partition);
      Slice->Name      = UniXNUAsciiToUnicode (TomlGetString (Item, "name", Partition));
      Slice->Offset    = (UINT64)Offset;
      Slice->Length    = (UINT64)Length;
      Slice->Writable  = TomlGetBoolean (Item, "writable", FALSE);
    }
  }

  Acpi = TomlGet (TomlGet (Root, "acpi"), "add");
  for (Item = (Acpi != NULL) ? Acpi->Child : NULL; Item != NULL; Item = Item->Next) {
    if (Item->Type == TomlString) {
      AddAcpi (Config, Config->Volume, UNIXNU_CONFIG_DIR, Item->String, "config");
    }
  }

  //
  // Kits after the config's own drivers and patches, so a config can stage
  // prerequisites (for example a file system driver) ahead of them.
  //
  LoadKits (Config, Root);

  List = TomlGet (Root, "entry");
  for (Item = (List != NULL) ? List->Child : NULL; Item != NULL; Item = Item->Next) {
    AddEntry (Config, Item);
  }

  Default = TomlGet (Boot, "default");
  Config->DefaultIndex = 0;
  if ((Default != NULL) && (Default->Type == TomlString)) {
    for (Index = 0; Index < Config->EntryCount; Index++) {
      if ((Config->Entries[Index].Id != NULL) && (AsciiStrCmp (Config->Entries[Index].Id, Default->String) == 0)) {
        Config->DefaultIndex = Index;
        break;
      }
    }

    if (Index == Config->EntryCount) {
      ConfigError (Config, "default entry '%a' not found", Default->String);
    }
  } else if ((Default != NULL) && (Default->Type == TomlInteger) && ((UINTN)Default->Integer < Config->EntryCount)) {
    Config->DefaultIndex = (UINTN)Default->Integer;
  }
}

STATIC
BOOLEAN
TryVolume (
  IN UNIXNU_CONFIG   *Config,
  IN EFI_HANDLE  Volume
  )
{
  EFI_STATUS  Status;
  CHAR8       *Text;
  UINTN       Size;
  TOML_NODE   *Root;
  CHAR8       Error[96];

  Status = UniXNUReadFile (Volume, (CONST CHAR16 *)PcdGetPtr (PcdUniXNUConfigPath), (VOID **)&Text, &Size);
  if (EFI_ERROR (Status)) {
    return FALSE;
  }

  Config->Volume = Volume;
  Status         = TomlParse (Text, Size, &Root, Error, sizeof (Error));
  FreePool (Text);
  if (EFI_ERROR (Status)) {
    ConfigError (Config, "unixnu.toml %a", Error);
    return FALSE;
  }

  UniXNULog ("config: loaded %s", (CONST CHAR16 *)PcdGetPtr (PcdUniXNUConfigPath));
  ApplyRoot (Config, Root);
  TomlFree (Root);
  return TRUE;
}

VOID
UniXNUConfigLoad (
  IN  EFI_HANDLE  ImageHandle,
  OUT UNIXNU_CONFIG   *Config
  )
{
  EFI_STATUS                 Status;
  EFI_LOADED_IMAGE_PROTOCOL  *Self;
  EFI_HANDLE                 *Handles;
  UINTN                      Count;
  UINTN                      Index;
  BOOLEAN                    Loaded;
  TOML_NODE                  *Root;
  CHAR8                      Error[96];
  CHAR16                     Label[64];

  ZeroMem (Config, sizeof (*Config));
  Loaded = FALSE;

  //
  // The volume UniXNU was started from wins; then every other volume.
  //
  if (!EFI_ERROR (gBS->HandleProtocol (ImageHandle, &gEfiLoadedImageProtocolGuid, (VOID **)&Self))) {
    Loaded = TryVolume (Config, Self->DeviceHandle);
  }

  if (!Loaded && (Config->Error[0] == '\0')) {
    Status = gBS->LocateHandleBuffer (ByProtocol, &gEfiSimpleFileSystemProtocolGuid, NULL, &Count, &Handles);
    if (!EFI_ERROR (Status)) {
      for (Index = 0; Index < Count && !Loaded && Config->Error[0] == '\0'; Index++) {
        Loaded = TryVolume (Config, Handles[Index]);
      }

      FreePool (Handles);
    }
  }

  if (Loaded) {
    UnicodeSPrint (Label, sizeof (Label), L"config: %s", (CONST CHAR16 *)PcdGetPtr (PcdUniXNUConfigPath));
  } else {
    //
    // Built-in fallback. A parse error of a real file is kept in Error so the
    // menu can show it.
    //
    CHAR8  Saved[sizeof (Config->Error)];

    CopyMem (Saved, Config->Error, sizeof (Saved));
    ZeroMem (Config, sizeof (*Config));
    CopyMem (Config->Error, Saved, sizeof (Saved));

    Status = TomlParse (mBuiltinConfig, sizeof (mBuiltinConfig) - 1, &Root, Error, sizeof (Error));
    ASSERT_EFI_ERROR (Status);
    if (!EFI_ERROR (Status)) {
      ApplyRoot (Config, Root);
      TomlFree (Root);
    }

    if (AddFallbackLoaders (Config, ImageHandle) == 0) {
      //
      // Only the actions are left. Say so instead of showing a menu that
      // looks complete.
      //
      AsciiStrCpyS (Config->Notice, sizeof (Config->Notice), "no boot entry found");
      UniXNULog ("config: no boot entry found");
    }

    Config->DefaultIndex = 0;
    UnicodeSPrint (Label, sizeof (Label), L"built-in configuration");
    UniXNULog ("config: none found, using built-in configuration");
  }

  Config->SourceLabel = AllocateCopyPool (StrSize (Label), Label);

  //
  // A configuration without entries would leave nothing to show.
  //
  if (Config->EntryCount == 0) {
    UNIXNU_ENTRY  *Entry;

    ConfigError (Config, "no entries defined");
    Entry = GrowArray ((VOID **)&Config->Entries, &Config->EntryCount, sizeof (UNIXNU_ENTRY));
    if (Entry != NULL) {
      Entry->Id     = AsciiDup ("exit");
      Entry->Title  = AllocateCopyPool (sizeof (L"Return to firmware"), L"Return to firmware");
      Entry->Type   = UniXNUEntryAction;
      Entry->Action = UniXNUActionExit;
    }
  }

  if (Config->DefaultIndex >= Config->EntryCount) {
    Config->DefaultIndex = 0;
  }

  //
  // The countdown must never boot an entry that asks for confirmation: fall back to the first entry that does not.
  //
  if ((Config->EntryCount > 0) && (Config->Entries[Config->DefaultIndex].Confirm != NULL)) {
    UINTN  Safe;

    for (Safe = 0; Safe < Config->EntryCount; Safe++) {
      if (Config->Entries[Safe].Confirm == NULL) {
        ConfigError (Config, "default entry needs confirmation, using '%a'", (Config->Entries[Safe].Id != NULL) ? Config->Entries[Safe].Id : "?");
        Config->DefaultIndex = Safe;
        break;
      }
    }
  }
}
