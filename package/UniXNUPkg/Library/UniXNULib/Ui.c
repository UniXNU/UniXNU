/** @file
  Menu rendering on EFI_GRAPHICS_OUTPUT_PROTOCOL, with a text console
  fallback and a headless mode (log only).

  Graphics mode never prints through ConOut, so firmware consoles that mirror
  ConOut onto the same framebuffer cannot scribble over the menu.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include "Internal.h"

#define PIXEL(r, g, b)  { (b), (g), (r), 0 }

STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mBackground  = PIXEL (0x0B, 0x0C, 0x0F);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mText        = PIXEL (0xF2, 0xF3, 0xF5);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mDim         = PIXEL (0x7C, 0x83, 0x8D);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mAccent      = PIXEL (0x2A, 0x5B, 0xD7);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mRow         = PIXEL (0x17, 0x1A, 0x20);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mError       = PIXEL (0xFF, 0x8A, 0x80);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mRule        = PIXEL (0x26, 0x2A, 0x31);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mMarker      = PIXEL (0xFF, 0xFF, 0xFF);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mBadge       = PIXEL (0x26, 0x2A, 0x31);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mBadgeOn     = PIXEL (0x1B, 0x44, 0xA6);

//
// Rows of the status area (UniXNUUiDrawStatus Line numbers).
//
#define STATUS_LINES  3

STATIC
VOID
FillRect (
  IN UNIXNU_UI                          *Ui,
  IN UINTN                          X,
  IN UINTN                          Y,
  IN UINTN                          W,
  IN UINTN                          H,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Color
  )
{
  if ((X >= Ui->Width) || (Y >= Ui->Height)) {
    return;
  }

  W = MIN (W, Ui->Width - X);
  H = MIN (H, Ui->Height - Y);
  Ui->Gop->Blt (Ui->Gop, &Color, EfiBltVideoFill, 0, 0, X, Y, W, H, 0);
}

//
// Draw Text with its top-left at (X, Y) on a Background box. Returns the
// width in pixels. Characters outside printable ASCII render as '?'.
//
STATIC
UINTN
DrawText (
  IN UNIXNU_UI                          *Ui,
  IN UINTN                          X,
  IN UINTN                          Y,
  IN CONST CHAR16                   *Text,
  IN UINTN                          Scale,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Foreground,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Background,
  IN UINTN                          MaxWidth
  )
{
  UINTN                          Len;
  UINTN                          Cw;
  UINTN                          Ch;
  UINTN                          W;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer;
  UINTN                          Index;
  UINTN                          Row;
  UINTN                          Col;
  UINTN                          Sy;
  UINTN                          Sx;
  CHAR16                         C;
  CONST UINT8                    *Glyph;
  UINTN                          Base;

  Len = StrLen (Text);
  Cw  = UNIXNU_GLYPH_WIDTH * Scale;
  Ch  = UNIXNU_GLYPH_HEIGHT * Scale;
  if ((MaxWidth > 0) && (Len * Cw > MaxWidth)) {
    Len = MaxWidth / Cw;
  }

  if ((Len == 0) || (X >= Ui->Width) || (Y + Ch > Ui->Height)) {
    return 0;
  }

  Len = MIN (Len, (Ui->Width - X) / Cw);
  W   = Len * Cw;
  if (W == 0) {
    return 0;
  }

  Buffer = AllocatePool (W * Ch * sizeof (EFI_GRAPHICS_OUTPUT_BLT_PIXEL));
  if (Buffer == NULL) {
    return 0;
  }

  for (Index = 0; Index < W * Ch; Index++) {
    Buffer[Index] = Background;
  }

  for (Index = 0; Index < Len; Index++) {
    C     = Text[Index];
    Glyph = gCaFontGlyphs[((C >= 0x20) && (C <= 0x7E)) ? (C - 0x20) : ('?' - 0x20)];
    for (Row = 0; Row < UNIXNU_GLYPH_HEIGHT; Row++) {
      for (Col = 0; Col < UNIXNU_GLYPH_WIDTH; Col++) {
        if ((Glyph[Row] & (0x80 >> Col)) == 0) {
          continue;
        }

        Base = (Row * Scale) * W + Index * Cw + Col * Scale;
        for (Sy = 0; Sy < Scale; Sy++) {
          for (Sx = 0; Sx < Scale; Sx++) {
            Buffer[Base + Sy * W + Sx] = Foreground;
          }
        }
      }
    }
  }

  Ui->Gop->Blt (Ui->Gop, Buffer, EfiBltBufferToVideo, 0, 0, X, Y, W, Ch, 0);
  FreePool (Buffer);
  return W;
}

STATIC
VOID
DrawCentered (
  IN UNIXNU_UI                          *Ui,
  IN UINTN                          Y,
  IN CONST CHAR16                   *Text,
  IN UINTN                          Scale,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Foreground
  )
{
  UINTN  W;

  W = MIN (StrLen (Text) * UNIXNU_GLYPH_WIDTH * Scale, Ui->Width);
  DrawText (Ui, (Ui->Width - W) / 2, Y, Text, Scale, Foreground, mBackground, Ui->Width);
}

// ---------------------------------------------------------------------------
// Text console
// ---------------------------------------------------------------------------

STATIC
VOID
TextPrintAt (
  IN UNIXNU_UI         *Ui,
  IN UINTN         Row,
  IN UINTN         Attribute,
  IN CONST CHAR16  *Text
  )
{
  EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL  *Out;
  CHAR16                           Line[160];
  UINTN                            Width;
  UINTN                            Len;

  Out = gST->ConOut;
  if ((Out == NULL) || (Row >= Ui->TextRows)) {
    return;
  }

  //
  // Pad to the full width (minus the last column, which would scroll).
  //
  Width = MIN (Ui->TextColumns - 1, ARRAY_SIZE (Line) - 1);
  Len   = MIN (StrLen (Text), Width);
  CopyMem (Line, Text, Len * sizeof (CHAR16));
  while (Len < Width) {
    Line[Len++] = L' ';
  }

  Line[Len] = L'\0';
  Out->SetAttribute (Out, Attribute);
  Out->SetCursorPosition (Out, 0, Row);
  Out->OutputString (Out, Line);
  Out->SetAttribute (Out, EFI_LIGHTGRAY | EFI_BACKGROUND_BLACK);
}

STATIC
CONST CHAR16 *
TypeTag (
  IN UNIXNU_ENTRY  *Entry
  )
{
  switch (Entry->Type) {
    case UniXNUEntryLinux:
      return L"linux";
    case UniXNUEntryXnu:
      return L"xnu";
    case UniXNUEntryAction:
      return L"action";
    default:
      return L"efi";
  }
}


// ---------------------------------------------------------------------------
// Portrait layout
//
// A tall panel gets a column instead of the landscape arrangement. The logo,
// title and provenance float in the free space at the top. The entries are
// cards at the bottom, where a thumb reaches them, each with a number badge,
// the title and the entry type under it. The status lines sit under a rule at
// the very bottom and wrap onto a second row instead of running off the side.
// The logo carries the UniXNU wordmark, so the pixel-font title is drawn only
// when there is no logo or the configuration gives a different title.
// ---------------------------------------------------------------------------

#define PORTRAIT_TEXT_MAX    127
#define PORTRAIT_STATUS_ROWS 2     // Text rows per status line.

//
// Copy Text into Out (PORTRAIT_TEXT_MAX + 1 characters) cut to MaxChars with
// a trailing "..." when it is longer.
//
STATIC
VOID
FitText (
  IN  CONST CHAR16  *Text,
  IN  UINTN         MaxChars,
  OUT CHAR16        *Out
  )
{
  UINTN  Len;

  MaxChars = MIN (MaxChars, (UINTN)PORTRAIT_TEXT_MAX);
  Len      = MIN (StrLen (Text), (UINTN)PORTRAIT_TEXT_MAX);
  if (Len > MaxChars) {
    if (MaxChars > 3) {
      CopyMem (Out, Text, (MaxChars - 3) * sizeof (CHAR16));
      Out[MaxChars - 3] = L'.';
      Out[MaxChars - 2] = L'.';
      Out[MaxChars - 1] = L'.';
      Len               = MaxChars;
    } else {
      CopyMem (Out, Text, MaxChars * sizeof (CHAR16));
      Len = MaxChars;
    }
  } else {
    CopyMem (Out, Text, Len * sizeof (CHAR16));
  }

  Out[Len] = L'\0';
}

//
// Split Text over two rows of MaxChars at the last space that fits; the second
// row is cut with "..." if it still does not fit.
//
STATIC
VOID
WrapText (
  IN  CONST CHAR16  *Text,
  IN  UINTN         MaxChars,
  OUT CHAR16        *First,
  OUT CHAR16        *Second
  )
{
  UINTN  Len;
  UINTN  Cut;

  MaxChars = MIN (MAX (MaxChars, (UINTN)1), (UINTN)PORTRAIT_TEXT_MAX);
  Len      = StrLen (Text);
  if (Len <= MaxChars) {
    FitText (Text, MaxChars, First);
    Second[0] = L'\0';
    return;
  }

  Cut = MaxChars;
  while ((Cut > 0) && (Text[Cut] != L' ')) {
    Cut--;
  }

  if (Cut == 0) {
    Cut = MaxChars;
  }

  CopyMem (First, Text, Cut * sizeof (CHAR16));
  First[Cut] = L'\0';
  while (Text[Cut] == L' ') {
    Cut++;
  }

  FitText (Text + Cut, MaxChars, Second);
}

//
// Draw Text cut to Width pixels, horizontally centered in [Left, Left + Width).
//
STATIC
VOID
DrawCenteredIn (
  IN UNIXNU_UI                          *Ui,
  IN UINTN                          Left,
  IN UINTN                          Width,
  IN UINTN                          Y,
  IN CONST CHAR16                   *Text,
  IN UINTN                          Scale,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Foreground
  )
{
  CHAR16  Fit[PORTRAIT_TEXT_MAX + 1];
  UINTN   Cw;
  UINTN   W;

  Cw = UNIXNU_GLYPH_WIDTH * Scale;
  FitText (Text, Width / Cw, Fit);
  W = StrLen (Fit) * Cw;
  DrawText (Ui, Left + (Width - W) / 2, Y, Fit, Scale, Foreground, mBackground, 0);
}

STATIC
UINTN
FooterScale (
  IN UNIXNU_UI  *Ui
  )
{
  return (Ui->Scale > 1) ? Ui->Scale - 1 : 1;
}

STATIC
UINTN
FooterPitch (
  IN UNIXNU_UI  *Ui
  )
{
  UINTN  Ch;

  Ch = UNIXNU_GLYPH_HEIGHT * FooterScale (Ui);
  return Ch + Ch / 3;
}

//
// Draw (or only measure) the header block with its top at Top. Returns its
// height: logo, title, accent rule, version and the configuration source.
//
STATIC
UINTN
PortraitHeader (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN BOOLEAN        Draw,
  IN UINTN          Top,
  IN UINTN          Logo
  )
{
  UINTN                          Ch;
  UINTN                          Fch;
  UINTN                          Inner;
  UINTN                          TitleScale;
  UINTN                          Y;
  UINTN                          Rule;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer;
  CHAR16                         Line[128];

  Ch    = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  Fch   = UNIXNU_GLYPH_HEIGHT * FooterScale (Ui);
  Inner = Ui->Width - 2 * Ui->Margin;
  Y     = Top;

  if (Logo > 0) {
    if (Draw) {
      Buffer = AllocatePool (Logo * Logo * sizeof (EFI_GRAPHICS_OUTPUT_BLT_PIXEL));
      if (Buffer != NULL) {
        UniXNULogoRender (Buffer, Logo, mBackground);
        Ui->Gop->Blt (Ui->Gop, Buffer, EfiBltBufferToVideo, 0, 0, (Ui->Width - Logo) / 2, Y, Logo, Logo, 0);
        FreePool (Buffer);
      }
    }

    Y += Logo + Ch;
  }

  //
  // One and a half times the text size when the title fits the column, the
  // text size otherwise.
  //
  if ((Logo == 0) || (StrCmp (Config->Title, L"UniXNU") != 0)) {
    TitleScale = (StrLen (Config->Title) * UNIXNU_GLYPH_WIDTH * Ui->Scale * 3 / 2 <= Inner) ? Ui->Scale * 3 / 2 : Ui->Scale;
    if (Draw) {
      DrawCenteredIn (Ui, Ui->Margin, Inner, Y, Config->Title, TitleScale, mText);
    }

    Y += UNIXNU_GLYPH_HEIGHT * TitleScale + Ch / 2;
  }

  Rule = MAX ((UINTN)2, Ui->Scale);
  if (Draw) {
    FillRect (Ui, (Ui->Width - Inner / 5) / 2, Y, Inner / 5, Rule, mAccent);
  }

  Y += Rule + Ch / 2;
  if (Draw) {
    UnicodeSPrint (Line, sizeof (Line), L"version %a", UNIXNU_VERSION_STRING);
    DrawCenteredIn (Ui, Ui->Margin, Inner, Y, Line, FooterScale (Ui), mDim);
  }

  Y += Fch + Fch / 3;
  if (Draw) {
    DrawCenteredIn (Ui, Ui->Margin, Inner, Y, Config->SourceLabel, FooterScale (Ui), mDim);
  }

  Y += Fch;
  return Y - Top;
}

STATIC
VOID
DrawPortraitStatusRow (
  IN UNIXNU_UI                          *Ui,
  IN UINTN                          Row,
  IN CONST CHAR16                   *Text,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Color
  )
{
  CHAR16  First[PORTRAIT_TEXT_MAX + 1];
  CHAR16  Second[PORTRAIT_TEXT_MAX + 1];
  UINTN   Fs;
  UINTN   Pitch;
  UINTN   Y;
  UINTN   Inner;

  Fs    = FooterScale (Ui);
  Pitch = FooterPitch (Ui);
  Inner = Ui->Width - 2 * Ui->Margin;
  Y     = Ui->FooterTop + Row * Pitch;
  FillRect (Ui, 0, Y, Ui->Width, PORTRAIT_STATUS_ROWS * Pitch, mBackground);
  WrapText (Text, Inner / (UNIXNU_GLYPH_WIDTH * Fs), First, Second);
  DrawCenteredIn (Ui, Ui->Margin, Inner, Y, First, Fs, Color);
  if (Second[0] != L'\0') {
    DrawCenteredIn (Ui, Ui->Margin, Inner, Y + Pitch, Second, Fs, Color);
  }
}

STATIC
VOID
DrawFramePortrait (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  )
{
  UINTN   Ch;
  UINTN   Fch;
  UINTN   Pad;
  UINTN   Pitch;
  UINTN   Top;
  UINTN   FooterRows;
  UINTN   ListBottom;
  UINTN   MaxRows;
  UINTN   Logo;
  UINTN   HeaderH;
  UINTN   Other;
  UINTN   Free;
  UINTN   Extra;
  UINTN   Inner;
  BOOLEAN HasNote;
  CHAR16  Line[160];

  Ch    = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  Fch   = UNIXNU_GLYPH_HEIGHT * FooterScale (Ui);
  Inner = Ui->Width - 2 * Ui->Margin;
  FillRect (Ui, 0, 0, Ui->Width, Ui->Height, mBackground);

  //
  // Footer: the countdown and key help lines, the result of the last boot
  // attempt when there is one, then the configuration problem and the
  // injection summary; each is two rows tall.
  //
  HasNote       = (Config->Error[0] != '\0') || (Config->Notice[0] != '\0');
  Ui->StatusLines = (Ui->Notice[0] != L'\0') ? STATUS_LINES : 2;
  FooterRows    = (Ui->StatusLines + (HasNote ? 1 : 0) + ((Ui->Info[0] != L'\0') ? 1 : 0)) * PORTRAIT_STATUS_ROWS;
  Ui->FooterTop = Ui->Height - Ui->Height / 32 - FooterRows * FooterPitch (Ui);
  FillRect (Ui, Ui->Margin, Ui->FooterTop - Fch, Inner, MAX ((UINTN)1, Ui->Scale / 2), mRule);

  //
  // Cards: two text lines inside a padded box, a gap between cards.
  //
  Pad            = Ch / 2;
  Ui->CardHeight = Ch + Fch + 2 * Pad;
  Pitch          = Ui->CardHeight + Ui->Scale * 3;
  Ui->RowHeight  = Pitch;
  ListBottom     = Ui->FooterTop - Fch * 2;
  Top            = Ui->Height / 20;

  //
  // Cards first, from the bottom up; the header (without the logo) gets what
  // is above them. The logo takes the space the header leaves free, as large
  // as the column allows, and is dropped when less than 128 pixels remain.
  //
  HeaderH = PortraitHeader (Ui, Config, FALSE, 0, 0);
  MaxRows = (ListBottom > Top + HeaderH + Ch) ? (ListBottom - Top - HeaderH - Ch) / Pitch : 0;
  Ui->VisibleRows = MIN (Config->EntryCount, MAX (MaxRows, (UINTN)1));
  Ui->MenuTop     = ListBottom - Ui->VisibleRows * Pitch + Ui->Scale * 3;

  //
  // Header height without the logo, whether or not the title shows beside it.
  //
  Other = PortraitHeader (Ui, Config, FALSE, 0, 1) - 1 - Ch;
  Logo  = 0;
  Free  = (Ui->MenuTop > Top + Ch) ? Ui->MenuTop - Ch - Top : 0;
  if (Config->ShowLogo && (Free > Other + Ch * 2)) {
    Logo = MIN (MIN (Inner * 8 / 10, (UINTN)Ui->Height / 4), Free - Other - Ch * 2);
    if (Logo < 128) {
      Logo = 0;
    }
  }

  //
  // The header floats in the space the cards leave free.
  //
  HeaderH = PortraitHeader (Ui, Config, FALSE, 0, Logo);
  Extra   = (Free > HeaderH) ? (Free - HeaderH) / 2 : 0;
  PortraitHeader (Ui, Config, TRUE, Top + Extra, Logo);

  Line[0] = L'\0';
  Extra   = Ui->StatusLines * PORTRAIT_STATUS_ROWS;
  if (Config->Error[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"config error: %a", Config->Error);
  } else if (Config->Notice[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"%a", Config->Notice);
  }

  if (Line[0] != L'\0') {
    DrawPortraitStatusRow (Ui, Extra, Line, mError);
    Extra += PORTRAIT_STATUS_ROWS;
  }

  if (Ui->Info[0] != L'\0') {
    DrawPortraitStatusRow (Ui, Extra, Ui->Info, mDim);
  }
}

STATIC
VOID
DrawEntryPortrait (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN UINTN          Index,
  IN BOOLEAN        Selected
  )
{
  UNIXNU_ENTRY                   *Entry;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Bg;
  UINTN                          Ch;
  UINTN                          Fs;
  UINTN                          Fch;
  UINTN                          Pad;
  UINTN                          Badge;
  UINTN                          X;
  UINTN                          Y;
  UINTN                          Width;
  UINTN                          TextX;
  UINTN                          TextW;
  UINTN                          DigitW;
  CHAR16                         Fit[PORTRAIT_TEXT_MAX + 1];
  CHAR16                         Number[8];

  Entry = &Config->Entries[Index];
  Ch    = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  Fs    = FooterScale (Ui);
  Fch   = UNIXNU_GLYPH_HEIGHT * Fs;
  Pad   = Ch / 2;
  X     = Ui->Margin;
  Y     = Ui->MenuTop + Index * Ui->RowHeight;
  Width = Ui->Width - 2 * Ui->Margin;
  Bg    = Selected ? mAccent : mRow;

  FillRect (Ui, X, Y, Width, Ui->CardHeight, Bg);
  if (Selected) {
    FillRect (Ui, X, Y, Ui->Scale * 2, Ui->CardHeight, mMarker);
  }

  //
  // Number badge, centered vertically in the card.
  //
  Badge = Ch * 3 / 2;
  FillRect (Ui, X + Pad, Y + (Ui->CardHeight - Badge) / 2, Badge, Badge, Selected ? mBadgeOn : mBadge);
  UnicodeSPrint (Number, sizeof (Number), L"%u", (UINT32)Index + 1);
  DigitW = StrLen (Number) * UNIXNU_GLYPH_WIDTH * Ui->Scale;
  DrawText (
    Ui,
    X + Pad + (Badge - MIN (DigitW, Badge)) / 2,
    Y + (Ui->CardHeight - Ch) / 2,
    Number,
    Ui->Scale,
    mText,
    Selected ? mBadgeOn : mBadge,
    Badge
    );

  TextX = X + Pad + Badge + Pad;
  TextW = (X + Width > TextX + Pad) ? X + Width - Pad - TextX : 0;
  FitText (Entry->Title, TextW / (UNIXNU_GLYPH_WIDTH * Ui->Scale), Fit);
  DrawText (Ui, TextX, Y + Pad, Fit, Ui->Scale, mText, Bg, 0);
  DrawText (Ui, TextX, Y + Ui->CardHeight - Pad - Fch, TypeTag (Entry), Fs, Selected ? mText : mDim, Bg, 0);
}

STATIC
VOID
DrawStatusPortrait (
  IN UNIXNU_UI         *Ui,
  IN UINTN         Line,
  IN CONST CHAR16  *Text
  )
{
  DrawPortraitStatusRow (Ui, Line * PORTRAIT_STATUS_ROWS, Text, (Line == 0) ? mText : mDim);
}

BOOLEAN
UniXNUUiChoosePortrait (
  IN UNIXNU_LAYOUT  Layout,
  IN UINTN          PortraitBelow,
  IN UINT32         Width,
  IN UINT32         Height
  )
{
  if (Layout == UniXNULayoutLandscape) {
    return FALSE;
  }

  if (Layout == UniXNULayoutPortrait) {
    return TRUE;
  }

  return (Height != 0) && ((UINT64)Width * 1000 < (UINT64)PortraitBelow * Height);
}

// ---------------------------------------------------------------------------
// Public
// ---------------------------------------------------------------------------

VOID
UniXNUUiInit (
  IN  UNIXNU_CONFIG  *Config,
  OUT UNIXNU_UI      *Ui
  )
{
  EFI_STATUS  Status;

  ZeroMem (Ui, sizeof (*Ui));
  Ui->Mode = UniXNUUiHeadless;

  if ((Config->Console == UniXNUConsoleAuto) || (Config->Console == UniXNUConsoleGraphics)) {
    Status = EFI_NOT_FOUND;
    if (gST->ConsoleOutHandle != NULL) {
      Status = gBS->HandleProtocol (gST->ConsoleOutHandle, &gEfiGraphicsOutputProtocolGuid, (VOID **)&Ui->Gop);
    }

    if (EFI_ERROR (Status)) {
      Status = gBS->LocateProtocol (&gEfiGraphicsOutputProtocolGuid, NULL, (VOID **)&Ui->Gop);
    }

    if (!EFI_ERROR (Status) && (Ui->Gop->Mode != NULL) && (Ui->Gop->Mode->Info != NULL)) {
      Ui->Mode   = UniXNUUiGraphics;
      Ui->Width  = Ui->Gop->Mode->Info->HorizontalResolution;
      Ui->Height = Ui->Gop->Mode->Info->VerticalResolution;
      Ui->Portrait = UniXNUUiChoosePortrait (Config->Layout, Config->PortraitBelow, Ui->Width, Ui->Height);
      if (Ui->Portrait) {
        //
        // The column is as wide as the short side: about 33 characters of
        // the normal size across a 1080 pixel panel.
        //
        Ui->Margin = Ui->Width / 12;
        Ui->Scale  = (Config->Scale > 0) ? Config->Scale : MAX (1, Ui->Width / 270);
      } else {
        Ui->Scale = (Config->Scale > 0) ? Config->Scale : MAX (1, Ui->Height / 540);
      }
    }
  }

  if ((Ui->Mode == UniXNUUiHeadless) && (Config->Console != UniXNUConsoleNone) && (gST->ConOut != NULL)) {
    if (!EFI_ERROR (gST->ConOut->QueryMode (gST->ConOut, gST->ConOut->Mode->Mode, &Ui->TextColumns, &Ui->TextRows))) {
      Ui->Mode = UniXNUUiText;
    }
  }

  if (Ui->Mode == UniXNUUiGraphics) {
    UniXNULog ("ui: graphics %ux%u, scale %u, %a layout", Ui->Width, Ui->Height, (UINT32)Ui->Scale, Ui->Portrait ? "portrait" : "landscape");
  } else if (Ui->Mode == UniXNUUiText) {
    UniXNULog ("ui: text console %ux%u", (UINT32)Ui->TextColumns, (UINT32)Ui->TextRows);
  } else {
    UniXNULog ("ui: headless (no GOP, no text console)");
  }
}

VOID
UniXNUUiDrawFrame (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  )
{
  UINTN                          Logo;
  UINTN                          Y;
  UINTN                          Cw;
  UINTN                          Ch;
  UINTN                          Index;
  UINTN                          Longest;
  UINTN                          MaxRows;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer;
  CHAR16                         Line[128];

  if (Ui->Mode == UniXNUUiText) {
    gST->ConOut->EnableCursor (gST->ConOut, FALSE);
    gST->ConOut->ClearScreen (gST->ConOut);
    UnicodeSPrint (Line, sizeof (Line), L"%s  (UniXNU %a)", Config->Title, UNIXNU_VERSION_STRING);
    TextPrintAt (Ui, 0, EFI_WHITE | EFI_BACKGROUND_BLACK, Line);
    TextPrintAt (Ui, 1, EFI_DARKGRAY | EFI_BACKGROUND_BLACK, Config->SourceLabel);
    Ui->MenuTop     = 3;
    Ui->VisibleRows = MIN (Config->EntryCount, Ui->TextRows > 8 ? Ui->TextRows - 8 : 1);
    Ui->FooterTop   = Ui->TextRows - STATUS_LINES - 2;
    if (Config->Error[0] != '\0') {
      UnicodeSPrint (Line, sizeof (Line), L"config error: %a", Config->Error);
      TextPrintAt (Ui, Ui->FooterTop + STATUS_LINES, EFI_LIGHTRED | EFI_BACKGROUND_BLACK, Line);
    } else if (Config->Notice[0] != '\0') {
      UnicodeSPrint (Line, sizeof (Line), L"%a", Config->Notice);
      TextPrintAt (Ui, Ui->FooterTop + STATUS_LINES, EFI_YELLOW | EFI_BACKGROUND_BLACK, Line);
    }

    if (Ui->Info[0] != L'\0') {
      TextPrintAt (Ui, Ui->FooterTop + STATUS_LINES + 1, EFI_DARKGRAY | EFI_BACKGROUND_BLACK, Ui->Info);
    }

    return;
  }

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  if (Ui->Portrait) {
    DrawFramePortrait (Ui, Config);
    return;
  }

  Cw = UNIXNU_GLYPH_WIDTH * Ui->Scale;
  Ch = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  FillRect (Ui, 0, 0, Ui->Width, Ui->Height, mBackground);

  //
  // Logo (it carries the UniXNU wordmark), title and provenance.
  //
  Y = Ui->Height / 18;
  if (Config->ShowLogo) {
    Logo   = MAX (96, MIN (Ui->Width, Ui->Height) * 3 / 10);
    Buffer = AllocatePool (Logo * Logo * sizeof (EFI_GRAPHICS_OUTPUT_BLT_PIXEL));
    if (Buffer != NULL) {
      UniXNULogoRender (Buffer, Logo, mBackground);
      Ui->Gop->Blt (Ui->Gop, Buffer, EfiBltBufferToVideo, 0, 0, (Ui->Width - Logo) / 2, Y, Logo, Logo, 0);
      FreePool (Buffer);
    }

    Y += Logo + Ch / 2;
  }

  //
  // The logo's wordmark already reads UniXNU: as in the portrait header, the
  // title is drawn only without the logo or when it says something else.
  //
  if (!Config->ShowLogo || (StrCmp (Config->Title, L"UniXNU") != 0)) {
    DrawCentered (Ui, Y, Config->Title, Ui->Scale * 2, mText);
    Y += Ch * 2 + Ch / 2;
  }

  UnicodeSPrint (Line, sizeof (Line), L"version %a  |  %s", UNIXNU_VERSION_STRING, Config->SourceLabel);
  DrawCentered (Ui, Y, Line, Ui->Scale, mDim);
  Y += Ch + Ch / 2;

  //
  // Menu box: wide enough for the longest title plus the type tag.
  //
  Longest = 24;
  for (Index = 0; Index < Config->EntryCount; Index++) {
    Longest = MAX (Longest, StrLen (Config->Entries[Index].Title) + 12);
  }

  Ui->RowHeight = Ch + Ch / 2;
  Ui->MenuWidth = MIN (Longest * Cw, Ui->Width - 2 * Cw);
  Ui->MenuLeft  = (Ui->Width - Ui->MenuWidth) / 2;
  FillRect (Ui, Ui->MenuLeft, Y, Ui->MenuWidth, MAX (1, Ui->Scale / 2), mRule);
  Y            += Ch;
  Ui->MenuTop   = Y;
  Ui->FooterTop = Ui->Height - (STATUS_LINES + 2) * (Ch + Ch / 3);
  MaxRows       = (Ui->FooterTop > Y + Ui->RowHeight) ? (Ui->FooterTop - Y) / Ui->RowHeight : 1;
  Ui->VisibleRows = MIN (Config->EntryCount, MaxRows);

  if (Config->Error[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"config error: %a", Config->Error);
    DrawCentered (Ui, Ui->FooterTop + STATUS_LINES * (Ch + Ch / 3), Line, Ui->Scale, mError);
  } else if (Config->Notice[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"%a", Config->Notice);
    DrawCentered (Ui, Ui->FooterTop + STATUS_LINES * (Ch + Ch / 3), Line, Ui->Scale, mError);
  }

  if (Ui->Info[0] != L'\0') {
    DrawCentered (Ui, Ui->FooterTop + (STATUS_LINES + 1) * (Ch + Ch / 3), Ui->Info, Ui->Scale, mDim);
  }
}

VOID
UniXNUUiDrawEntry (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN UINTN      Index,
  IN BOOLEAN    Selected
  )
{
  UNIXNU_ENTRY                       *Entry;
  UINTN                          Y;
  UINTN                          Pad;
  UINTN                          Cw;
  UINTN                          Ch;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Bg;
  CONST CHAR16                   *Tag;
  CHAR16                         Line[160];

  if (Index >= Ui->VisibleRows) {
    return;
  }

  Entry = &Config->Entries[Index];
  if (Ui->Mode == UniXNUUiText) {
    UnicodeSPrint (Line, sizeof (Line), L" %c %u. %s  [%s]", Selected ? L'>' : L' ', (UINT32)Index + 1, Entry->Title, TypeTag (Entry));
    TextPrintAt (
      Ui,
      Ui->MenuTop + Index,
      Selected ? (EFI_WHITE | EFI_BACKGROUND_RED) : (EFI_LIGHTGRAY | EFI_BACKGROUND_BLACK),
      Line
      );
    return;
  }

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  if (Ui->Portrait) {
    DrawEntryPortrait (Ui, Config, Index, Selected);
    return;
  }

  Cw  = UNIXNU_GLYPH_WIDTH * Ui->Scale;
  Ch  = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  Y   = Ui->MenuTop + Index * Ui->RowHeight;
  Pad = (Ui->RowHeight - Ch) / 2;
  Bg  = Selected ? mAccent : mRow;
  Tag = TypeTag (Entry);

  //
  // Leave a one-scale-unit gap between rows.
  //
  FillRect (Ui, Ui->MenuLeft, Y, Ui->MenuWidth, Ui->RowHeight - Ui->Scale, Bg);
  if (Selected) {
    FillRect (Ui, Ui->MenuLeft, Y, Ui->Scale * 3, Ui->RowHeight - Ui->Scale, mMarker);
  }
  UnicodeSPrint (Line, sizeof (Line), L"%u  %s", (UINT32)Index + 1, Entry->Title);
  DrawText (Ui, Ui->MenuLeft + Cw, Y + Pad, Line, Ui->Scale, mText, Bg, Ui->MenuWidth - (StrLen (Tag) + 3) * Cw);
  DrawText (
    Ui,
    Ui->MenuLeft + Ui->MenuWidth - (StrLen (Tag) + 1) * Cw,
    Y + Pad,
    Tag,
    Ui->Scale,
    Selected ? mText : mDim,
    Bg,
    0
    );
}

VOID
UniXNUUiDrawStatus (
  IN UNIXNU_UI         *Ui,
  IN UINTN         Line,
  IN CONST CHAR16  *Text
  )
{
  UINTN  Ch;
  UINTN  Y;

  if (Line >= STATUS_LINES) {
    return;
  }

  if (Ui->Mode == UniXNUUiText) {
    TextPrintAt (Ui, Ui->FooterTop + Line, EFI_LIGHTGRAY | EFI_BACKGROUND_BLACK, Text);
    return;
  }

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  if (Ui->Portrait) {
    DrawStatusPortrait (Ui, Line, Text);
    return;
  }

  Ch = UNIXNU_GLYPH_HEIGHT * Ui->Scale;
  Y  = Ui->FooterTop + Line * (Ch + Ch / 3);
  FillRect (Ui, 0, Y, Ui->Width, Ch, mBackground);
  DrawCentered (Ui, Y, Text, Ui->Scale, (Line == 0) ? mText : mDim);
}
