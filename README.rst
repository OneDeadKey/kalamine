Kalamine
================================================================================

A cross-platform Keyboard Layout Maker, blatantly stolen from the
`qwerty-lafayette <https://qwerty-lafayette.org>`_ project.


Basic Usage
--------------------------------------------------------------------------------

Draw your keyboard layout in ASCII-art and include it in a YAML document:

.. code-block:: yaml

    name: qwerty-ansi
    name8: q-ansi
    description: QWERTY-US layout.
    version: 1.0.0
    geometry: ANSI

    base: |
        ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┲━━━━━━━━━━┓
        │ ~   │ !   │ @   │ #   │ $   │ %   │ ^   │ &   │ *   │ (   │ )   │ _   │ +   ┃          ┃
        │ `   │ 1   │ 2   │ 3   │ 4   │ 5   │ 6   │ 7   │ 8   │ 9   │ 0   │ -   │ =   ┃ ⌫        ┃
        ┢━━━━━┷━━┱──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┺━━┯━━━━━━━┩
        ┃        ┃ Q   │ W   │ E   │ R   │ T   │ Y   │ U   │ I   │ O   │ P   │ {   │ }   │ |     │
        ┃ ↹      ┃     │     │     │     │     │     │     │     │     │     │ [   │ ]   │ \     │
        ┣━━━━━━━━┻┱────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┲━━━━┷━━━━━━━┪
        ┃         ┃ A   │ S   │ D   │ F   │ G   │ H   │ J   │ K   │ L   │ :   │ "   ┃            ┃
        ┃ ⇬       ┃     │     │     │     │     │     │     │     │     │ ;   │ '   ┃ ⏎          ┃
        ┣━━━━━━━━━┻━━┱──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┲━━┻━━━━━━━━━━━━┫
        ┃            ┃ Z   │ X   │ C   │ V   │ B   │ N   │ M   │ <   │ >   │ ?   ┃               ┃
        ┃ ⇧          ┃     │     │     │     │     │     │     │ ,   │ .   │ /   ┃ ⇧             ┃
        ┣━━━━━━━┳━━━━┻━━┳━━┷━━━━┱┴─────┴─────┴─────┴─────┴─────┴─┲━━━┷━━━┳━┷━━━━━╋━━━━━━━┳━━━━━━━┫
        ┃       ┃       ┃       ┃                                ┃       ┃       ┃       ┃       ┃
        ┃ Ctrl  ┃ super ┃ Alt   ┃ ␣                              ┃ Alt   ┃ super ┃ menu  ┃ Ctrl  ┃
        ┗━━━━━━━┻━━━━━━━┻━━━━━━━┹────────────────────────────────┺━━━━━━━┻━━━━━━━┻━━━━━━━┻━━━━━━━┛

Build it:

.. code-block:: bash

    kalamine qwerty-ansi.yaml

Get all keyboard drivers:

.. code-block:: bash

    dist/
    ├── q-ansi.klc        # Windows
    ├── q-ansi.keylayout  # MacOSX
    ├── q-ansi.xkb        # Linux
    └── q-ansi.json


Install
--------------------------------------------------------------------------------

Windows
```````

* download a keyboard layout installer:

  * either MSKLC_ — proprietary freeware, compatible with Windows XP, Vista, Seven, 8, 8.1,
  * or KbdEdit_ — proprietary shareware, compatible with Windows XP, Vista, Seven, 8, 8.1 *and* 10;

* run this installer to generate a setup program;
* run the setup program;
* the keyboard layout appears in the language bar.

.. _MSKLC: https://www.microsoft.com/en-us/download/details.aspx?id=22339
.. _KbdEdit: http://www.kbdedit.com/

MacOSX
``````

* copy your ``*.keylayout`` file into:

  * either ``~/Library/Keyboard Layouts`` for the current user only,
  * or ``/Library/Keyboard Layouts`` for all users;

* restart your session;
* the keyboard layout appears in the “Language and Text” preferences, “Input Methods” tab.

Linux
`````

On Xorg, ``*.xkb`` keyboard descriptions can be applied with ``xkbcomp``:

.. code-block:: bash

    xkbcomp -w10 layout.xkb $DISPLAY

To get back to the standard us-qwerty layout:

.. code-block:: bash

    setxkbmap us


XKalamine
--------------------------------------------------------------------------------

``xkalamine`` is a Linux-specific tool for managing keyboard layouts with ``xkb``.

To apply a keyboard layout in user-space:

.. code-block:: bash

    # equivalent to `xkbcomp -w10 layout.xkb $DISPLAY`
    xkalamine apply layout.yaml

This has limitations: it doesn’t work on Wayland and the keyboard layout doesn’t show up in the Gnome keyboard manager. Besides, on some distros, media keys might stop working.

The proper way to install a keyboard layout on Linux is to modify directly the files in ``/usr/share/X11/xkb``. This is where ``xkalamine`` comes in:

.. code-block:: bash

    sudo xkalamine install layout.yaml

There’s also:

* ``xkalamine list`` to enumerate all installed Kalamine layouts
* ``xkalamine remove`` to uninstall a Kalamine layout
