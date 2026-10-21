/** @file
  Smoke-test payload for UniXNU.

  Load options are "<words>": "expect=a,b,c" selects which hand-over checks
  must pass (dtb, overlay, driver, initrd, var, slice), "pause" keeps the
  report on screen for 15 s before returning, "shutdown" powers the machine
  off at the end so an emulator run terminates. Every line it prints starts
  with "UNIXNU-HELLO:" for log matching.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include <Uefi.h>
#include <Guid/UniXNUBlockSlice.h>
#include <Guid/Fdt.h>
#include <Guid/LinuxEfiInitrdMedia.h>
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/DevicePathLib.h>
#include <Library/FdtLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/PrintLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Protocol/BlockIo.h>
#include <Protocol/UniXNUSample.h>
#include <Protocol/LoadedImage.h>
#include <Protocol/LoadFile2.h>

extern EFI_GUID  gUniXNUVariableGuid;

#pragma pack (1)
typedef struct {
  VENDOR_DEVICE_PATH          VenMedia;
  EFI_DEVICE_PATH_PROTOCOL    End;
} INITRD_DEVICE_PATH;
#pragma pack ()

STATIC CONST INITRD_DEVICE_PATH  mInitrdPath = {
  {
    { MEDIA_DEVICE_PATH, MEDIA_VENDOR_DP, { sizeof (VENDOR_DEVICE_PATH), 0 }
    },
    LINUX_EFI_INITRD_MEDIA_GUID
  },
  { END_DEVICE_PATH_TYPE, END_ENTIRE_DEVICE_PATH_SUBTYPE, { sizeof (EFI_DEVICE_PATH_PROTOCOL), 0 }
  }
};

STATIC UINTN  mPassed;
STATIC UINTN  mFailed;

STATIC
VOID
Report (
  IN CONST CHAR16  *Check,
  IN BOOLEAN       Ok,
  IN CONST CHAR16  *Detail
  )
{
  Print (L"UNIXNU-HELLO: check %s %s (%s)\n", Check, Ok ? L"PASS" : L"FAIL", Detail);
  if (Ok) {
    mPassed++;
  } else {
    mFailed++;
  }
}

STATIC
CONST CHAR8 *
FdtString (
  IN VOID         *Fdt,
  IN CONST CHAR8  *Node,
  IN CONST CHAR8  *Prop
  )
{
  INT32  Offset;
  INT32  Len;

  Offset = FdtPathOffset (Fdt, Node);
  if (Offset < 0) {
    return NULL;
  }

  return FdtGetProp (Fdt, Offset, Prop, &Len);
}

STATIC
VOID
CheckDtb (
  IN BOOLEAN  WantOverlay
  )
{
  VOID         *Fdt;
  CONST CHAR8  *Bootargs;
  CONST CHAR8  *Marker;
  CONST CHAR8  *Overlay;
  CHAR16       Detail[200];

  if (EFI_ERROR (EfiGetSystemConfigurationTable (&gFdtTableGuid, &Fdt)) || (FdtCheckHeader (Fdt) != 0)) {
    Report (L"dtb", FALSE, L"no EFI_DTB_TABLE");
    if (WantOverlay) {
      Report (L"overlay", FALSE, L"no EFI_DTB_TABLE");
    }

    return;
  }

  Bootargs = FdtString (Fdt, "/chosen", "bootargs");
  Marker   = FdtString (Fdt, "/unixnu-test", "marker");
  UnicodeSPrint (
    Detail,
    sizeof (Detail),
    L"bootargs='%a' marker='%a'",
    (Bootargs != NULL) ? Bootargs : "(none)",
    (Marker != NULL) ? Marker : "(none)"
    );
  Report (L"dtb", Bootargs != NULL && Marker != NULL && AsciiStrCmp (Marker, "patched") == 0, Detail);

  if (WantOverlay) {
    Overlay = FdtString (Fdt, "/unixnu-overlay", "status");
    UnicodeSPrint (Detail, sizeof (Detail), L"/unixnu-overlay status='%a'", (Overlay != NULL) ? Overlay : "(none)");
    Report (L"overlay", Overlay != NULL && AsciiStrCmp (Overlay, "applied") == 0, Detail);
  }
}

STATIC
VOID
CheckDriver (
  VOID
  )
{
  UNIXNU_SAMPLE_PROTOCOL  *Sample;
  CHAR16                     Detail[160];

  if (EFI_ERROR (gBS->LocateProtocol (&gUniXNUSampleProtocolGuid, NULL, (VOID **)&Sample)) ||
      (Sample->Signature != UNIXNU_SAMPLE_SIGNATURE))
  {
    Report (L"driver", FALSE, L"sample protocol missing");
    return;
  }

  UnicodeSPrint (Detail, sizeof (Detail), L"sample driver args='%s'", (Sample->LoadOptions != NULL) ? Sample->LoadOptions : L"(none)");
  Report (L"driver", TRUE, Detail);
}

STATIC
VOID
CheckInitrd (
  VOID
  )
{
  EFI_STATUS                Status;
  EFI_DEVICE_PATH_PROTOCOL  *Path;
  EFI_HANDLE                Handle;
  EFI_LOAD_FILE2_PROTOCOL   *LoadFile2;
  UINTN                     Size;
  CHAR8                     *Data;
  CHAR16                    Detail[120];
  UINTN                     Index;

  Path   = (EFI_DEVICE_PATH_PROTOCOL *)&mInitrdPath;
  Status = gBS->LocateDevicePath (&gEfiLoadFile2ProtocolGuid, &Path, &Handle);
  if (EFI_ERROR (Status)) {
    Report (L"initrd", FALSE, L"no initrd media");
    return;
  }

  gBS->HandleProtocol (Handle, &gEfiLoadFile2ProtocolGuid, (VOID **)&LoadFile2);
  Size   = 0;
  Status = LoadFile2->LoadFile (LoadFile2, Path, FALSE, &Size, NULL);
  if ((Status != EFI_BUFFER_TOO_SMALL) || (Size == 0)) {
    Report (L"initrd", FALSE, L"size probe failed");
    return;
  }

  Data   = AllocateZeroPool (Size + 1);
  Status = LoadFile2->LoadFile (LoadFile2, Path, FALSE, &Size, Data);
  for (Index = 0; Index < Size; Index++) {
    if ((Data[Index] < 0x20) || (Data[Index] > 0x7E)) {
      Data[Index] = '\0';
      break;
    }
  }

  UnicodeSPrint (Detail, sizeof (Detail), L"%u bytes, '%.40a'", (UINT32)Size, Data);
  Report (L"initrd", !EFI_ERROR (Status), Detail);
  FreePool (Data);
}

STATIC
VOID
CheckVariable (
  VOID
  )
{
  EFI_STATUS  Status;
  CHAR8       Value[64];
  UINTN       Size;
  UINT32      Attributes;
  CHAR16      Detail[120];

  ZeroMem (Value, sizeof (Value));
  Size   = sizeof (Value) - 1;
  Status = gRT->GetVariable (L"UniXNUTest", &gUniXNUVariableGuid, &Attributes, &Size, Value);
  UnicodeSPrint (Detail, sizeof (Detail), L"UniXNUTest='%a' attr 0x%x: %r", Value, Attributes, Status);
  Report (L"var", !EFI_ERROR (Status), Detail);
}

//
// A [[block_slice]] device whose first block starts with the tail marker.
//
STATIC
VOID
CheckSlice (
  VOID
  )
{
  EFI_STATUS                         Status;
  EFI_HANDLE                         *Handles;
  UINTN                              Count;
  UINTN                              Index;
  EFI_DEVICE_PATH_PROTOCOL           *Node;
  UNIXNU_BLOCK_SLICE_DEVICE_PATH  *Slice;
  EFI_BLOCK_IO_PROTOCOL              *BlockIo;
  CHAR8                              *Block;
  CHAR16                             Detail[160];
  BOOLEAN                            Found;

  Found  = FALSE;
  Status = gBS->LocateHandleBuffer (ByProtocol, &gEfiBlockIoProtocolGuid, NULL, &Count, &Handles);
  if (EFI_ERROR (Status)) {
    Count = 0;
  }

  for (Index = 0; Index < Count && !Found; Index++) {
    if (EFI_ERROR (gBS->HandleProtocol (Handles[Index], &gEfiDevicePathProtocolGuid, (VOID **)&Node))) {
      continue;
    }

    while (!IsDevicePathEnd (NextDevicePathNode (Node))) {
      Node = NextDevicePathNode (Node);
    }

    Slice = (UNIXNU_BLOCK_SLICE_DEVICE_PATH *)Node;
    if ((DevicePathType (Node) != MEDIA_DEVICE_PATH) || (DevicePathSubType (Node) != MEDIA_VENDOR_DP) ||
        !CompareGuid (&Slice->Header.Guid, &gUniXNUBlockSliceGuid))
    {
      continue;
    }

    Found = TRUE;
    gBS->HandleProtocol (Handles[Index], &gEfiBlockIoProtocolGuid, (VOID **)&BlockIo);
    Block  = AllocateZeroPool (BlockIo->Media->BlockSize + 1);
    Status = BlockIo->ReadBlocks (BlockIo, BlockIo->Media->MediaId, 0, BlockIo->Media->BlockSize, Block);
    Block[MIN (BlockIo->Media->BlockSize, 40)] = '\0';
    UnicodeSPrint (
      Detail,
      sizeof (Detail),
      L"'%s' %lu blocks %a, block 0 '%a': %r",
      Slice->Name,
      BlockIo->Media->LastBlock + 1,
      BlockIo->Media->ReadOnly ? "ro" : "rw",
      Block,
      Status
      );
    Report (L"slice", !EFI_ERROR (Status) && AsciiStrnCmp (Block, "UNIXNU-TAIL", 11) == 0, Detail);
    FreePool (Block);
  }

  if (!Found) {
    Report (L"slice", FALSE, L"no block_slice device");
  }

  if (Count > 0) {
    FreePool (Handles);
  }
}

EFI_STATUS
EFIAPI
HelloPayloadEntry (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
  EFI_LOADED_IMAGE_PROTOCOL  *Loaded;
  CONST CHAR16               *Args;

  Args = L"";
  if (!EFI_ERROR (gBS->HandleProtocol (ImageHandle, &gEfiLoadedImageProtocolGuid, (VOID **)&Loaded)) &&
      (Loaded->LoadOptions != NULL) && (Loaded->LoadOptionsSize >= sizeof (CHAR16)))
  {
    Args = Loaded->LoadOptions;
  }

  if (gST->ConOut != NULL) {
    gST->ConOut->ClearScreen (gST->ConOut);
  }

  Print (L"UNIXNU-HELLO: Hello from the UniXNU test payload\n");
  Print (L"UNIXNU-HELLO: load options '%s'\n", Args);

  if (StrStr (Args, L"dtb") != NULL) {
    CheckDtb (StrStr (Args, L"overlay") != NULL);
  }

  if (StrStr (Args, L"driver") != NULL) {
    CheckDriver ();
  }

  if (StrStr (Args, L"initrd") != NULL) {
    CheckInitrd ();
  }

  if (StrStr (Args, L"var") != NULL) {
    CheckVariable ();
  }

  if (StrStr (Args, L"slice") != NULL) {
    CheckSlice ();
  }

  Print (L"UNIXNU-HELLO: RESULT %s %u passed %u failed\n", (mFailed == 0) ? L"PASS" : L"FAIL", (UINT32)mPassed, (UINT32)mFailed);

  if (StrStr (Args, L"pause") != NULL) {
    gBS->Stall (15 * 1000 * 1000);
  }

  if (StrStr (Args, L"shutdown") != NULL) {
    gBS->Stall (500000);
    gRT->ResetSystem (EfiResetShutdown, EFI_SUCCESS, 0, NULL);
  }

  return (mFailed == 0) ? EFI_SUCCESS : EFI_ABORTED;
}
