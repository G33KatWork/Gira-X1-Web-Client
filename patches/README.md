# Browser patches

`series.json` defines patch order and reviewed application versions. Run
`python3 setup.py` from the project root to extract a fresh copy of the installer
and apply the complete series. Do not edit the generated `web/` directly.

Each JSON patch contains an ID, rationale, and literal UTF-8 `before`/`after`
edits. Every `before` must occur **exactly once**. Setup validates the full series
before writing patched files and leaves the previous web root intact on failure.
There is no fuzzy matching against changed vendor bundles.

| Patch | Behavior |
| --- | --- |
| 001 | Restore context menus on content and inputs |
| 002 | Permit browser zoom and remove the duplicate viewport |
| 003 | Keep user-requested DOM fullscreen active |
| 004 | Restore global text selection, highlights, and tap feedback |
| 005 | Restore Ctrl+D in demo mode |
| 006 | Set a readable application tab title |
| 008 | Declare HTML5 standards mode |
| 009 | Give the content wrapper a definite height so Firefox renders rooms |
| 010 | Size detail flip wrappers and SVG knob hosts; remove the dimmer's table layout |
| 011 | Use the vendor's modern flex detail layout in Firefox as well as Chrome |

Patch 009 retains the child views' existing header-height calculations. The
Firefox failure was reproduced with room data in the DOM but a zero-height
content area; with the patch, Chrome and Firefox both render a 750px content area
at a 1280×900 viewport.

The grid check alone missed detail controls. With standards mode enabled,
`.coverflip-viewsides` and the front side lacked definite heights, clipping all
controls inside the zero-height `.detail-control`. A dimmer additionally used a
table containing non-cell children; its dial's percentage-height parent collapsed.
The SVG knob factory put dimensions on an inline wrapper and width/height HTML
attributes on a div, which did not establish the SVG viewport height.
Patch 010 fixes those containing blocks without changing control behavior.

The vendor also gates its modern flex layout on a Chrome-version check, sending
Firefox through obsolete percentage sizing. Patch 011 uses the existing modern
layout classes directly in the two detail templates, without spoofing a browser.
Disposable browser checks exercised demo dimmers in Firefox and Chrome at
1280×900, 900×1200, 1280×600, and 1920×1080. Dial/button centers agree within one
pixel and SVG/control heights remain positive and unclipped. Demo dimmer clicks
and timer transitions, climate-control rendering, and settings navigation were
also exercised. These are demo checks, not device
control writes.

For a new installer, inspect any failing source fragment before adjusting the
smallest relevant patch. Verify startup, demo, settings, browser defaults, and
live room rendering in Chrome and Firefox, then update `tested_versions`.
Never weaken the single-match requirement merely to accept a new release.

The build manifest records patch hashes and before/after hashes of modified
assets. Control-specific drag/selection handling and iframe sandbox permissions
remain intact. No explicit F12/devtools blocker was found in this version.
