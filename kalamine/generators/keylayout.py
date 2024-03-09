"""
macOS: keylayout output
https://developer.apple.com/library/content/technotes/tn2056/
"""

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..template import load_tpl, substitute_lines
from ..utils import DK_INDEX, LAYER_KEYS, SCAN_CODES, Layer, hex_ord


def _xml_proof(char: str) -> str:
    if char not in '<&"\u0020\u00a0\u202f>':
        return char
    return f"&#x{hex_ord(char)};"


def _xml_proof_id(symbol: str) -> str:
    return symbol[2:-1] if symbol.startswith("&#x") else symbol


def macos_keymap(layout: "KeyboardLayout") -> List[List[str]]:
    """macOS layout, main part."""

    if layout.qwerty_shortcuts:
        print("WARN: keeping qwerty shortcuts is not yet supported for MacOS")

    ret_str = []
    for index in range(5):
        layer = layout.layers[
            [Layer.BASE, Layer.SHIFT, Layer.BASE, Layer.ALTGR, Layer.ALTGR_SHIFT][index]
        ]
        caps = index == 2

        def has_dead_keys(letter: str) -> bool:
            if letter in "\u0020\u00a0\u202f":  # space
                return True
            for k in layout.dead_keys:
                if letter in layout.dead_keys[k]:
                    return True
            return False

        output: List[str] = []
        for key_name in LAYER_KEYS:
            if key_name in ["ae13", "ab11"]:  # ABNT / JIS keys
                continue  # these two keys are not supported yet

            if key_name.startswith("-"):
                if output:
                    output.append("")
                output.append("<!--" + key_name[1:] + " -->")
                continue

            symbol = "&#x0010;"
            final_key = True

            if key_name in layer:
                key = layer[key_name]
                if key in layout.dead_keys:
                    symbol = f"dead_{DK_INDEX[key].name}"
                    final_key = False
                else:
                    symbol = _xml_proof(key.upper() if caps else key)
                    final_key = not has_dead_keys(key.upper())

            char = f"code=\"{SCAN_CODES['osx'][key_name]}\"".ljust(10)
            if final_key:
                action = f'output="{symbol}"'
            elif symbol.startswith("dead_"):
                action = f'action="{_xml_proof_id(symbol)}"'
            else:
                action = f'action="{key_name}_{_xml_proof_id(symbol)}"'
            output.append(f"<key {char} {action} />")

        ret_str.append(output)
    return ret_str


def macos_actions(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key actions."""

    ret_actions = []

    def when(state: str, action: str) -> str:
        state_attr = f'state="{state}"'.ljust(18)
        if action in layout.dead_keys:
            action_attr = f'next="{DK_INDEX[action].name}"'
        elif action.startswith("dead_"):
            action_attr = f'next="{action[5:]}"'
        else:
            action_attr = f'output="{_xml_proof(action)}"'
        return f"  <when {state_attr} {action_attr} />"

    def append_actions(key: str, symbol: str, actions: List[Tuple[str, str]]) -> None:
        ret_actions.append(f'<action id="{key}_{_xml_proof_id(symbol)}">')
        ret_actions.append(when("none", symbol))
        for state, out in actions:
            ret_actions.append(when(state, out))
        ret_actions.append("</action>")

    # dead key definitions
    for key in layout.dead_keys:
        name = DK_INDEX[key].name
        term = layout.dead_keys[key][key]
        ret_actions.append(f'<action id="dead_{name}">')
        ret_actions.append(f'  <when state="none" next="{name}" />')
        if name == "1dk" and term in layout.dead_keys:
            nested_dk = DK_INDEX[term].name
            ret_actions.append(f'  <when state="1dk" next="{nested_dk}" />')
        ret_actions.append("</action>")
        continue

    # normal key actions
    for key_name in LAYER_KEYS:
        if key_name.startswith("-"):
            ret_actions.append("")
            ret_actions.append(f"<!--{key_name[1:]} -->")
            continue

        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            if key_name == "spce" or key_name not in layout.layers[i]:
                continue

            key = layout.layers[i][key_name]
            if i and key == layout.layers[Layer.BASE][key_name]:
                continue
            if key in layout.dead_keys:
                continue

            actions: List[Tuple[str, str]] = []
            for k in DK_INDEX:
                if k in layout.dead_keys:
                    if key in layout.dead_keys[k]:
                        actions.append((DK_INDEX[k].name, layout.dead_keys[k][key]))
            if actions:
                append_actions(key_name, _xml_proof(key), actions)

    # spacebar actions
    actions = []
    for k in DK_INDEX:
        if k in layout.dead_keys:
            actions.append((DK_INDEX[k].name, layout.dead_keys[k][" "]))
    append_actions("spce", "&#x0020;", actions)  # space
    append_actions("spce", "&#x00a0;", actions)  # no-break space
    append_actions("spce", "&#x202f;", actions)  # fine no-break space

    return ret_actions


def macos_terminators(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key terminators."""

    ret_terminators = []
    for key in DK_INDEX:
        if key not in layout.dead_keys:
            continue
        dk = layout.dead_keys[key]
        name = DK_INDEX[key].name
        term = dk[key]
        if name == "1dk" and term in layout.dead_keys:
            term = dk[" "]
        state = f'state="{name}"'.ljust(18)
        output = f'output="{_xml_proof(term)}"'
        ret_terminators.append(f"<when {state} {output} />")
    return ret_terminators


def keylayout(layout: "KeyboardLayout") -> str:
    """macOS driver"""

    out = load_tpl(layout, ".keylayout")
    for i, layer in enumerate(macos_keymap(layout)):
        out = substitute_lines(out, "LAYER_" + str(i), layer)
    out = substitute_lines(out, "ACTIONS", macos_actions(layout))
    out = substitute_lines(out, "TERMINATORS", macos_terminators(layout))
    return out
