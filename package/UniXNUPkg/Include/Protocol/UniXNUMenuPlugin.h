/** @file
  Optional protocol for plugins shown in UniXNU's Tools menu.

  A platform (or any DXE driver) installs one instance per tool. UniXNU
  discovers the installed instances at run time, lists their titles in a
  second-level Tools menu, and runs the selected one inside a content region
  that leaves UniXNU's logo, title and status footer visible.

  Copyright (c) 2026, UniXNU contributors. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#ifndef UNIXNU_MENU_PLUGIN_PROTOCOL_H_
#define UNIXNU_MENU_PLUGIN_PROTOCOL_H_

#include <Uefi.h>
#include <Protocol/GraphicsOutput.h>

#define UNIXNU_MENU_PLUGIN_PROTOCOL_SIGNATURE  SIGNATURE_32 ('U','X','M','P')
#define UNIXNU_MENU_PLUGIN_PROTOCOL_VERSION    1

typedef struct _UNIXNU_MENU_PLUGIN_PROTOCOL UNIXNU_MENU_PLUGIN_PROTOCOL;

//
// A rectangular drawing area, in pixels. UniXNU chooses it so the plugin
// stays between the header (logo/title) and the footer (status lines).
//
typedef struct {
  UINT32  X;
  UINT32  Y;
  UINT32  Width;
  UINT32  Height;
} UNIXNU_PLUGIN_RECT;

//
// Update one footer status line. Line 0 is the primary line; the range is the
// same one used by UniXNUUiDrawStatus. UniXNU keeps ownership of the footer.
//
typedef
VOID
(EFIAPI *UNIXNU_MENU_PLUGIN_DRAW_STATUS)(
  IN CONST UNIXNU_MENU_PLUGIN_PROTOCOL  *This,
  IN UINTN                              Line,
  IN CONST CHAR16                       *Text
  );

//
// Run the plugin. The implementation owns its input loop and returns when the
// user chooses to return to the Tools menu. It must draw only inside Content
// and must not call DrawStatus with a line outside the footer range.
//
typedef
EFI_STATUS
(EFIAPI *UNIXNU_MENU_PLUGIN_RUN)(
  IN UNIXNU_MENU_PLUGIN_PROTOCOL    *This,
  IN EFI_GRAPHICS_OUTPUT_PROTOCOL   *Gop,
  IN CONST UNIXNU_PLUGIN_RECT       *Content,
  IN UNIXNU_MENU_PLUGIN_DRAW_STATUS DrawStatus
  );

struct _UNIXNU_MENU_PLUGIN_PROTOCOL {
  UINT32                      Signature;
  UINT32                      Version;
  CONST CHAR16                *Title;   ///< Shown as the Tools menu entry.
  UNIXNU_MENU_PLUGIN_RUN      Run;
};

extern EFI_GUID  gUniXNUMenuPluginProtocolGuid;

#endif
