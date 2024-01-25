Kalamine
================================================================================

A text-based, cross-platform Keyboard Layout Maker.


Install
--------------------------------------------------------------------------------

All you need is a Python environment with version >= 3.8:

.. code-block:: bash

   python3 -m pip install kalamine

Developers can also install it from the current directory:

.. code-block:: bash

    python3 -m pip install -e .

To install dev dependencies, specify the extra dependencies:

.. code-block:: bash

    python3 -m pip install -e ".[dev]"

And to uninstall kalamine:

.. code-block:: bash

    python3 -m pip uninstall kalamine


If your system requires a ``python virtual environment``, check the XKalamine/pyenv section at the end of this document (you can skip the ``sudo su`` command to install as user).

If you get a ``UnicodeEncodeError`` on Windows, try specifying this environment variable before executing Kalamine:

.. code-block:: powershell

    $Env:PYTHONUTF8 = 1


Building Distributable Layouts
--------------------------------------------------------------------------------

Create a keyboard layout with ``kalamine create``:

.. code-block:: bash

   kalamine create layout.toml                  # make a basic layout
   kalamine create layout.toml --altgr          # use an AltGr layer
   kalamine create layout.toml --1dk            # use a custom dead key
   kalamine create layout.toml --geometry ERGO  # apply an ortholinear geometry

Edit this layout with your preferred text editor:

- the `user guide`_ is available at the end of the ``*.toml`` file
- the layout can be rendered and emulated with ``kalamine watch`` (see next section)

.. _`user guide`: https://github.com/fabi1cazenave/kalamine/tree/master/docs

Build your layout:

.. code-block:: bash

    kalamine make layout.toml

Get all distributable keyboard drivers:

.. code-block:: bash

    dist/
     ├─ layout.ahk         # Windows (user)
     ├─ layout.klc         # Windows (admin)
     ├─ layout.keylayout   # macOS
     ├─ layout.xkb         # Linux (user)
     ├─ layout.xkb_custom  # Linux (root)
     ├─ layout.json        # web
     └─ layout.svg

You can also ask for a single target by specifying the file extension:

.. code-block:: bash

    kalamine make layout.toml --out layout.xkb_custom


Emulating Layouts
--------------------------------------------------------------------------------

Your layout can be emulated in a browser — including dead keys and an AltGr layer, if any.


.. code-block:: bash

    $ kalamine watch layout.toml
    Server started: http://localhost:1664

Check your browser, type in the input area, test your layout. Changes on your TOML file are auto-detected and reloaded automatically.

.. image:: watch.png

Press Ctrl-C when you’re done, and kalamine will write all platform-specific files.


Installing Distributable Layouts
--------------------------------------------------------------------------------


Windows
```````

* get a keyboard layout installer: MSKLC_ (freeware) or KbdEdit_ (shareware);
* load the ``*.klc`` file with it;
* run this installer to generate a setup program;
* run the setup program;
* the keyboard layout appears in the language bar.

.. _MSKLC: https://www.microsoft.com/en-us/download/details.aspx?id=102134
.. _KbdEdit: http://www.kbdedit.com/


macOS
`````

* copy your ``*.keylayout`` file into:

  * either ``~/Library/Keyboard Layouts`` for the current user only,
  * or ``/Library/Keyboard Layouts`` for all users;

* restart your session;
* the keyboard layout appears in the “Language and Text” preferences, “Input Methods” tab.


Linux (root)
````````````

Recent versions of XKB allow *one* custom keyboard layout in root space:

.. code-block:: bash

    sudo cp layout.xkb_custom ${XKB_CONFIG_ROOT:-/usr/share/X11/xkb}/symbols/custom

Your keyboard layout will be listed as “Custom” in the keyboard settings.
This works on both Wayland and X.Org. Depending on your system, you might have to relog to your session or to reboot X completely.

On X.Org you can also select your keyboard layout from the command line:

.. code-block:: bash

    setxkbmap custom  # select your keyboard layout
    setxkbmap us      # get back to QWERTY

On Wayland, this depends on your compositor. For Sway, tweak your keyboard input section like this:

.. code-block:: properties

    input type:keyboard {
        xkb_layout "custom"
    }


Linux (user)
````````````

``*.xkb`` keyboard descriptions can be applied in user-space. The main limitation is that the keyboard layout won’t show up in the keyboard settings.

On X.Org it is straight-forward with ``xkbcomp``:

.. code-block:: bash

    xkbcomp -w10 layout.xkb $DISPLAY

Again, ``setxkbmap`` can be used to get back to the standard us-qwerty layout on X.Org:

.. code-block:: bash

    setxkbmap us

On Wayland, this depends on your compositor. For Sway, tweak your keyboard input section like this:

.. code-block:: properties

    input type:keyboard {
        xkb_file /path/to/layout.xkb
    }


XKalamine
--------------------------------------------------------------------------------

``xkalamine`` is a Linux-specific CLI tool for installing and managing keyboard layouts with XKB, so that they can be listed in the system’s keyboard preferences.


Wayland (user)
``````````````

On Wayland, keyboard layouts can be installed in user-space:

.. code-block:: bash

    # Install a YAML/TOML keyboard layout into ~/.config/xkb
    xkalamine install layout.toml

    # Uninstall Kalamine layouts from ~/.config/xkb
    xkalamine remove us/prog     # remove the kalamine 'prog' layout
    xkalamine remove fr          # remove all kalamine layouts for French
    xkalamine remove "*"         # remove all kalamine layouts

    # List available keyboard layouts
    xkalamine list               # list all kalamine layouts
    xkalamine list fr            # list all kalamine layouts for French
    xkalamine list us --all      # list all layouts for US English
    xkalamine list --all         # list all layouts, ordered by locale

Once installed, layouts are selectable in the desktop environment’s keyboard preferences. On Sway, you can also select a layout like this:

.. code-block:: properties

    input type:keyboard {
        xkb_layout "us"
        xkb_variant "prog"
    }


X.Org (root)
````````````

On X.Org, a layout can be applied on the fly in user-space:

.. code-block:: bash

    # Equivalent to `xkbcomp -w10 layout.xkb $DISPLAY`
    xkalamine apply layout.toml

However, installing a layout so it can be selected in the keyboard preferences requires ``sudo`` privileges:

.. code-block:: bash

    # Install a YAML/TOML keyboard layout into /usr/share/X11/xkb
    sudo xkalamine install layout.toml

    # Uninstall Kalamine layouts from /usr/share/X11/xkb
    sudo xkalamine remove us/prog
    sudo xkalamine remove fr
    sudo xkalamine remove "*"

Once installed, you can apply a keyboard layout like this:

.. code-block:: bash

   setxkbmap us -variant prog

Note that updating XKB will delete all layouts installed using ``sudo xkalamine install``.

Besides, using ``xkalamine`` with ``sudo`` supposes kalamine has been installed as root — hopefully in a pyenv:

.. code-block:: bash

   python -m venv /path/to/pyenv      # create a pyenv (if you don’t already have one)
   cd /path/to/pyenv/bin
   sudo su                            # get root privileges
   ./python -m pip install kalamine   # install Kalamine in the pyenv (don't forget `./`)
   exit                               # return to standard user status
   cd ~/.local/bin                    # symlink the executables in your $PATH dir
   ln -s /path/to/pyenv/bin/kalamine
   ln -s /path/to/pyenv/bin/xkalamine

Sadly, it seems there’s no way to install keyboard layouts in ``~/.config/xkb`` for X.Org. The system keyboard preferences will probably list user-space kayouts, but they won’t be usable on X.Org.

    If you want custom keymaps on your machine, switch to Wayland (and/or fix any remaining issues preventing you from doing so) instead of hoping this will ever work on X.

    -- `Peter Hutterer`_

.. _`Peter Hutterer`: https://who-t.blogspot.com/2020/09/no-user-specific-xkb-configuration-in-x.html


Resources
`````````

XKB is a tricky piece of software. The following resources might be helpful if you want to dig in:

* https://www.charvolant.org/doug/xkb/html/
* https://wiki.archlinux.org/title/X_keyboard_extension
* https://wiki.archlinux.org/title/Xorg/Keyboard_configuration
* https://github.com/xkbcommon/libxkbcommon/blob/master/doc/keymap-format-text-v1.md


Alternative
--------------------------------------------------------------------------------

https://github.com/39aldo39/klfc
