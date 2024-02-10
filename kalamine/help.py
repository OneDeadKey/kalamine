from typing import List

from .utils import load_data

SEPARATOR = "--------------------------------------------------------------------------------"

MARKDOWN_HEADER = """Defining a Keyboard Layout
================================================================================

Kalamine keyboard layouts are defined with TOML files including this kind of
ASCII-art layer templates:

```
full = '''
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┲━━━━━━━━━━┓
│ ~*~ │ !   │ @   │ #   │ $   │ %   │ ^   │ &   │ *   │ (   │ )   │ _   │ +   ┃          ┃
│ `*` │ 1   │ 2   │ 3   │ 4   │ 5   │ 6*^ │ 7   │ 8   │ 9   │ 0   │ -   │ =   ┃ ⌫        ┃
┢━━━━━┷━━┱──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┺━━┯━━━━━━━┩
┃        ┃ Q   │ W   │ E   │ R   │ T   │ Y   │ U   │ I   │ O   │ P   │ {   │ }   │ |     │
┃ ↹      ┃   @ │   < │   > │   $ │   % │   ^ │   & │   * │   ' │   ` │ [   │ ]   │ \\     │
┣━━━━━━━━┻┱────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┲━━━━┷━━━━━━━┪
┃         ┃ A   │ S   │ D   │ F   │ G   │ H   │ J   │ K   │ L   │ :   │ "*¨ ┃            ┃
┃ ⇬       ┃   { │   ( │   ) │   } │   = │   \\ │   + │   - │   / │ ; " │ '*´ ┃ ⏎          ┃
┣━━━━━━━━━┻━━┱──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┲━━┻━━━━━━━━━━━━┫
┃            ┃ Z   │ X   │ C   │ V   │ B   │ N   │ M   │ <   │ >   │ ?   ┃               ┃
┃ ⇧          ┃   ~ │   [ │   ] │   _ │   # │   | │   ! │ , ; │ . : │ / ? ┃ ⇧             ┃
┣━━━━━━━┳━━━━┻━━┳━━┷━━━━┱┴─────┴─────┴─────┴─────┴─────┴─┲━━━┷━━━┳━┷━━━━━╋━━━━━━━┳━━━━━━━┫
┃       ┃       ┃       ┃                                ┃       ┃       ┃       ┃       ┃
┃ Ctrl  ┃ super ┃ Alt   ┃ ␣                              ┃ AltGr ┃ super ┃ menu  ┃ Ctrl  ┃
┗━━━━━━━┻━━━━━━━┻━━━━━━━┹────────────────────────────────┺━━━━━━━┻━━━━━━━┻━━━━━━━┻━━━━━━━┛
'''
```
"""

TOML_HEADER = """# kalamine keyboard layout descriptor
name        = "qwerty-custom"  # full layout name, displayed in the keyboard settings
name8       = "custom"         # short Windows filename: no spaces, no special chars
locale      = "us"             # locale/language id
variant     = "custom"         # layout variant id
author      = "nobody"         # author name
description = "custom QWERTY layout"
url         = "https://OneDeadKey.github.com/kalamine"
version     = "0.0.1"
geometry    = """

TOML_FOOTER = """
[spacebar]
1dk         = "'"  # apostrophe
1dk_shift   = "'"  # apostrophe"""


def dead_key_table() -> str:
    out = f"\n    id  XKB name          base -> accented chars\n    {SEPARATOR[4:]}"
    for item in load_data("dead_keys"):
        if (item["char"]) != "**":
            out += f"\n    {item['char']}  {item['name']:<17} {item['base']}"
            out += f"\n                       -> {item['alt']}"
    return out


def core_guide() -> List[str]:
    sections: List[str] = []

    for title, content in load_data("user_guide").items():
        out = f"\n{title.replace('_', ' ')}\n{SEPARATOR}"

        if isinstance(content, dict):
            for subtitle, subcontent in content.items():
                out += f"\n\n### {subtitle.replace('_', ' ')}"
                out += f"\n\n{subcontent}"
                if subtitle == "Standard_Dead_Keys":
                    out += dead_key_table()
        else:
            out += f"\n\n{content}"

        sections.append(out)

    return sections


def user_guide() -> str:
    return MARKDOWN_HEADER + "\n".join(core_guide())


def inline_guide() -> str:
    content: str = ""

    for topic in core_guide():
        content += f"\n\n\n# {SEPARATOR}"
        content += "\n# ".join(topic.rstrip().split("\n"))

    return content.replace(" \n", "\n")
