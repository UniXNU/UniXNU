/** @file
  Menu loop: input, countdown and idle rotation.

  Degradation rules (see README):
  - No input device: the timeout always runs (fallback_timeout replaces a
    negative timeout) and the highlight rotates through the entries.
  - Any key press stops both the countdown and the rotation.
  - The countdown always boots the default entry; rotation is display only.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include "Internal.h"

#define TICK_MS             100
#define DEFAULT_ROTATE_SEC  2

#ifndef SCAN_SUSPEND
#define SCAN_SUSPEND  0x0102
#endif

//
// Physical input = a SimpleTextIn instance that sits on a device path; the
// ConSplitter's virtual handle has none.
//
STATIC
UINTN
CountInputDevices (
  VOID
  )
{
  EFI_STATUS  Status;
  EFI_HANDLE  *Handles;
  UINTN       Count;
  UINTN       Index;
  UINTN       Physical;
  VOID        *Path;

  if (gST->ConIn == NULL) {
    return 0;
  }

  Status = gBS->LocateHandleBuffer (ByProtocol, &gEfiSimpleTextInProtocolGuid, NULL, &Count, &Handles);
  if (EFI_ERROR (Status)) {
    return 0;
  }

  Physical = 0;
  for (Index = 0; Index < Count; Index++) {
    if (!EFI_ERROR (gBS->HandleProtocol (Handles[Index], &gEfiDevicePathProtocolGuid, &Path))) {
      Physical++;
    }
  }

  FreePool (Handles);
  return Physical;
}

STATIC
VOID
DrawCountdown (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN INTN       RemainingMs,
  IN BOOLEAN    HasInput
  )
{
  CHAR16  Line[128];

  if (RemainingMs >= 0) {
    UnicodeSPrint (
      Line,
      sizeof (Line),
      L"Booting %s in %u s",
      Config->Entries[Config->DefaultIndex].Title,
      (UINT32)((RemainingMs + 999) / 1000)
      );
  } else {
    UnicodeSPrint (Line, sizeof (Line), L"Select an entry");
  }

  UniXNUUiDrawStatus (Ui, 0, Line);
}

UINTN
UniXNUMenuRun (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN BOOLEAN    Countdown
  )
{
  EFI_STATUS     Status;
  EFI_EVENT      Timer;
  EFI_EVENT      Events[2];
  UINTN          EventCount;
  UINTN          Signaled;
  EFI_INPUT_KEY  Key;
  UINTN          Selected;
  UINTN          Previous;
  UINTN          Index;
  BOOLEAN        HasInput;
  BOOLEAN        UserActive;
  INTN           RemainingMs;
  UINTN          RotateMs;
  UINTN          RotateAccum;
  INTN           LastShownSecond;
  UINTN          Count;

  Count    = Config->EntryCount;
  Selected = Config->DefaultIndex;
  HasInput = (CountInputDevices () > 0);

  if (!Countdown) {
    RemainingMs = HasInput ? -1 : (INTN)Config->FallbackTimeout * 1000;
  } else if (Config->Timeout < 0) {
    RemainingMs = HasInput ? -1 : (INTN)Config->FallbackTimeout * 1000;
  } else {
    RemainingMs = Config->Timeout * 1000;
  }

  RotateMs = Config->RotateSeconds * 1000;
  if (!HasInput && (RotateMs == 0)) {
    RotateMs = DEFAULT_ROTATE_SEC * 1000;
  }

  UniXNUUiDrawFrame (Ui, Config);
  for (Index = 0; Index < Count; Index++) {
    UniXNUUiDrawEntry (Ui, Config, Index, Index == Selected);
  }

  UniXNUUiDrawStatus (
    Ui,
    1,
    HasInput ? L"Up/Down: select    Enter: boot    1-9: boot entry    Esc: stop timer"
             : L"No input device: the default entry boots when the timer ends"
    );
  if (Ui->Notice[0] != L'\0') {
    UniXNUUiDrawStatus (Ui, 2, Ui->Notice);
  }

  UniXNULog (
    "menu: shown %u entries, default %u '%a', timeout %d ms, input %a, rotate %u ms",
    (UINT32)Count,
    (UINT32)Config->DefaultIndex,
    (Config->Entries[Config->DefaultIndex].Id != NULL) ? Config->Entries[Config->DefaultIndex].Id : "?",
    (INT32)RemainingMs,
    HasInput ? "yes" : "no",
    (UINT32)RotateMs
    );

  if (RemainingMs == 0) {
    UniXNULog ("menu: timeout 0, booting default");
    return Config->DefaultIndex;
  }

  Status = gBS->CreateEvent (EVT_TIMER, TPL_CALLBACK, NULL, NULL, &Timer);
  if (EFI_ERROR (Status)) {
    return Config->DefaultIndex;
  }

  gBS->SetTimer (Timer, TimerPeriodic, EFI_TIMER_PERIOD_MILLISECONDS (TICK_MS));

  EventCount = 0;
  Events[EventCount++] = Timer;
  if (gST->ConIn != NULL) {
    Events[EventCount++] = gST->ConIn->WaitForKey;
  }

  UserActive      = FALSE;
  RotateAccum     = 0;
  LastShownSecond = -2;
  for ( ; ;) {
    INTN  Second = (RemainingMs < 0) ? -1 : (RemainingMs + 999) / 1000;

    if (Second != LastShownSecond) {
      DrawCountdown (Ui, Config, RemainingMs, HasInput);
      LastShownSecond = Second;
    }

    Status = gBS->WaitForEvent (EventCount, Events, &Signaled);
    if (EFI_ERROR (Status)) {
      break;
    }

    Previous = Selected;
    if (Signaled == 0) {
      if (RemainingMs > 0) {
        RemainingMs -= TICK_MS;
        if (RemainingMs <= 0) {
          UniXNULog ("menu: timeout, booting default %u", (UINT32)Config->DefaultIndex);
          Selected = Config->DefaultIndex;
          break;
        }
      }

      if (!UserActive && (RotateMs > 0) && (Count > 1)) {
        RotateAccum += TICK_MS;
        if (RotateAccum >= RotateMs) {
          RotateAccum = 0;
          Selected    = (Selected + 1) % Count;
        }
      }
    } else {
      if (EFI_ERROR (gST->ConIn->ReadKeyStroke (gST->ConIn, &Key))) {
        continue;
      }

      if (!UserActive) {
        //
        // The first key takes over: no more countdown or rotation, and the
        // highlight returns to the default before the key applies.
        //
        UserActive  = TRUE;
        RemainingMs = -1;
        Selected    = Config->DefaultIndex;
      }

      if ((Key.ScanCode == SCAN_UP) || (Key.UnicodeChar == L'k')) {
        Selected = (Selected + Count - 1) % Count;
      } else if ((Key.ScanCode == SCAN_DOWN) || (Key.UnicodeChar == L'j')) {
        Selected = (Selected + 1) % Count;
      } else if (Key.ScanCode == SCAN_HOME) {
        Selected = 0;
      } else if (Key.ScanCode == SCAN_END) {
        Selected = Count - 1;
      } else if ((Key.UnicodeChar >= L'1') && (Key.UnicodeChar <= L'9') && ((UINTN)(Key.UnicodeChar - L'1') < Count)) {
        Selected = Key.UnicodeChar - L'1';
        UniXNULog ("menu: key %c, booting %u", Key.UnicodeChar, (UINT32)Selected);
        break;
      } else if ((Key.UnicodeChar == CHAR_CARRIAGE_RETURN) || (Key.UnicodeChar == CHAR_LINEFEED) ||
                 (Key.UnicodeChar == L' ') || (Key.ScanCode == SCAN_RIGHT) || (Key.ScanCode == SCAN_SUSPEND))
      {
        UniXNULog ("menu: enter, booting %u", (UINT32)Selected);
        break;
      }
    }

    if (Selected != Previous) {
      UniXNUUiDrawEntry (Ui, Config, Previous, FALSE);
      UniXNUUiDrawEntry (Ui, Config, Selected, TRUE);
    }
  }

  gBS->SetTimer (Timer, TimerCancel, 0);
  gBS->CloseEvent (Timer);
  return Selected;
}

//
// The Tools submenu reuses the ordinary menu loop against a temporary config
// whose entries are the installed menu plugins plus a leading Back entry. The
// selected plugin draws between the header and footer; DrawStatus lets it
// update the footer without owning it.
//
STATIC UNIXNU_UI  *mToolsUi;

STATIC
VOID
EFIAPI
ToolsDrawStatus (
  IN CONST UNIXNU_MENU_PLUGIN_PROTOCOL  *This,
  IN UINTN                              Line,
  IN CONST CHAR16                       *Text
  )
{
  (VOID)This;
  if (mToolsUi != NULL) {
    UniXNUUiDrawStatus (mToolsUi, Line, Text);
  }
}

VOID
UniXNUMenuRunTools (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  )
{
  EFI_STATUS                   Status;
  EFI_HANDLE                   *Handles;
  UINTN                        HandleCount;
  UINTN                        Index;
  UINTN                        PluginCount;
  UNIXNU_MENU_PLUGIN_PROTOCOL  **Plugins;
  UNIXNU_ENTRY                 *Entries;
  UNIXNU_CONFIG                Tools;
  UNIXNU_PLUGIN_RECT           Content;
  UINTN                        Selected;
  CHAR16                       SavedNotice[sizeof (Ui->Notice) / sizeof (Ui->Notice[0])];

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  Handles     = NULL;
  Plugins     = NULL;
  Entries     = NULL;
  PluginCount = 0;

  Status = gBS->LocateHandleBuffer (
                  ByProtocol,
                  &gUniXNUMenuPluginProtocolGuid,
                  NULL,
                  &HandleCount,
                  &Handles
                  );
  if (EFI_ERROR (Status) || (HandleCount == 0)) {
    UniXNULog ("tools: no menu plugins installed");
    goto Done;
  }

  Plugins = AllocateZeroPool (HandleCount * sizeof (*Plugins));
  if (Plugins == NULL) {
    goto Done;
  }

  for (Index = 0; Index < HandleCount; Index++) {
    UNIXNU_MENU_PLUGIN_PROTOCOL  *Plugin;

    if (EFI_ERROR (gBS->HandleProtocol (Handles[Index], &gUniXNUMenuPluginProtocolGuid, (VOID **)&Plugin)) ||
        (Plugin == NULL) ||
        (Plugin->Signature != UNIXNU_MENU_PLUGIN_PROTOCOL_SIGNATURE) ||
        (Plugin->Version != UNIXNU_MENU_PLUGIN_PROTOCOL_VERSION) ||
        (Plugin->Run == NULL))
    {
      continue;
    }

    Plugins[PluginCount++] = Plugin;
  }

  if (PluginCount == 0) {
    UniXNULog ("tools: %u handle(s), none usable", (UINT32)HandleCount);
    goto Done;
  }

  Entries = AllocateZeroPool ((PluginCount + 1) * sizeof (*Entries));
  if (Entries == NULL) {
    goto Done;
  }

  //
  // Back is first so a first key press cannot launch a tool; the default
  // highlight starts on Back and any Up/Down/Enter press takes over cleanly.
  //
  Entries[0].Id     = "back";
  Entries[0].Title  = L"Back";
  Entries[0].Type   = UniXNUEntryAction;
  Entries[0].Action = UniXNUActionNone;
  for (Index = 0; Index < PluginCount; Index++) {
    Entries[Index + 1].Id     = "tool";
    Entries[Index + 1].Title  = (CHAR16 *)Plugins[Index]->Title;
    Entries[Index + 1].Type   = UniXNUEntryAction;
    Entries[Index + 1].Action = UniXNUActionNone;
  }

  Tools              = *Config;
  Tools.Entries      = Entries;
  Tools.EntryCount   = PluginCount + 1;
  Tools.DefaultIndex = 0;
  Tools.Timeout      = -1;
  Tools.Error[0]     = '\0';
  Tools.Notice[0]    = '\0';

  CopyMem (SavedNotice, Ui->Notice, sizeof (SavedNotice));
  Ui->Notice[0] = L'\0';
  for ( ; ;) {
    Selected = UniXNUMenuRun (Ui, &Tools, FALSE);
    if ((Selected == 0) || (Selected > PluginCount)) {
      break;
    }

    Content.X      = 0;
    Content.Y      = (UINT32)Ui->ContentTop;
    Content.Width  = Ui->Width;
    Content.Height = (UINT32)((Ui->ContentBottom > Ui->ContentTop) ? Ui->ContentBottom - Ui->ContentTop : 0);

    mToolsUi = Ui;
    Plugins[Selected - 1]->Run (
                            Plugins[Selected - 1],
                            Ui->Gop,
                            &Content,
                            ToolsDrawStatus
                            );
    mToolsUi = NULL;
  }

  CopyMem (Ui->Notice, SavedNotice, sizeof (SavedNotice));

Done:
  if (Entries != NULL) {
    FreePool (Entries);
  }

  if (Plugins != NULL) {
    FreePool (Plugins);
  }

  if (Handles != NULL) {
    FreePool (Handles);
  }
}

BOOLEAN
UniXNUMenuConfirm (
  IN  UNIXNU_UI      *Ui,
  IN  UNIXNU_ENTRY   *Entry,
  OUT UINTN      *Choice
  )
{
  EFI_INPUT_KEY  Key;
  UINTN          Index;
  UINTN          Shown;
  UINTN          Items;
  CHAR16         Line[160];

  *Choice = 0;
  if ((gST->ConIn == NULL) || (CountInputDevices () == 0)) {
    UniXNULog ("menu: confirmation needs an input device, cancelled");
    return FALSE;
  }

  //
  // With choices the items are the choices and then Cancel, and Cancel is shown first, so the first press cannot confirm anything.
  //
  Items = (Entry->ConfirmCount > 0) ? Entry->ConfirmCount + 1 : 0;
  Shown = Items > 0 ? Items - 1 : 0;

  UnicodeSPrint (Line, sizeof (Line), L"%s", Entry->Confirm);
  UniXNUUiDrawStatus (Ui, 0, Line);
  UniXNUUiDrawStatus (Ui, 2, Items > 0 ? L"Volume keys: choose     Power key: confirm" : L"Power key = confirm     any other key = cancel");

  //
  // The press that chose the entry, and anything typed since, must not answer the question.
  //
  gBS->Stall (500000);
  while (!EFI_ERROR (gST->ConIn->ReadKeyStroke (gST->ConIn, &Key))) {
  }

  for ( ; ;) {
    if (Items > 0) {
      UnicodeSPrint (Line, sizeof (Line), L"<  %s  >", (Shown + 1 == Items) ? L"Cancel" : Entry->ConfirmTitles[Shown]);
      UniXNUUiDrawStatus (Ui, 1, Line);
    } else {
      UniXNUUiDrawStatus (Ui, 1, L"");
    }

    if (EFI_ERROR (gBS->WaitForEvent (1, &gST->ConIn->WaitForKey, &Index))) {
      return FALSE;
    }

    if (EFI_ERROR (gST->ConIn->ReadKeyStroke (gST->ConIn, &Key))) {
      continue;
    }

    if (Items > 0) {
      if (Key.ScanCode == SCAN_UP) {
        Shown = (Shown + Items - 1) % Items;
        continue;
      }

      if (Key.ScanCode == SCAN_DOWN) {
        Shown = (Shown + 1) % Items;
        continue;
      }
    }

    if ((Key.UnicodeChar == CHAR_CARRIAGE_RETURN) || (Key.UnicodeChar == CHAR_LINEFEED)) {
      if (Items > 0) {
        if (Shown + 1 == Items) {
          return FALSE;
        }

        *Choice = Shown;
      }

      UniXNULog ("menu: confirmed '%a' choice %u", (Entry->Id != NULL) ? Entry->Id : "?", (UINT32)*Choice);
      return TRUE;
    }

    return FALSE;
  }
}
