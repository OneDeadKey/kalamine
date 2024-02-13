KLC Considerations
================================================================================

Kalamine’s `*.klc` outputs can be used:
- either directly by the Microsoft Keyboard Layout Creator, a.k.a. [MSKLC][1],
freeware and unmaintained;
- or as an import format by [KbdEdit][2], shareware and maintained. The Premium
version is required to build distributable installers.

[1]: https://www.microsoft.com/en-us/download/details.aspx?id=102134
[2]: http://www.kbdedit.com/


File Format
--------------------------------------------------------------------------------

Beware: KLC files are encoded in UTF16-LE and require a BOM mark.

KbdEdit is a bit picky: additional line breaks in dead key sections is enough to
break the KLC support.


Limitations
--------------------------------------------------------------------------------

KbdEdit has the most extensive support:
- no particular limitation on the AltGr key;
- dead keys work fine, including chained dead keys (CDK);
- the installer is a single executable file — though unsigned, which raises a
Windows security warning.

MSKLC produces a signed installer (multiple files) but comes with a few limitations:
- AltGr+Spacebar cannot be remapped, making it unsuitable for Bépo;
- chained dead keys are not supported, making it unsuitable for Ergo‑L;
- since Windows 10 (maybe 8), some `1dk` features stopped working — e.g.
QWERTY-Lafayette’s dead key works fine in the preview or when installed on
Windows 7, but not on Windows 10 and 11.

Note: even when chained dead keys are properly supported by the keyboard driver,
they can still cause bugs in other Windows apps — *even without using CDKs*: the
CDK support alone has side-effects that may create bugs, like [this AHK bug][3]
for instance.

[3]: https://github.com/AutoHotkey/AutoHotkey/pull/331


Alternatives
--------------------------------------------------------------------------------

MSKLC comes up with a `kbdutools` executable allowing to build a keyboard driver
DLL that doesn’t have MSKLC’s limitations (AltGr, CDKs…).

The [Windows Driver Kit (WDK)][4] looks like an interesting alternative. There
are even [keyboard layout samples][5] on github.

Installing the DLL onto the system is tricky and implies manipulating the
register base, but it can be done:
- either by replacing the DLL produced by MSKLC in its installer, as described
[in this page][6];
- or by trying to do it manually, as described in the [WinKbdLayouts project][7].

[4]: https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk
[5]: https://github.com/microsoft/Windows-driver-samples/blob/main/input/layout/README.md
[6]: http://accentuez.mon.nom.free.fr/Clavier-CreationClavier.php
[7]: https://github.com/lelegard/winkbdlayouts

Last but not least, the [Neo][10] team has done an impressive job regarding their
Windows drivers, both for the standalone version ([ReNeo][11]) and the installable
version ([KbdNeo2][12]). Kudos, folks!

[10]: https://neo-layout.org
[11]: https://github.com/Rojetto/ReNeo
[12]: https://git.neo-layout.org/neo/neo-layout/src/branch/master/windows/kbdneo2


Links
--------------------------------------------------------------------------------

- https://learn.microsoft.com/en-us/windows/win32/inputdev/about-keyboard-input
- [Michael Kaplan’s archives](https://archives.miloush.net/michkap/archive/) (author of MSKLC)
- [GOTCHAS for keyboard developers using MSKLC](https://metacpan.org/pod/UI::KeyboardLayout#WINDOWS-GOTCHAS-for-keyboard-developers-using-MSKLC)
- https://kbdlayout.info/features/deadkeys
