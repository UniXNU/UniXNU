/** @file
  QR renderer for the Advanced Logger log.

  The log is collected once, split into scannable chunks, and rotated on the
  panel as QR bitmaps. Power exits; volume keys make the rotation faster or
  slower.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include <Uefi.h>
#include <Protocol/AdvancedLogger.h>
#include <Protocol/UniXNUMenuPlugin.h>
#include <Library/AdvancedLoggerAccessLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/DebugLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/PrintLib.h>
#include <Library/QrEncoderLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Protocol/SimpleTextIn.h>

#define ONESEND_BLOCK_LENGTH  720
#define ONESEND_HEADER_LENGTH 28
#define ONESEND_CRC_LENGTH    4
#define ONESEND_FRAME_LENGTH  (ONESEND_HEADER_LENGTH + ONESEND_BLOCK_LENGTH + ONESEND_CRC_LENGTH)
#define NO_LOG_STALL_MS     3000

#define SPEED_BAR_GAP          24
#define SPEED_BAR_MAX_HEIGHT   40
#define SPEED_BAR_SEGMENTS     5
#define SPEED_GEAR_COUNT       5
#define SPEED_GEAR_INITIAL     2

STATIC EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mBackground = { 0x0F, 0x0C, 0x0B, 0 };
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mSpeedColors[SPEED_BAR_SEGMENTS] = {
  { 0xFF, 0xFF, 0xFF, 0 },  // pure white
  { 0xFF, 0x8C, 0x1F, 0 },  // bright blue
  { 0x5E, 0xC5, 0x22, 0 },  // vivid green
  { 0x0A, 0xD6, 0xFF, 0 },  // bright yellow
  { 0x30, 0x3B, 0xFF, 0 }   // warning red
};
STATIC CONST UINTN  mGearIntervals[SPEED_GEAR_COUNT] = {
  5000,  // gear 0: slowest
  2000,
  1000,  // gear 2: initial
  500,
  250    // gear 4: fastest
};

STATIC
VOID
Fill (
  IN EFI_GRAPHICS_OUTPUT_PROTOCOL  *Gop,
  IN UINT32                        X,
  IN UINT32                        Y,
  IN UINT32                        Width,
  IN UINT32                        Height,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL Color
  )
{
  Gop->Blt (Gop, &Color, EfiBltVideoFill, 0, 0, X, Y, Width, Height, 0);
}

STATIC
VOID
FillBuffer (
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer,
  IN UINTN                          Count,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Color
  )
{
  UINTN  Index;

  for (Index = 0; Index < Count; Index++) {
    Buffer[Index] = Color;
  }
}

STATIC
VOID
DrawSpeedBar (
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer,
  IN UINTN                          Stride,
  IN UINT32                         Height,
  IN UINT32                         X,
  IN UINT32                         Width,
  IN UINT32                         Baseline,
  IN UINTN                          Level
  )
{
  UINT32                          SegmentWidth;
  UINT32                          Rem;
  UINT32                          SegmentX;
  UINT32                          SegmentHeight;
  UINT32                          Top;
  UINT32                          Row;
  UINT32                          Col;
  UINTN                           Segment;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL   Color;

  if ((Baseline > Height) || (SPEED_BAR_MAX_HEIGHT > Baseline)) {
    return;
  }

  SegmentWidth = Width / SPEED_BAR_SEGMENTS;
  if (SegmentWidth == 0) {
    return;
  }

  if (Level > SPEED_BAR_SEGMENTS) {
    Level = SPEED_BAR_SEGMENTS;
  }
  if (Level == 0) {
    return;
  }

  Rem       = Width % SPEED_BAR_SEGMENTS;
  SegmentX  = X;
  for (Segment = 0; Segment < SPEED_BAR_SEGMENTS; Segment++) {
    SegmentWidth  = Width / SPEED_BAR_SEGMENTS;
    if (Segment < Rem) {
      SegmentWidth++;
    }

    SegmentHeight = SPEED_BAR_MAX_HEIGHT * (Segment + 1) / SPEED_BAR_SEGMENTS;
    Top           = Baseline - SegmentHeight;
    if ((Segment + 1) > Level) {
      SegmentX += SegmentWidth;
      continue;
    }

    Color = mSpeedColors[Segment];
    for (Row = 0; Row < SegmentHeight; Row++) {
      for (Col = 0; Col < SegmentWidth; Col++) {
        Buffer[(Top + Row) * Stride + SegmentX + Col] = Color;
      }
    }

    SegmentX += SegmentWidth;
  }
}

STATIC
UINT32
Crc32 (
  IN CONST UINT8  *Data,
  IN UINTN        Length
  )
{
  UINT32  Crc;
  UINTN   Index;
  UINTN   Bit;

  Crc = 0xFFFFFFFFu;
  for (Index = 0; Index < Length; Index++) {
    Crc ^= Data[Index];
    for (Bit = 0; Bit < 8; Bit++) {
      Crc = (Crc >> 1) ^ ((0u - (Crc & 1u)) & 0xEDB88320u);
    }
  }

  return Crc ^ 0xFFFFFFFFu;
}

STATIC
VOID
PutLe16 (
  OUT UINT8   *Dest,
  IN  UINT16  Value
  )
{
  Dest[0] = (UINT8)Value;
  Dest[1] = (UINT8)(Value >> 8);
}

STATIC
VOID
PutLe32 (
  OUT UINT8   *Dest,
  IN  UINT32  Value
  )
{
  Dest[0] = (UINT8)Value;
  Dest[1] = (UINT8)(Value >> 8);
  Dest[2] = (UINT8)(Value >> 16);
  Dest[3] = (UINT8)(Value >> 24);
}

STATIC
UINT8 *
BuildEnvelope (
  IN  CONST UINT8  *Log,
  IN  UINTN        LogLen,
  OUT UINTN        *EnvelopeLen
  )
{
  CONST CHAR8         *Model;
  EFI_TIME            Time;
  CHAR8               FileName[96];
  STATIC CONST CHAR8  Mime[]     = "text/plain";
  UINTN               NameLen;
  UINTN               MimeLen;
  UINTN               Total;
  UINTN               DataStart;
  UINT32              Checksum;
  UINT8               *Envelope;

  Model = (CONST CHAR8 *)FixedPcdGetPtr (PcdUniXNUDeviceModel);
  ZeroMem (&Time, sizeof (Time));
  gRT->GetTime (&Time, NULL);
  AsciiSPrint (
    FileName,
    sizeof (FileName),
    "%a-%04u%02u%02u-%02u%02u%02u.log",
    Model,
    (UINT32)Time.Year,
    (UINT32)Time.Month,
    (UINT32)Time.Day,
    (UINT32)Time.Hour,
    (UINT32)Time.Minute,
    (UINT32)Time.Second
    );

  NameLen = AsciiStrLen (FileName);
  MimeLen = sizeof (Mime) - 1;
  Total   = 26 + NameLen + MimeLen + LogLen;
  Envelope = AllocatePool (Total);
  if (Envelope == NULL) {
    return NULL;
  }

  Checksum = Crc32 (Log, LogLen);
  Envelope[0] = 'L';
  Envelope[1] = 'M';
  Envelope[2] = 'S';
  Envelope[3] = '1';
  Envelope[4] = 2;
  Envelope[5] = 0;
  PutLe16 (Envelope + 6, (UINT16)NameLen);
  PutLe16 (Envelope + 8, (UINT16)MimeLen);
  PutLe32 (Envelope + 10, (UINT32)LogLen);
  PutLe32 (Envelope + 14, Checksum);
  PutLe32 (Envelope + 18, (UINT32)LogLen);
  PutLe32 (Envelope + 22, Checksum);
  CopyMem (Envelope + 26, FileName, NameLen);
  DataStart = 26 + NameLen;
  CopyMem (Envelope + DataStart, Mime, MimeLen);
  DataStart += MimeLen;
  CopyMem (Envelope + DataStart, Log, LogLen);
  *EnvelopeLen = Total;
  return Envelope;
}

STATIC
VOID
BuildFrame (
  IN  CONST UINT8  *Payload,
  IN  UINTN        PayloadLen,
  IN  UINTN        BlockIndex,
  IN  UINT32       SessionId,
  IN  UINT32       PayloadChecksum,
  OUT UINT8        *Frame
  )
{
  UINTN   BlockCount;
  UINTN   Offset;
  UINTN   ChunkLen;
  UINT32  Sequence;
  UINT32  Checksum;

  BlockCount = (PayloadLen + ONESEND_BLOCK_LENGTH - 1) / ONESEND_BLOCK_LENGTH;
  Sequence   = (UINT32)(BlockIndex + BlockIndex / 4);
  ZeroMem (Frame, ONESEND_FRAME_LENGTH);
  Frame[0] = 'O';
  Frame[1] = 'S';
  Frame[2] = 2;
  Frame[3] = 0;
  PutLe32 (Frame + 4, SessionId);
  PutLe32 (Frame + 8, Sequence);
  PutLe32 (Frame + 12, (UINT32)BlockCount);
  PutLe16 (Frame + 16, ONESEND_BLOCK_LENGTH);
  PutLe16 (Frame + 18, 0);
  PutLe32 (Frame + 20, (UINT32)PayloadLen);
  PutLe32 (Frame + 24, PayloadChecksum);

  Offset   = BlockIndex * ONESEND_BLOCK_LENGTH;
  ChunkLen = MIN ((UINTN)ONESEND_BLOCK_LENGTH, PayloadLen - Offset);
  CopyMem (Frame + ONESEND_HEADER_LENGTH, Payload + Offset, ChunkLen);
  Checksum = Crc32 (Frame, ONESEND_HEADER_LENGTH + ONESEND_BLOCK_LENGTH);
  PutLe32 (Frame + ONESEND_HEADER_LENGTH + ONESEND_BLOCK_LENGTH, Checksum);
}

STATIC
EFI_STATUS
DrawPage (
  IN EFI_GRAPHICS_OUTPUT_PROTOCOL   *Gop,
  IN CONST UNIXNU_PLUGIN_RECT       *Content,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *BackBuffer,
  IN CONST UINT8                    *Payload,
  IN UINTN                          PayloadLen,
  IN UINTN                          Page,
  IN UINTN                          PageCount,
  IN UINT32                         SessionId,
  IN UINT32                         PayloadChecksum,
  IN UINTN                          SpeedLevel,
  IN UNIXNU_MENU_PLUGIN_PROTOCOL    *This,
  IN UNIXNU_MENU_PLUGIN_DRAW_STATUS DrawStatus
  )
{
  EFI_STATUS                     Status;
  UINT8                          Frame[ONESEND_FRAME_LENGTH];
  CHAR16                         StatusLine[48];
  INTN                           RegionSize;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Bitmap;
  UINTN                          Row;
  UINTN                          Stride;
  UINT32                         X;
  UINT32                         Y;
  UINT32                         Baseline;

  Stride = Content->Width;
  FillBuffer (BackBuffer, (UINTN)Content->Width * Content->Height, mBackground);

  if (Payload != NULL) {
    BuildFrame (Payload, PayloadLen, Page, SessionId, PayloadChecksum, Frame);

    RegionSize = (INTN)MIN (Content->Width, Content->Height);
    if (RegionSize > 1200) {
      RegionSize = 1200;
    }

    RegionSize -= RegionSize / 8;

    Bitmap = NULL;
    Status = QrEncodeData (
               QrAutoVersion,
               QrECLevel_L,
               QrByteMode,
               0,
               Frame,
               ONESEND_FRAME_LENGTH,
               RegionSize,
               &Bitmap
               );
    if (EFI_ERROR (Status) || (Bitmap == NULL)) {
      return Status;
    }

    X = (Content->Width > (UINT32)RegionSize) ? (Content->Width - (UINT32)RegionSize) / 2 : 0;
    Y = (Content->Height > (UINT32)RegionSize) ? (Content->Height - (UINT32)RegionSize) / 2 : 0;
    for (Row = 0; Row < (UINTN)RegionSize; Row++) {
      CopyMem (
        BackBuffer + (Y + Row) * Stride + X,
        Bitmap + Row * (UINTN)RegionSize,
        (UINTN)RegionSize * sizeof (*Bitmap)
        );
    }

    FreePool (Bitmap);

    Baseline = Y + (UINT32)RegionSize + SPEED_BAR_GAP + SPEED_BAR_MAX_HEIGHT;
    if (Baseline > Content->Height) {
      Baseline = Content->Height;
    }

    DrawSpeedBar (
      BackBuffer,
      Stride,
      Content->Height,
      X,
      (UINT32)RegionSize,
      Baseline,
      SpeedLevel
      );

    UnicodeSPrint (
      StatusLine,
      sizeof (StatusLine),
      L"Advanced Logger  %u/%u  left %u",
      (UINT32)(Page + 1),
      (UINT32)PageCount,
      (UINT32)(PageCount - Page - 1)
      );
    if (DrawStatus != NULL) {
      DrawStatus (This, 0, StatusLine);
    }
  }

  Gop->Blt (
         Gop,
         BackBuffer,
         EfiBltBufferToVideo,
         0,
         0,
         Content->X,
         Content->Y,
         Content->Width,
         Content->Height,
         0
         );

  return EFI_SUCCESS;
}

STATIC
CHAR8 *
CollectLog (
  OUT UINTN  *LogLen
  )
{
  ADVANCED_LOGGER_ACCESS_MESSAGE_LINE_ENTRY  Line;
  EFI_STATUS                                 Status;
  CHAR8                                      *Log;
  CHAR8                                      *New;
  UINTN                                      Len;
  UINTN                                      Cap;
  UINTN                                      NewCap;

  Log = NULL;
  Len = 0;
  Cap = 0;
  ZeroMem (&Line, sizeof (Line));

  for ( ; ;) {
    Status = AdvancedLoggerAccessLibGetNextFormattedLine (&Line);
    if (Status == EFI_END_OF_FILE) {
      break;
    }

    if (EFI_ERROR (Status) || (Line.MessageLen == 0)) {
      break;
    }

    if ((Len + Line.MessageLen + 1) > Cap) {
      NewCap = MAX (Len + Line.MessageLen + 1, Cap * 2);
      NewCap = MAX (NewCap, (UINTN)4096);
      if (Log == NULL) {
        New = AllocatePool (NewCap);
      } else {
        New = ReallocatePool (Cap, NewCap, Log);
      }

      if (New == NULL) {
        break;
      }

      Log = New;
      Cap = NewCap;
    }

    CopyMem (Log + Len, Line.Message, Line.MessageLen);
    Len += Line.MessageLen;
  }

  AdvancedLoggerAccessLibReset (&Line);
  *LogLen = Len;
  return Log;
}

STATIC
EFI_STATUS
EFIAPI
AdvancedLogRun (
  IN UNIXNU_MENU_PLUGIN_PROTOCOL    *This,
  IN EFI_GRAPHICS_OUTPUT_PROTOCOL   *Gop,
  IN CONST UNIXNU_PLUGIN_RECT       *Content,
  IN UNIXNU_MENU_PLUGIN_DRAW_STATUS DrawStatus
  )
{
  EFI_STATUS    Status;
  EFI_EVENT     Timer;
  EFI_EVENT     Events[2];
  UINTN         EventCount;
  UINTN         Signaled;
  EFI_INPUT_KEY  Key;
  CHAR8         *Log;
  UINTN         LogLen;
  UINT8         *Payload;
  UINTN         PayloadLen;
  UINT32        SessionId;
  UINT32        PayloadChecksum;
  UINTN         Page;
  UINTN         PageCount;
  UINTN         Gear;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *BackBuffer;

  if ((Gop == NULL) || (Content == NULL) || (Content->Width == 0) || (Content->Height == 0)) {
    return EFI_INVALID_PARAMETER;
  }

  Log      = CollectLog (&LogLen);
  if (LogLen == 0) {
    Fill (Gop, Content->X, Content->Y, Content->Width, Content->Height, mBackground);
    if (DrawStatus != NULL) {
      DrawStatus (This, 0, L"Advanced Logger: no log");
    }

    gBS->Stall (NO_LOG_STALL_MS * 1000);
    if (Log != NULL) {
      FreePool (Log);
    }

    return EFI_NOT_FOUND;
  }

  Payload = BuildEnvelope ((CONST UINT8 *)Log, LogLen, &PayloadLen);
  FreePool (Log);
  Log = NULL;
  if (Payload == NULL) {
    return EFI_OUT_OF_RESOURCES;
  }

  PageCount      = (PayloadLen + ONESEND_BLOCK_LENGTH - 1) / ONESEND_BLOCK_LENGTH;
  PayloadChecksum = Crc32 (Payload, PayloadLen);
  SessionId       = 0x9E3779B9u ^ (UINT32)(UINTN)Gop ^ (UINT32)PayloadLen;
  if (SessionId == 0) {
    SessionId = 1;
  }

  Page = 0;

  BackBuffer = AllocatePool ((UINTN)Content->Width * Content->Height * sizeof (*BackBuffer));
  if (BackBuffer == NULL) {
    FreePool (Payload);
    return EFI_OUT_OF_RESOURCES;
  }

  Status = gBS->CreateEvent (EVT_TIMER, TPL_CALLBACK, NULL, NULL, &Timer);
  if (EFI_ERROR (Status)) {
    FreePool (BackBuffer);
    FreePool (Payload);
    return Status;
  }

  Gear = SPEED_GEAR_INITIAL;
  gBS->SetTimer (Timer, TimerPeriodic, EFI_TIMER_PERIOD_MILLISECONDS (mGearIntervals[Gear]));
  EventCount = 0;
  Events[EventCount++] = Timer;
  if (gST->ConIn != NULL) {
    Events[EventCount++] = gST->ConIn->WaitForKey;
  }

  DrawPage (Gop, Content, BackBuffer, Payload, PayloadLen, Page, PageCount, SessionId, PayloadChecksum, Gear + 1, This, DrawStatus);
  for ( ; ;) {
    Status = gBS->WaitForEvent (EventCount, Events, &Signaled);
    if (EFI_ERROR (Status)) {
      break;
    }

    if (Signaled == 0) {
      Page = (Page + 1) % PageCount;
      DrawPage (Gop, Content, BackBuffer, Payload, PayloadLen, Page, PageCount, SessionId, PayloadChecksum, Gear + 1, This, DrawStatus);
      continue;
    }

    if (gST->ConIn == NULL) {
      continue;
    }

    if (EFI_ERROR (gST->ConIn->ReadKeyStroke (gST->ConIn, &Key))) {
      continue;
    }

    if ((Key.UnicodeChar == CHAR_CARRIAGE_RETURN) ||
        (Key.UnicodeChar == CHAR_LINEFEED) ||
        (Key.ScanCode == SCAN_ESC))
    {
      break;
    }

    if ((Key.ScanCode == SCAN_UP) || (Key.UnicodeChar == L'k')) {
      if (Gear < SPEED_GEAR_COUNT - 1) {
        Gear++;
        gBS->SetTimer (Timer, TimerPeriodic, EFI_TIMER_PERIOD_MILLISECONDS (mGearIntervals[Gear]));
      }

      DrawPage (Gop, Content, BackBuffer, Payload, PayloadLen, Page, PageCount, SessionId, PayloadChecksum, Gear + 1, This, DrawStatus);
    } else if ((Key.ScanCode == SCAN_DOWN) || (Key.UnicodeChar == L'j')) {
      if (Gear > 0) {
        Gear--;
        gBS->SetTimer (Timer, TimerPeriodic, EFI_TIMER_PERIOD_MILLISECONDS (mGearIntervals[Gear]));
      }

      DrawPage (Gop, Content, BackBuffer, Payload, PayloadLen, Page, PageCount, SessionId, PayloadChecksum, Gear + 1, This, DrawStatus);
    }
  }

  gBS->SetTimer (Timer, TimerCancel, 0);
  gBS->CloseEvent (Timer);
  FreePool (BackBuffer);
  FreePool (Payload);
  return EFI_SUCCESS;
}

STATIC UNIXNU_MENU_PLUGIN_PROTOCOL  mAdvancedLogPlugin = {
  UNIXNU_MENU_PLUGIN_PROTOCOL_SIGNATURE,
  UNIXNU_MENU_PLUGIN_PROTOCOL_VERSION,
  L"Advanced Logger",
  AdvancedLogRun
};

EFI_STATUS
EFIAPI
AdvancedLogDxeEntry (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
  (VOID)SystemTable;
  return gBS->InstallProtocolInterface (
                &ImageHandle,
                &gUniXNUMenuPluginProtocolGuid,
                EFI_NATIVE_INTERFACE,
                &mAdvancedLogPlugin
                );
}
