# Deferred issues

- The default command/file-read sandbox fails with `mountinfo path is not absolute`; commands require escalation and updates use the system patch editor.
- The vendor temperature-preference reader throws on GDS 112 for accounts without a profile (for example, `device`); saving preferences also targets the absent profile. Use the configured app account.
- The demo clock stayed unset in the automated Chrome session while Firefox showed a demo time; the browser difference remains uninvestigated.
- Browser mode defaults to debug mode and German language in the vendor code, whereas Electron respects its startup settings. Review these runtime differences separately.
- The vendor browser adapter stores connection credentials in localStorage, disables discovery, and depends on an absent localhost:8184 development proxy for S1 setup.
- Browser IP-link/video actions are stubs; barcode, location, NFC, and biometric paths contain test responses. Camera, weather, and door communication remain unverified.
