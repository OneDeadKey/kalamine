"""
macOS: keylayout output
https://developer.apple.com/library/content/technotes/tn2056/
"""

from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from ..layout import KeyboardLayout

from ..key import KEYS, KeyCategory
from ..template import load_tpl, substitute_lines
from ..utils import Layer, hex_ord


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
        prev_category: Optional[KeyCategory] = None
        for key in KEYS.values():
            # TODO: remove test and use only next?
            if key.id in ["ae13", "ab11"]:  # ABNT / JIS keys
                continue  # these two keys are not supported yet
            if key.macos is None:
                continue

            if key.category is not prev_category:
                if output:
                    output.append("")
                output.append("<!-- " + key.category.description + " -->")
                prev_category = key.category

            symbol = "&#x0010;"
            final_key = True

            if key.id in layer:
                value = layer[key.id]
                if value in layout.dead_keys:
                    symbol = f"dead_{layout.custom_dead_keys[value].name}"
                    final_key = False
                else:
                    symbol = _xml_proof(value.upper() if caps else value)
                    final_key = not has_dead_keys(value.upper())

            char = f"code=\"{key.macos}\"".ljust(10)
            if final_key:
                action = f'output="{symbol}"'
            elif symbol.startswith("dead_"):
                action = f'action="{_xml_proof_id(symbol)}"'
            else:
                action = f'action="{key.id}_{_xml_proof_id(symbol)}"'
            output.append(f"<key {char} {action} />")

        ret_str.append(output)
    return ret_str


def macos_actions(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key actions."""

    ret_actions = []

    def when(state: str, action: str) -> str:
        state_attr = f'state="{state}"'.ljust(18)
        if action in layout.dead_keys:
            action_attr = f'next="{layout.custom_dead_keys[action].name}"'
        elif action.startswith("dead_"):
            action_attr = f'next="{action[5:]}"'
        else:
            action_attr = f'output="{_xml_proof(action)}"'
        return f"  <when {state_attr} {action_attr} />"

    def append_actions(id: str, symbol: str, actions: List[Tuple[str, str]]) -> None:
        ret_actions.append(f'<action id="{id}_{_xml_proof_id(symbol)}">')
        ret_actions.append(when("none", symbol))
        for state, out in actions:
            ret_actions.append(when(state, out))
        ret_actions.append("</action>")

    # dead key definitions
    for dk in layout.dead_keys:
        name = layout.custom_dead_keys[dk].name
        term = layout.dead_keys[dk][dk]
        ret_actions.append(f'<action id="dead_{name}">')
        ret_actions.append(f'  <when state="none" next="{name}" />')
        if name == "1dk" and term in layout.dead_keys:
            nested_dk = layout.custom_dead_keys[term].name
            ret_actions.append(f'  <when state="1dk" next="{nested_dk}" />')
        ret_actions.append("</action>")
        continue

    # normal key actions
    prev_category: Optional[KeyCategory] = None
    for key in KEYS.values():
        if key.macos is None:
            continue

        if key.category is not prev_category:
            ret_actions.append("")
            ret_actions.append(f"<!-- {key.category.description} -->")
            prev_category = key.category

        for i in [Layer.BASE, Layer.SHIFT, Layer.ALTGR, Layer.ALTGR_SHIFT]:
            if key.id == "spce" or key.id not in layout.layers[i]:
                continue

            value = layout.layers[i][key.id]
            if i and value == layout.layers[Layer.BASE][key.id]:
                continue
            if value in layout.dead_keys:
                continue

            actions: List[Tuple[str, str]] = []
            for k in layout.custom_dead_keys:
                if k in layout.dead_keys:
                    if value in layout.dead_keys[k]:
                        actions.append((layout.custom_dead_keys[k].name, layout.dead_keys[k][value]))
            if actions:
                append_actions(key.id, _xml_proof(value), actions)

    # spacebar actions
    actions = []
    for k in layout.custom_dead_keys:
        if k in layout.dead_keys:
            actions.append((layout.custom_dead_keys[k].name, layout.dead_keys[k][" "]))
    append_actions("spce", "&#x0020;", actions)  # space
    append_actions("spce", "&#x00a0;", actions)  # no-break space
    append_actions("spce", "&#x202f;", actions)  # fine no-break space

    return ret_actions


def macos_terminators(layout: "KeyboardLayout") -> List[str]:
    """macOS layout, dead key terminators."""

    ret_terminators = []
    for key in layout.custom_dead_keys:
        if key not in layout.dead_keys:
            continue
        dk = layout.dead_keys[key]
        name = layout.custom_dead_keys[key].name
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
