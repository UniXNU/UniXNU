/** @file
  OpenCode-inspired TUI boot menu on EFI_GRAPHICS_OUTPUT_PROTOCOL, with a
  text console fallback and a headless mode (log only).

  Graphics mode never prints through ConOut, so firmware consoles that mirror
  ConOut onto the same framebuffer cannot scribble over the menu.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include "Internal.h"

#define PIXEL(r, g, b)  { (b), (g), (r), 0 }

STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mBackground      = PIXEL (0x0A, 0x0A, 0x0A);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mSurface         = PIXEL (0x14, 0x14, 0x14);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mSurfaceSelected = PIXEL (0x1E, 0x1B, 0x29);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mAccent          = PIXEL (0xA7, 0x8B, 0xFA);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mAmber           = PIXEL (0xE0, 0xA0, 0x60);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mText            = PIXEL (0xEC, 0xEE, 0xF2);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mTextSoft        = PIXEL (0x9C, 0xA3, 0xAF);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mDim             = PIXEL (0x5C, 0x63, 0x70);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mError           = PIXEL (0xF8, 0x71, 0x71);
STATIC CONST EFI_GRAPHICS_OUTPUT_BLT_PIXEL  mLogoWhite       = PIXEL (0xFF, 0xFF, 0xFF);

//
// Rows of the status area (UniXNUUiDrawStatus Line numbers).
//
#define STATUS_LINES   3
#define WORDMARK_ROWS  5
#define WORDMARK_COLS  25

//
// Compact all-white pixel wordmark ("uniXNU"): 5-row uni + slim XNU.
//
STATIC CONST CHAR8  *mWordmark[WORDMARK_ROWS] = {
  "W..W.WWWW.W..W.W.W..W.W.W",
  "W..W.W..W....W.W.WW.W.W.W",
  "W..W.W..W.W...W..W.WW.W.W",
  "W..W.W..W.W..W.W.W..W.W.W",
  "WWWW.W..W.W..W.W.W..W.WWW"
};

STATIC
VOID
FillRect (
  IN UNIXNU_UI                      *Ui,
  IN UINTN                          X,
  IN UINTN                          Y,
  IN UINTN                          W,
  IN UINTN                          H,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Color
  )
{
  if ((X >= Ui->Width) || (Y >= Ui->Height) || (W == 0) || (H == 0)) {
    return;
  }

  W = MIN (W, Ui->Width - X);
  H = MIN (H, Ui->Height - Y);
  Ui->Gop->Blt (Ui->Gop, &Color, EfiBltVideoFill, 0, 0, X, Y, W, H, 0);
}

STATIC
UINTN
GlyphIndex (
  IN CHAR16  C
  )
{
  return ((C >= 0x20) && (C <= 0x7E)) ? (UINTN)(C - 0x20) : (UINTN)('?' - 0x20);
}

STATIC
UINTN
MeasureTextN (
  IN CONST CHAR16  *Text,
  IN UINTN         Count,
  IN UINTN         Scale
  )
{
  UINTN  Index;
  UINTN  GridW;

  GridW = 0;
  for (Index = 0; Index < Count; Index++) {
    GridW += gOcFontWidths[GlyphIndex (Text[Index])];
  }

  return GridW * Scale;
}

STATIC
UINTN
MeasureText (
  IN CONST CHAR16  *Text,
  IN UINTN         Scale
  )
{
  return MeasureTextN (Text, StrLen (Text), Scale);
}

STATIC
UINTN
MeasureMenuTextN (
  IN CONST CHAR16  *Text,
  IN UINTN         Count,
  IN UINTN         Scale
  )
{
  UINTN  Index;
  UINTN  GridW;

  GridW = 0;
  for (Index = 0; Index < Count; Index++) {
    GridW += gOcMenuFontWidths[GlyphIndex (Text[Index])];
  }

  return GridW * Scale;
}

STATIC
UINTN
MeasureMenuText (
  IN CONST CHAR16  *Text,
  IN UINTN         Scale
  )
{
  return MeasureMenuTextN (Text, StrLen (Text), Scale);
}

//
// Draw proportional Silkscreen pixel Text with its top-left at (X, Y) on a
// Background box. Returns the width in pixels. Non-ASCII renders as '?'.
//
STATIC
UINTN
DrawText (
  IN UNIXNU_UI                      *Ui,
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
  UINTN                          DrawLen;
  UINTN                          Ch;
  UINTN                          Limit;
  UINTN                          W;
  UINTN                          CurX;
  UINTN                          GIdx;
  UINTN                          Adv;
  UINTN                          AdvPx;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer;
  UINTN                          Index;
  UINTN                          Row;
  UINTN                          Col;
  UINTN                          Sy;
  UINTN                          Sx;
  CONST UINT8                    *Glyph;
  UINTN                          Base;

  Len = StrLen (Text);
  Ch  = UNIXNU_OC_GLYPH_HEIGHT * Scale;
  if ((Len == 0) || (Scale == 0) || (X >= Ui->Width) || (Y + Ch > Ui->Height)) {
    return 0;
  }

  Limit = Ui->Width - X;
  if ((MaxWidth > 0) && (MaxWidth < Limit)) {
    Limit = MaxWidth;
  }

  W       = 0;
  DrawLen = 0;
  for (Index = 0; Index < Len; Index++) {
    AdvPx = gOcFontWidths[GlyphIndex (Text[Index])] * Scale;
    if (W + AdvPx > Limit) {
      break;
    }

    W += AdvPx;
    DrawLen++;
  }

  if ((DrawLen == 0) || (W == 0)) {
    return 0;
  }

  Buffer = AllocatePool (W * Ch * sizeof (EFI_GRAPHICS_OUTPUT_BLT_PIXEL));
  if (Buffer == NULL) {
    return 0;
  }

  for (Index = 0; Index < W * Ch; Index++) {
    Buffer[Index] = Background;
  }

  CurX = 0;
  for (Index = 0; Index < DrawLen; Index++) {
    GIdx  = GlyphIndex (Text[Index]);
    Glyph = gOcFontGlyphs[GIdx];
    Adv   = gOcFontWidths[GIdx];
    for (Row = 0; Row < UNIXNU_OC_GLYPH_HEIGHT; Row++) {
      for (Col = 0; Col < Adv; Col++) {
        if ((Glyph[Row] & (0x80 >> Col)) == 0) {
          continue;
        }

        Base = (Row * Scale) * W + CurX + Col * Scale;
        for (Sy = 0; Sy < Scale; Sy++) {
          for (Sx = 0; Sx < Scale; Sx++) {
            Buffer[Base + Sy * W + Sx] = Foreground;
          }
        }
      }
    }

    CurX += Adv * Scale;
  }

  Ui->Gop->Blt (Ui->Gop, Buffer, EfiBltBufferToVideo, 0, 0, X, Y, W, Ch, 0);
  FreePool (Buffer);
  return W;
}

//
// Draw proportional Fusion Pixel 10px Text (10px grid, case-sensitive, slashed
// '0') for menu entry titles, sharing the same pixel block size as Silkscreen.
//
STATIC
UINTN
DrawMenuText (
  IN UNIXNU_UI                      *Ui,
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
  UINTN                          DrawLen;
  UINTN                          Ch;
  UINTN                          Limit;
  UINTN                          W;
  UINTN                          CurX;
  UINTN                          GIdx;
  UINTN                          Adv;
  UINTN                          MaxCol;
  UINTN                          AdvPx;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  *Buffer;
  UINTN                          Index;
  UINTN                          Row;
  UINTN                          Col;
  UINTN                          Sy;
  UINTN                          Sx;
  CONST UINT8                    *Glyph;
  UINTN                          Base;

  Len = StrLen (Text);
  Ch  = UNIXNU_OC_MENU_GLYPH_HEIGHT * Scale;
  if ((Len == 0) || (Scale == 0) || (X >= Ui->Width) || (Y + Ch > Ui->Height)) {
    return 0;
  }

  Limit = Ui->Width - X;
  if ((MaxWidth > 0) && (MaxWidth < Limit)) {
    Limit = MaxWidth;
  }

  W       = 0;
  DrawLen = 0;
  for (Index = 0; Index < Len; Index++) {
    AdvPx = gOcMenuFontWidths[GlyphIndex (Text[Index])] * Scale;
    if (W + AdvPx > Limit) {
      break;
    }

    W += AdvPx;
    DrawLen++;
  }

  if ((DrawLen == 0) || (W == 0)) {
    return 0;
  }

  Buffer = AllocatePool (W * Ch * sizeof (EFI_GRAPHICS_OUTPUT_BLT_PIXEL));
  if (Buffer == NULL) {
    return 0;
  }

  for (Index = 0; Index < W * Ch; Index++) {
    Buffer[Index] = Background;
  }

  CurX = 0;
  for (Index = 0; Index < DrawLen; Index++) {
    GIdx   = GlyphIndex (Text[Index]);
    Glyph  = gOcMenuFontGlyphs[GIdx];
    Adv    = gOcMenuFontWidths[GIdx];
    MaxCol = MIN (Adv, (UINTN)8);
    for (Row = 0; Row < UNIXNU_OC_MENU_GLYPH_HEIGHT; Row++) {
      for (Col = 0; Col < MaxCol; Col++) {
        if ((Glyph[Row] & (0x80 >> Col)) == 0) {
          continue;
        }

        Base = (Row * Scale) * W + CurX + Col * Scale;
        for (Sy = 0; Sy < Scale; Sy++) {
          for (Sx = 0; Sx < Scale; Sx++) {
            Buffer[Base + Sy * W + Sx] = Foreground;
          }
        }
      }
    }

    CurX += Adv * Scale;
  }

  Ui->Gop->Blt (Ui->Gop, Buffer, EfiBltBufferToVideo, 0, 0, X, Y, W, Ch, 0);
  FreePool (Buffer);
  return W;
}

//
// Draw case-sensitive Spleen 8x16 pixel Text (with slashed '0') for
// diagnostic and error lines.
//
STATIC
UINTN
DrawBodyText (
  IN UNIXNU_UI                      *Ui,
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
  CONST UINT8                    *Glyph;
  UINTN                          Base;

  Len = StrLen (Text);
  Cw  = UNIXNU_OC_BODY_GLYPH_WIDTH * Scale;
  Ch  = UNIXNU_OC_BODY_GLYPH_HEIGHT * Scale;
  if ((Len == 0) || (Scale == 0) || (X >= Ui->Width) || (Y + Ch > Ui->Height)) {
    return 0;
  }

  if ((MaxWidth > 0) && (Len * Cw > MaxWidth)) {
    Len = MaxWidth / Cw;
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
    Glyph = gOcBodyFontGlyphs[GlyphIndex (Text[Index])];
    for (Row = 0; Row < UNIXNU_OC_BODY_GLYPH_HEIGHT; Row++) {
      for (Col = 0; Col < UNIXNU_OC_BODY_GLYPH_WIDTH; Col++) {
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

//
// Copy Text into Out, truncating with "..." when it exceeds MaxChars.
//
#define TEXT_FIT_MAX  160

STATIC
VOID
FitText (
  IN  CONST CHAR16  *Text,
  IN  UINTN         MaxChars,
  OUT CHAR16        *Out
  )
{
  UINTN  Len;

  MaxChars = MIN (MaxChars, (UINTN)TEXT_FIT_MAX);
  if (MaxChars == 0) {
    Out[0] = L'\0';
    return;
  }

  Len = StrLen (Text);
  if (Len <= MaxChars) {
    CopyMem (Out, Text, (Len + 1) * sizeof (CHAR16));
    return;
  }

  if (MaxChars <= 3) {
    CopyMem (Out, Text, MaxChars * sizeof (CHAR16));
    Out[MaxChars] = L'\0';
    return;
  }

  CopyMem (Out, Text, (MaxChars - 3) * sizeof (CHAR16));
  Out[MaxChars - 3] = L'.';
  Out[MaxChars - 2] = L'.';
  Out[MaxChars - 1] = L'.';
  Out[MaxChars]     = L'\0';
}

//
// Copy Text into Out, truncating with "..." when its proportional Silkscreen
// width exceeds MaxPx.
//
STATIC
VOID
FitTextWidth (
  IN  CONST CHAR16  *Text,
  IN  UINTN         MaxPx,
  IN  UINTN         Scale,
  OUT CHAR16        *Out
  )
{
  UINTN  Len;
  UINTN  EllipsisPx;
  UINTN  Budget;
  UINTN  Used;
  UINTN  Count;
  UINTN  AdvPx;

  if ((MaxPx == 0) || (Scale == 0)) {
    Out[0] = L'\0';
    return;
  }

  Len = MIN (StrLen (Text), (UINTN)TEXT_FIT_MAX);
  if (MeasureTextN (Text, Len, Scale) <= MaxPx) {
    CopyMem (Out, Text, Len * sizeof (CHAR16));
    Out[Len] = L'\0';
    return;
  }

  EllipsisPx = MeasureText (L"...", Scale);
  if (MaxPx <= EllipsisPx) {
    Used  = 0;
    Count = 0;
    while (Count < Len) {
      AdvPx = gOcFontWidths[GlyphIndex (Text[Count])] * Scale;
      if (Used + AdvPx > MaxPx) {
        break;
      }

      Used += AdvPx;
      Count++;
    }

    CopyMem (Out, Text, Count * sizeof (CHAR16));
    Out[Count] = L'\0';
    return;
  }

  Budget = MaxPx - EllipsisPx;
  Used   = 0;
  Count  = 0;
  while ((Count < Len) && (Count + 3 < TEXT_FIT_MAX)) {
    AdvPx = gOcFontWidths[GlyphIndex (Text[Count])] * Scale;
    if (Used + AdvPx > Budget) {
      break;
    }

    Used += AdvPx;
    Count++;
  }

  CopyMem (Out, Text, Count * sizeof (CHAR16));
  Out[Count]     = L'.';
  Out[Count + 1] = L'.';
  Out[Count + 2] = L'.';
  Out[Count + 3] = L'\0';
}

STATIC
VOID
FitMenuTextWidth (
  IN  CONST CHAR16  *Text,
  IN  UINTN         MaxPx,
  IN  UINTN         Scale,
  OUT CHAR16        *Out
  )
{
  UINTN  Len;
  UINTN  EllipsisPx;
  UINTN  Budget;
  UINTN  Used;
  UINTN  Count;
  UINTN  AdvPx;

  if ((MaxPx == 0) || (Scale == 0)) {
    Out[0] = L'\0';
    return;
  }

  Len = MIN (StrLen (Text), (UINTN)TEXT_FIT_MAX);
  if (MeasureMenuTextN (Text, Len, Scale) <= MaxPx) {
    CopyMem (Out, Text, Len * sizeof (CHAR16));
    Out[Len] = L'\0';
    return;
  }

  EllipsisPx = MeasureMenuText (L"...", Scale);
  if (MaxPx <= EllipsisPx) {
    Used  = 0;
    Count = 0;
    while (Count < Len) {
      AdvPx = gOcMenuFontWidths[GlyphIndex (Text[Count])] * Scale;
      if (Used + AdvPx > MaxPx) {
        break;
      }

      Used += AdvPx;
      Count++;
    }

    CopyMem (Out, Text, Count * sizeof (CHAR16));
    Out[Count] = L'\0';
    return;
  }

  Budget = MaxPx - EllipsisPx;
  Used   = 0;
  Count  = 0;
  while ((Count < Len) && (Count + 3 < TEXT_FIT_MAX)) {
    AdvPx = gOcMenuFontWidths[GlyphIndex (Text[Count])] * Scale;
    if (Used + AdvPx > Budget) {
      break;
    }

    Used += AdvPx;
    Count++;
  }

  CopyMem (Out, Text, Count * sizeof (CHAR16));
  Out[Count]     = L'.';
  Out[Count + 1] = L'.';
  Out[Count + 2] = L'.';
  Out[Count + 3] = L'\0';
}

STATIC
VOID
DrawCenteredIn (
  IN UNIXNU_UI                      *Ui,
  IN UINTN                          Left,
  IN UINTN                          Width,
  IN UINTN                          Y,
  IN CONST CHAR16                   *Text,
  IN UINTN                          Scale,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Foreground,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Background
  )
{
  CHAR16  Fit[TEXT_FIT_MAX + 1];
  UINTN   W;

  if (Width == 0) {
    return;
  }

  FitTextWidth (Text, Width, Scale, Fit);
  W = MeasureText (Fit, Scale);
  if (W > Width) {
    W = Width;
  }

  DrawText (Ui, Left + (Width - W) / 2, Y, Fit, Scale, Foreground, Background, Width);
}

STATIC
VOID
DrawBodyCenteredIn (
  IN UNIXNU_UI                      *Ui,
  IN UINTN                          Left,
  IN UINTN                          Width,
  IN UINTN                          Y,
  IN CONST CHAR16                   *Text,
  IN UINTN                          Scale,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Foreground,
  IN EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Background
  )
{
  CHAR16  Fit[TEXT_FIT_MAX + 1];
  UINTN   Cw;
  UINTN   W;

  Cw = UNIXNU_OC_BODY_GLYPH_WIDTH * Scale;
  if ((Cw == 0) || (Width < Cw)) {
    return;
  }

  FitText (Text, Width / Cw, Fit);
  W = StrLen (Fit) * Cw;
  DrawBodyText (Ui, Left + (Width - W) / 2, Y, Fit, Scale, Foreground, Background, Width);
}

STATIC
UINTN
FooterScale (
  IN UNIXNU_UI  *Ui
  )
{
  if (Ui->Scale >= 4) {
    return Ui->Scale - 2;
  }

  return (Ui->Scale > 1) ? Ui->Scale - 1 : 1;
}

STATIC
UINTN
ErrorBodyScale (
  IN UNIXNU_UI  *Ui
  )
{
  return MAX ((UINTN)1, (FooterScale (Ui) + 1) / 2);
}

//
// Draw the compact all-white uniXNU pixel wordmark at (X0, Y).
// Returns rendered height in pixels.
//
STATIC
UINTN
DrawWordmarkAt (
  IN UNIXNU_UI  *Ui,
  IN UINTN      X0,
  IN UINTN      Y,
  IN UINTN      Block
  )
{
  UINTN  Row;
  UINTN  Col;

  for (Row = 0; Row < WORDMARK_ROWS; Row++) {
    for (Col = 0; Col < WORDMARK_COLS; Col++) {
      if (mWordmark[Row][Col] == 'W') {
        FillRect (Ui, X0 + Col * Block, Y + Row * Block, Block, Block, mLogoWhite);
      }
    }
  }

  return WORDMARK_ROWS * Block;
}

//
// Draw a keybind hint string like "Up/Down: select    Enter: boot" in OpenCode
// two-tone style: key tokens in bright white, descriptions in muted grey.
// Returns TRUE if two-tone segments were parsed and drawn.
//
STATIC
BOOLEAN
DrawKeybindLine (
  IN UNIXNU_UI      *Ui,
  IN UINTN          Left,
  IN UINTN          Width,
  IN UINTN          Y,
  IN CONST CHAR16   *Text,
  IN UINTN          Scale,
  IN BOOLEAN        RightAlign
  )
{
  CONST CHAR16  *P;
  CONST CHAR16  *Sep;
  CONST CHAR16  *End;
  UINTN         SpaceW;
  UINTN         GapW;
  UINTN         TotalW;
  UINTN         Pairs;
  UINTN         X;
  CHAR16        KeyBuf[48];
  CHAR16        DescBuf[48];
  UINTN         KeyLen;
  UINTN         DescLen;

  SpaceW = gOcFontWidths[0] * Scale;
  GapW   = (3 * UNIXNU_OC_GLYPH_WIDTH * Scale) / 2;
  if ((Width == 0) || (Scale == 0)) {
    return FALSE;
  }

  //
  // First pass: measure total rendered pixel width and confirm there is at
  // least one "Key: desc" or "Key = desc" pair.
  //
  TotalW = 0;
  Pairs  = 0;
  P      = Text;
  while (*P != L'\0') {
    while (*P == L' ') {
      P++;
    }

    if (*P == L'\0') {
      break;
    }

    //
    // Split segments on two or more consecutive spaces.
    //
    End = P;
    while (*End != L'\0') {
      if ((End[0] == L' ') && (End[1] == L' ')) {
        break;
      }

      End++;
    }

    Sep = NULL;
    for (CONST CHAR16 *Q = P; Q < End; Q++) {
      if ((*Q == L':') || (*Q == L'=')) {
        Sep = Q;
        break;
      }
    }

    if (Sep == NULL) {
      return FALSE;
    }

    KeyLen = (UINTN)(Sep - P);
    while ((KeyLen > 0) && (P[KeyLen - 1] == L' ')) {
      KeyLen--;
    }

    Sep++;
    while ((Sep < End) && (*Sep == L' ')) {
      Sep++;
    }

    DescLen = (UINTN)(End - Sep);
    while ((DescLen > 0) && (Sep[DescLen - 1] == L' ')) {
      DescLen--;
    }

    if ((KeyLen == 0) || (DescLen == 0) || (KeyLen >= ARRAY_SIZE (KeyBuf)) || (DescLen >= ARRAY_SIZE (DescBuf))) {
      return FALSE;
    }

    if (Pairs > 0) {
      TotalW += GapW;
    }

    TotalW += MeasureTextN (P, KeyLen, Scale) + SpaceW + MeasureTextN (Sep, DescLen, Scale);
    Pairs++;
    P = End;
  }

  if ((Pairs == 0) || (TotalW > Width)) {
    return FALSE;
  }

  if (RightAlign) {
    X = Left + Width - TotalW;
  } else {
    X = Left + (Width - TotalW) / 2;
  }

  //
  // Second pass: render bright keys and dim descriptions.
  //
  Pairs = 0;
  P     = Text;
  while (*P != L'\0') {
    while (*P == L' ') {
      P++;
    }

    if (*P == L'\0') {
      break;
    }

    End = P;
    while (*End != L'\0') {
      if ((End[0] == L' ') && (End[1] == L' ')) {
        break;
      }

      End++;
    }

    Sep = P;
    while ((Sep < End) && (*Sep != L':') && (*Sep != L'=')) {
      Sep++;
    }

    KeyLen = (UINTN)(Sep - P);
    while ((KeyLen > 0) && (P[KeyLen - 1] == L' ')) {
      KeyLen--;
    }

    CopyMem (KeyBuf, P, KeyLen * sizeof (CHAR16));
    KeyBuf[KeyLen] = L'\0';

    Sep++;
    while ((Sep < End) && (*Sep == L' ')) {
      Sep++;
    }

    DescLen = (UINTN)(End - Sep);
    while ((DescLen > 0) && (Sep[DescLen - 1] == L' ')) {
      DescLen--;
    }

    CopyMem (DescBuf, Sep, DescLen * sizeof (CHAR16));
    DescBuf[DescLen] = L'\0';

    if (Pairs > 0) {
      X += GapW;
    }

    X += DrawText (Ui, X, Y, KeyBuf, Scale, mText, mBackground, 0);
    X += SpaceW;
    X += DrawText (Ui, X, Y, DescBuf, Scale, mDim, mBackground, 0);
    Pairs++;
    P = End;
  }

  return TRUE;
}

//
// Draw Status line 0 (directly beneath the uniXNU wordmark). For countdown
// text "Booting <Title> in <N> s", highlight <Title> in warm amber like
// OpenCode's subtitle.
//
STATIC
VOID
DrawStatusSubtitle (
  IN UNIXNU_UI      *Ui,
  IN CONST CHAR16   *Text
  )
{
  UINTN                          Ch;
  UINTN                          BaseCh;
  UINTN                          Scale;
  UINTN                          Y;
  UINTN                          AreaLeft;
  UINTN                          AreaWidth;
  CONST CHAR16                   *InPart;
  UINTN                          PrefixLen;
  UINTN                          MidLen;
  UINTN                          TotalW;
  UINTN                          X;
  CHAR16                         MidBuf[96];
  CHAR16                         Fit[TEXT_FIT_MAX + 1];
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Color;

  Scale     = Ui->Portrait ? FooterScale (Ui) : Ui->Scale;
  BaseCh    = UNIXNU_OC_GLYPH_HEIGHT * Scale;
  AreaLeft  = Ui->StatusLeft;
  AreaWidth = Ui->StatusWidth;

  //
  // Clear only the status slot so the top-left uniXNU wordmark stays intact.
  //
  FillRect (Ui, AreaLeft, Ui->StatusTop, AreaWidth, BaseCh + Scale * 2, mBackground);
  if ((Text[0] == L'\0') || (AreaWidth == 0)) {
    return;
  }

  //
  // Shrink to footer scale automatically if a long confirmation prompt exceeds
  // the right-hand header slot width.
  //
  if (!Ui->Portrait && (MeasureText (Text, Scale) > AreaWidth)) {
    Scale = FooterScale (Ui);
  }

  Ch = UNIXNU_OC_GLYPH_HEIGHT * Scale;
  Y  = Ui->StatusTop + ((BaseCh > Ch) ? (BaseCh - Ch) : 0);

  PrefixLen = 8; // StrLen (L"Booting ")
  if ((StrnCmp (Text, L"Booting ", PrefixLen) == 0) && ((InPart = StrStr (Text + PrefixLen, L" in ")) != NULL)) {
    MidLen = (UINTN)(InPart - (Text + PrefixLen));
    TotalW = MeasureText (Text, Scale);
    if ((MidLen > 0) && (MidLen < ARRAY_SIZE (MidBuf)) && (TotalW <= AreaWidth)) {
      CopyMem (MidBuf, Text + PrefixLen, MidLen * sizeof (CHAR16));
      MidBuf[MidLen] = L'\0';
      X              = Ui->Portrait ? (AreaLeft + (AreaWidth - TotalW) / 2) : (AreaLeft + AreaWidth - TotalW);
      X             += DrawText (Ui, X, Y, L"Booting ", Scale, mDim, mBackground, 0);
      X             += DrawText (Ui, X, Y, MidBuf, Scale, mAmber, mBackground, 0);
      DrawText (Ui, X, Y, InPart, Scale, mDim, mBackground, 0);
      return;
    }
  }

  Color = (StrCmp (Text, L"Select an entry") == 0) ? mDim : mAmber;
  if (Ui->Portrait) {
    DrawCenteredIn (Ui, AreaLeft, AreaWidth, Y, Text, Scale, Color, mBackground);
  } else {
    FitTextWidth (Text, AreaWidth, Scale, Fit);
    TotalW = MeasureText (Fit, Scale);
    X      = (AreaWidth > TotalW) ? (AreaLeft + AreaWidth - TotalW) : AreaLeft;
    DrawText (Ui, X, Y, Fit, Scale, Color, mBackground, AreaWidth);
  }
}

STATIC
CONST CHAR16 *
TypeTag (
  IN CONST UNIXNU_ENTRY  *Entry
  )
{
  switch (Entry->Type) {
    case UniXNUEntryEfi:    return L"EFI";
    case UniXNUEntryXnu:    return L"XNU";
    case UniXNUEntryAction: return L"ACTION";
    default:                return L"";
  }
}

// ---------------------------------------------------------------------------
// Public
// ---------------------------------------------------------------------------

VOID
UniXNUUiOcLikeInit (
  IN  UNIXNU_CONFIG  *Config,
  OUT UNIXNU_UI      *Ui
  )
{
  if (Ui->Portrait) {
    Ui->Margin = Ui->Width / 14;
    Ui->Scale  = (Config->Scale > 0) ? Config->Scale : MAX ((UINTN)2, Ui->Width / 240);
  } else {
    Ui->Margin = Ui->Width / 16;
    Ui->Scale  = (Config->Scale > 0) ? Config->Scale : MAX ((UINTN)2, Ui->Height / 360);
  }
}

VOID
UniXNUUiOcLikeDrawFrame (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config
  )
{
  UINTN   Cw;
  UINTN   Ch;
  UINTN   Fs;
  UINTN   Fcw;
  UINTN   Fch;
  UINTN   Index;
  UINTN   Longest;
  UINTN   WordBlock;
  UINTN   LogoW;
  UINTN   LogoH;
  UINTN   PadTop;
  UINTN   PadBot;
  UINTN   MetaH;
  UINTN   CardW;
  UINTN   CardH;
  UINTN   SubGap;
  UINTN   CardGap;
  UINTN   FootGap;
  UINTN   Status0H;
  UINTN   FooterBlockH;
  UINTN   TotalH;
  UINTN   TopY;
  UINTN   CardY;
  UINTN   MetaY;
  UINTN   InnerX;
  UINTN   InnerW;
  UINTN   X;
  UINTN   MaxRows;
  UINTN   ExtraY;
  CHAR16  Line[160];
  CHAR16  ResBuf[32];
  CHAR16  VerBuf[32];
  CHAR16  Fit[TEXT_FIT_MAX + 1];

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  Cw      = UNIXNU_OC_GLYPH_WIDTH * Ui->Scale;
  Ch      = UNIXNU_OC_GLYPH_HEIGHT * Ui->Scale;
  Fs      = FooterScale (Ui);
  Fcw     = UNIXNU_OC_GLYPH_WIDTH * Fs;
  Fch     = UNIXNU_OC_GLYPH_HEIGHT * Fs;

  FillRect (Ui, 0, 0, Ui->Width, Ui->Height, mBackground);

  //
  // Card width: generous OpenCode floating column (~56% on landscape, ~86% on portrait).
  //
  if (Ui->Portrait) {
    CardW = Ui->Width - 2 * Ui->Margin;
  } else {
    Longest = 0;
    for (Index = 0; Index < Config->EntryCount; Index++) {
      Longest = MAX (
                  Longest,
                  MeasureMenuText (Config->Entries[Index].Title, Ui->Scale) +
                  MeasureText (TypeTag (&Config->Entries[Index]), Ui->Scale) +
                  10 * Cw
                  );
    }

    CardW = MAX (Longest, (Ui->Width * 56) / 100);
    CardW = MIN (CardW, Ui->Width - 4 * Cw);
  }

  Ui->MenuWidth = CardW;
  Ui->MenuLeft  = (Ui->Width - CardW) / 2;
  Ui->RowHeight = UNIXNU_OC_MENU_GLYPH_HEIGHT * Ui->Scale + Ui->Scale * 4;

  //
  // Compact all-white uniXNU wordmark perched at the top-left of the
  // menu card. On landscape, Status line 0 sits right-aligned on the same bar.
  //
  WordBlock    = MAX ((UINTN)2, CardW / (WORDMARK_COLS * 5));
  LogoW        = Config->ShowLogo ? (WORDMARK_COLS * WordBlock) : MeasureText (Config->Title, Ui->Scale);
  LogoH        = Config->ShowLogo ? (WORDMARK_ROWS * WordBlock) : Ch;
  SubGap       = Ui->Portrait ? (Fch / 2) : 0;
  Status0H     = Ui->Portrait ? Fch : 0;
  CardGap      = Ch / 2 + Ui->Scale * 3;
  PadTop       = Ch / 2 + Ui->Scale * 3;
  PadBot       = Ch / 2 + Ui->Scale * 3;
  MetaH        = Fch + Ui->Scale * 2;
  FootGap      = Fch;
  FooterBlockH = Fch * 4;

  //
  // Determine how many entry rows fit comfortably inside the vertical budget.
  //
  if (Ui->Height > LogoH + SubGap + Status0H + CardGap + PadTop + PadBot + MetaH + FootGap + FooterBlockH + Ch * 2) {
    MaxRows = (Ui->Height - (LogoH + SubGap + Status0H + CardGap + PadTop + PadBot + MetaH + FootGap + FooterBlockH + Ch * 2)) / Ui->RowHeight;
  } else {
    MaxRows = 1;
  }

  Ui->VisibleRows = MIN (Config->EntryCount, MAX (MaxRows, (UINTN)1));
  CardH           = PadTop + Ui->VisibleRows * Ui->RowHeight + Ui->Scale * 5 + MetaH + PadBot;
  Ui->CardHeight  = CardH;

  TotalH = LogoH + SubGap + Status0H + CardGap + CardH + FootGap + FooterBlockH;
  TopY   = (Ui->Height > TotalH) ? (Ui->Height - TotalH) / 2 : Ch;

  //
  // 1. Compact all-white uniXNU wordmark at top-left of the menu card.
  //
  if (Config->ShowLogo) {
    DrawWordmarkAt (Ui, Ui->MenuLeft, TopY, WordBlock);
  } else {
    DrawText (Ui, Ui->MenuLeft, TopY, Config->Title, Ui->Scale, mLogoWhite, mBackground, CardW / 2);
  }

  //
  // 2. Status line 0 slot: right-aligned on the logo header bar (landscape), or
  // directly beneath the logo (portrait).
  //
  if (Ui->Portrait) {
    Ui->StatusTop   = TopY + LogoH + SubGap;
    Ui->StatusLeft  = Ui->MenuLeft;
    Ui->StatusWidth = CardW;
    CardY           = Ui->StatusTop + Status0H + CardGap;
  } else {
    Ui->StatusTop   = (LogoH > Ch) ? (TopY + LogoH - Ch) : TopY;
    Ui->StatusLeft  = Ui->MenuLeft + LogoW + Cw;
    Ui->StatusWidth = (CardW > LogoW + Cw) ? (CardW - LogoW - Cw) : 0;
    CardY           = TopY + LogoH + CardGap;
  }

  //
  // 3. Borderless dark TUI card.
  //
  Ui->CardTop    = CardY;
  Ui->MenuTop    = CardY + PadTop;
  Ui->ContentTop = CardY;

  FillRect (Ui, Ui->MenuLeft, CardY, CardW, CardH, mSurface);

  //
  // Metadata bar at the bottom of the card (clean space separation, no dividers).
  //
  InnerX = Ui->MenuLeft + Cw;
  InnerW = (CardW > 2 * Cw) ? (CardW - 2 * Cw) : 0;
  MetaY  = Ui->MenuTop + Ui->VisibleRows * Ui->RowHeight + Ui->Scale * 5;
  X      = InnerX;
  X     += DrawText (Ui, X, MetaY, Config->Title, Fs, mAccent, mSurface, InnerW / 3);
  if (!Ui->Portrait && (InnerW > 20 * Fcw)) {
    X += DrawText (Ui, X, MetaY, L"   ", Fs, mDim, mSurface, 0);
    UnicodeSPrint (ResBuf, sizeof (ResBuf), L"   %ux%u", Ui->Width, Ui->Height);
    FitTextWidth (
      Config->SourceLabel,
      (InnerW > (X - InnerX) + MeasureText (ResBuf, Fs) + MeasureText (L"UEFI", Fs) + 3 * Fcw)
        ? (InnerW - (X - InnerX) - MeasureText (ResBuf, Fs) - MeasureText (L"UEFI", Fs) - 3 * Fcw)
        : 0,
      Fs,
      Fit
      );
    X += DrawText (Ui, X, MetaY, Fit, Fs, mTextSoft, mSurface, 0);
    if ((X - InnerX) + MeasureText (ResBuf, Fs) + MeasureText (L"UEFI", Fs) + 2 * Fcw < InnerW) {
      DrawText (Ui, X, MetaY, ResBuf, Fs, mDim, mSurface, 0);
    }
  } else if (InnerW > 12 * Fcw) {
    UnicodeSPrint (ResBuf, sizeof (ResBuf), L"  %ux%u", Ui->Width, Ui->Height);
    DrawText (Ui, X, MetaY, ResBuf, Fs, mDim, mSurface, InnerW - (X - InnerX) - MeasureText (L"UEFI", Fs) - 2 * Fcw);
  }

  //
  // Right-aligned warm amber badge ("UEFI") inside the card footer, matching OpenCode.
  //
  if (InnerW > MeasureText (L"UEFI", Fs) + 2 * Fcw) {
    DrawText (Ui, InnerX + InnerW - MeasureText (L"UEFI", Fs), MetaY, L"UEFI", Fs, mAmber, mSurface, 0);
  }

  //
  // 4. Footer region right underneath the card.
  //
  Ui->FooterTop     = CardY + CardH + FootGap;
  Ui->ContentBottom = Ui->FooterTop;

  //
  // Save source label on the left of the footer line (landscape); DrawStatus(1)
  // renders right-aligned keybinds alongside it.
  //
  FitText (Config->SourceLabel, ARRAY_SIZE (Ui->SourceHint) - 1, Ui->SourceHint);
  if (!Ui->Portrait) {
    FitTextWidth (Ui->SourceHint, CardW / 3, Fs, Fit);
    DrawText (Ui, Ui->MenuLeft, Ui->FooterTop, Fit, Fs, mDim, mBackground, CardW / 3);
  }

  //
  // Error / Notice / Info lines below status line 2.
  //
  ExtraY = Ui->FooterTop + 2 * (Fch + Fch / 2);
  Line[0] = L'\0';
  if (Config->Error[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"config error: %a", Config->Error);
  } else if (Config->Notice[0] != '\0') {
    UnicodeSPrint (Line, sizeof (Line), L"%a", Config->Notice);
  }

  if ((Line[0] != L'\0') && (ExtraY + UNIXNU_OC_BODY_GLYPH_HEIGHT * ErrorBodyScale (Ui) < Ui->Height)) {
    DrawBodyCenteredIn (Ui, Ui->MenuLeft, CardW, ExtraY, Line, ErrorBodyScale (Ui), mError, mBackground);
    ExtraY += UNIXNU_OC_BODY_GLYPH_HEIGHT * ErrorBodyScale (Ui) + Fch / 2;
  }

  if ((Ui->Info[0] != L'\0') && (ExtraY + UNIXNU_OC_BODY_GLYPH_HEIGHT * ErrorBodyScale (Ui) < Ui->Height)) {
    DrawBodyCenteredIn (Ui, Ui->MenuLeft, CardW, ExtraY, Ui->Info, ErrorBodyScale (Ui), mDim, mBackground);
  }

  //
  // 5. Subtle version string tucked in the bottom-right corner (matching OpenCode).
  //
  UnicodeSPrint (VerBuf, sizeof (VerBuf), L"%a", UNIXNU_VERSION_STRING);
  if ((Ui->Width > MeasureText (VerBuf, Fs) + 2 * Fcw) && (Ui->Height > Fch * 2)) {
    DrawText (
      Ui,
      Ui->Width - MeasureText (VerBuf, Fs) - 2 * Fcw,
      Ui->Height - Fch - Fch,
      VerBuf,
      Fs,
      mDim,
      mBackground,
      0
      );
  }
}

VOID
UniXNUUiOcLikeDrawEntry (
  IN UNIXNU_UI      *Ui,
  IN UNIXNU_CONFIG  *Config,
  IN UINTN          Index,
  IN BOOLEAN        Selected
  )
{
  UNIXNU_ENTRY                   *Entry;
  UINTN                          Y;
  UINTN                          RowH;
  UINTN                          PadY;
  UINTN                          Cw;
  UINTN                          Ch;
  UINTN                          InnerX;
  UINTN                          TitleX;
  UINTN                          TagW;
  UINTN                          MaxTitleW;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL  Bg;
  CONST CHAR16                   *Tag;
  CHAR16                         NumBuf[16];
  CHAR16                         Fit[TEXT_FIT_MAX + 1];

  if (Index >= Ui->VisibleRows) {
    return;
  }

  Entry = &Config->Entries[Index];
  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  Cw   = UNIXNU_OC_GLYPH_WIDTH * Ui->Scale;
  Ch   = 7 * Ui->Scale; // Fusion Pixel 10px cap height (x-height 5*S matches Silkscreen cap).
  Y    = Ui->MenuTop + Index * Ui->RowHeight;
  RowH = Ui->RowHeight - Ui->Scale;
  PadY = (RowH > Ch) ? ((RowH + Ch) / 2) : RowH; // Shared baseline offset from Y.
  Bg   = Selected ? mSurfaceSelected : mSurface;
  Tag  = TypeTag (Entry);
  TagW = MeasureText (Tag, Ui->Scale);

  //
  // Fill row surface across the full card width.
  //
  FillRect (Ui, Ui->MenuLeft, Y, Ui->MenuWidth, RowH, Bg);

  {
    UINTN  SilkY;
    UINTN  PixY;

    SilkY = (PadY >= 6 * Ui->Scale) ? (Y + PadY - 6 * Ui->Scale) : Y;
    PixY  = (PadY >= 8 * Ui->Scale) ? (Y + PadY - 8 * Ui->Scale) : Y;

    InnerX = Ui->MenuLeft + Cw;
    if (Selected) {
      DrawText (Ui, InnerX, SilkY, L">", Ui->Scale, mAccent, Bg, 0);
    }

    UnicodeSPrint (NumBuf, sizeof (NumBuf), L"%u", (UINT32)Index + 1);
    DrawText (Ui, InnerX + 2 * Cw, SilkY, NumBuf, Ui->Scale, Selected ? mAccent : mDim, Bg, 0);

    TitleX    = InnerX + 4 * Cw;
    MaxTitleW = (Ui->MenuLeft + Ui->MenuWidth > TitleX + TagW + 2 * Cw)
                ? (Ui->MenuLeft + Ui->MenuWidth - TitleX - TagW - 2 * Cw)
                : 0;
    FitMenuTextWidth (Entry->Title, MaxTitleW, Ui->Scale, Fit);
    DrawMenuText (Ui, TitleX, PixY, Fit, Ui->Scale, Selected ? mText : mTextSoft, Bg, MaxTitleW);

    if (TagW > 0) {
      DrawText (
        Ui,
        Ui->MenuLeft + Ui->MenuWidth - Cw - TagW,
        SilkY,
        Tag,
        Ui->Scale,
        Selected ? mAmber : mDim,
        Bg,
        0
        );
    }
  }
}

VOID
UniXNUUiOcLikeDrawStatus (
  IN UNIXNU_UI      *Ui,
  IN UINTN          Line,
  IN CONST CHAR16   *Text
  )
{
  UINTN   Fs;
  UINTN   Fcw;
  UINTN   Fch;
  UINTN   Y;
  UINTN   RightLeft;
  UINTN   RightW;
  CHAR16  Fit[TEXT_FIT_MAX + 1];

  if (Line >= STATUS_LINES) {
    return;
  }

  if (Ui->Mode != UniXNUUiGraphics) {
    return;
  }

  if (Line == 0) {
    DrawStatusSubtitle (Ui, Text);
    return;
  }

  Fs  = FooterScale (Ui);
  Fcw = UNIXNU_OC_GLYPH_WIDTH * Fs;
  Fch = UNIXNU_OC_GLYPH_HEIGHT * Fs;

  if (Line == 1) {
    Y = Ui->FooterTop;
    FillRect (Ui, 0, Y, Ui->Width, Fch + Fs * 2, mBackground);
    if (!Ui->Portrait && (Text[0] != L'\0') && (Text[0] != L'<')) {
      //
      // Landscape OpenCode footer: SourceLabel on left, two-tone keybinds on right.
      //
      FitTextWidth (Ui->SourceHint, Ui->MenuWidth / 3, Fs, Fit);
      DrawText (Ui, Ui->MenuLeft, Y, Fit, Fs, mDim, mBackground, Ui->MenuWidth / 3);
      RightLeft = Ui->MenuLeft + Ui->MenuWidth / 3 + Fcw;
      RightW    = (Ui->MenuLeft + Ui->MenuWidth > RightLeft) ? (Ui->MenuLeft + Ui->MenuWidth - RightLeft) : 0;
      if (!DrawKeybindLine (Ui, RightLeft, RightW, Y, Text, Fs, TRUE)) {
        //
        // Fall back to full-width centered two-tone or plain text if hints are wider than 2/3 card.
        //
        FillRect (Ui, 0, Y, Ui->Width, Fch + Fs * 2, mBackground);
        if (!DrawKeybindLine (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Fs, FALSE)) {
          DrawCenteredIn (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Fs, mDim, mBackground);
        }
      }
    } else if (Text[0] == L'<') {
      //
      // Confirmation choice selector ("<  Cancel  >").
      //
      DrawCenteredIn (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Ui->Scale, mAmber, mBackground);
    } else if (Text[0] != L'\0') {
      if (!DrawKeybindLine (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Fs, FALSE)) {
        DrawCenteredIn (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Fs, mDim, mBackground);
      }
    }

    return;
  }

  //
  // Line == 2: secondary notice/error (case-sensitive Spleen 8x16) or key hints.
  //
  Y = Ui->FooterTop + Fch + Fch / 2;
  FillRect (Ui, 0, Y, Ui->Width, MAX (Fch + Fs * 2, UNIXNU_OC_BODY_GLYPH_HEIGHT * ErrorBodyScale (Ui) + 2), mBackground);
  if (Text[0] == L'\0') {
    return;
  }

  if (!DrawKeybindLine (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, Fs, FALSE)) {
    DrawBodyCenteredIn (Ui, Ui->MenuLeft, Ui->MenuWidth, Y, Text, ErrorBodyScale (Ui), mError, mBackground);
  }
}
