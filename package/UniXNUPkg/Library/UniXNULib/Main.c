/** @file
  UniXNURun() and logging.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include "Internal.h"

#include <Protocol/SerialIo.h>

STATIC EFI_SERIAL_IO_PROTOCOL  *mSerial;

VOID
UniXNULogInit (
  VOID
  )
{
  if (EFI_ERROR (gBS->LocateProtocol (&gEfiSerialIoProtocolGuid, NULL, (VOID **)&mSerial))) {
    mSerial = NULL;
  }
}

VOID
EFIAPI
UniXNULog (
  IN CONST CHAR8  *Format,
  ...
  )
{
  VA_LIST  Args;
  CHAR8    Line[256];
  UINTN    Prefix;
  UINTN    Size;

  Prefix = AsciiSPrint (Line, sizeof (Line), "UNIXNU: ");
  VA_START (Args, Format);
  AsciiVSPrint (Line + Prefix, sizeof (Line) - Prefix - 2, Format, Args);
  VA_END (Args);
  AsciiStrCatS (Line, sizeof (Line), "\r\n");

  DEBUG ((PcdGet32 (PcdUniXNUDebugLevel), "%a", Line));
  if (mSerial != NULL) {
    Size = AsciiStrLen (Line);
    mSerial->Write (mSerial, &Size, Line);
  }
}

EFI_STATUS
EFIAPI
UniXNURun (
  IN EFI_HANDLE      ImageHandle,
  IN UNIXNU_HOST  Host
  )
{
  EFI_STATUS       Status;
  UNIXNU_CONFIG        Config;
  UNIXNU_UI            Ui;
  UNIXNU_INJECT_STATS  Stats;
  UINTN            Index;
  BOOLEAN          Countdown;
  UNIXNU_ENTRY         *Entry;
  UNIXNU_ENTRY         BootCopy;

  //
  // A boot manager waits for people; the 5 minute BDS watchdog does not.
  //
  gBS->SetWatchdogTimer (0, 0, 0, NULL);
  UniXNULogInit ();
  UniXNULog (
    "UniXNU %a starting as %a, firmware %s rev 0x%x",
    UNIXNU_VERSION_STRING,
    (Host == UniXNUHostFirmware) ? "firmware boot option" : "application",
    (gST->FirmwareVendor != NULL) ? gST->FirmwareVendor : L"?",
    gST->FirmwareRevision
    );

  //
  // Started straight from BDS, storage may not be connected yet.
  //
  if (Host == UniXNUHostFirmware) {
    UniXNUConnectAll ();
  }

  UniXNUConfigLoad (ImageHandle, &Config);
  UniXNULog (
    "config: %u entries, %u drivers, %u dt patches, %u acpi tables, %u slices, %u kits loaded, %u skipped",
    (UINT32)Config.EntryCount,
    (UINT32)Config.DriverCount,
    (UINT32)Config.PatchCount,
    (UINT32)Config.AcpiCount,
    (UINT32)Config.SliceCount,
    (UINT32)Config.KitsLoaded,
    (UINT32)Config.KitsSkipped
    );

  UniXNUPublishSlices (&Config);

  //
  // Drivers before the UI: an injected driver may provide the display or
  // the input device the menu needs.
  //
  ZeroMem (&Stats, sizeof (Stats));
  UniXNUInjectDrivers (ImageHandle, &Config, &Stats);
  UniXNUInjectAcpi (&Config, &Stats);

  UniXNUUiInit (&Config, &Ui);

  UnicodeSPrint (
    Ui.Info,
    sizeof (Ui.Info),
    L"drivers %u loaded / %u failed    kits %u    acpi %u",
    (UINT32)Stats.DriversLoaded,
    (UINT32)Stats.DriversFailed,
    (UINT32)Config.KitsLoaded,
    (UINT32)Stats.AcpiInstalled
    );

  Countdown = TRUE;
  for ( ; ;) {
    Index  = UniXNUMenuRun (&Ui, &Config, Countdown);
    Entry  = &Config.Entries[Index];
    BootCopy = *Entry;
    if (Entry->Confirm != NULL) {
      UINTN  Choice;

      if (!UniXNUMenuConfirm (&Ui, Entry, &Choice)) {
        UniXNULog ("menu: entry %u not confirmed", (UINT32)Index);
        UnicodeSPrint (Ui.Notice, sizeof (Ui.Notice), L"'%s' cancelled", Entry->Title);
        Countdown = FALSE;
        continue;
      }

      if (Entry->ConfirmCount > 0) {
        //
        // The chosen option's arguments follow the entry's own, on a copy: the entry itself stays as configured.
        //
        UINTN  Length = (Entry->Args != NULL ? StrLen (Entry->Args) : 0) + 1 + StrLen (Entry->ConfirmArgs[Choice]) + 1;

        BootCopy.Args = AllocateZeroPool (Length * sizeof (CHAR16));
        if (BootCopy.Args != NULL) {
          UnicodeSPrint (BootCopy.Args, Length * sizeof (CHAR16), L"%s %s", Entry->Args != NULL ? Entry->Args : L"", Entry->ConfirmArgs[Choice]);
        } else {
          BootCopy.Args = Entry->Args;
        }
      }
    }

    if ((Entry->Type == UniXNUEntryAction) && (Entry->Action == UniXNUActionTools)) {
      UniXNUMenuRunTools (&Ui, &Config);
      Countdown = FALSE;
      continue;
    }

    Status = UniXNUBootEntry (ImageHandle, &Config, &BootCopy);
    if ((Entry->Type == UniXNUEntryAction) && (Entry->Action == UniXNUActionExit)) {
      return EFI_SUCCESS;
    }

    //
    // The payload returned or failed: back to the menu, without the
    // countdown so a broken default cannot loop on a machine with input.
    //
    UnicodeSPrint (Ui.Notice, sizeof (Ui.Notice), L"'%s' returned: %r", Entry->Title, Status);
    UniXNULog ("menu: entry %u returned %r", (UINT32)Index, Status);
    gBS->SetWatchdogTimer (0, 0, 0, NULL);
    Countdown = FALSE;
  }
}
