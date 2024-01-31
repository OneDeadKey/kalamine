from pathlib import Path

from lxml import etree


def check_keylayout(filename: str):
    path = Path(__file__).parent.parent / "dist" / (filename + ".keylayout")
    tree = etree.parse(path, etree.XMLParser(recover=True))
    dead_keys = []

    # check all keymaps/layers: base, shift, caps, option, option+shift
    for keymap_index in range(5):
        keymap_query = f'//keyMap[@index="{keymap_index}"]'
        keymap = tree.xpath(keymap_query)
        assert len(keymap) == 1, f"{keymap_query} should be unique"

        # check all key codes for this keymap / layer
        # (the key codes below are not used, I don't know why)
        excluded_keys = [
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            68,
            73,
            74,
            90,
            93,
            94,
            95,
        ]
        for key_index in range(126):
            if key_index in excluded_keys:
                continue

            # ensure the key is defined and unique
            key_query = f'{keymap_query}/key[@code="{key_index}"]'
            key = tree.xpath(key_query)
            assert len(key) == 1, f"{key_query} should be unique"

            # ensure the key has either a direct output or a valid action
            action_id = key[0].get("action")
            if action_id:
                if action_id.startswith("dead_"):
                    dead_keys.append(action_id[5:])
                action_query = f'//actions/action[@id="{action_id}"]'
                action = tree.xpath(action_query)
                assert len(action) == 1, f"{action_query} should be unique"
            else:
                assert (
                    len(key[0].get("output")) <= 1
                ), f"{key_query} should have a one-char output"

    # check all dead keys
    # TODO: ensure there are no unused actions or terminators
    for dk in dead_keys:
        when_query = f'//actions/action[@id="dead_{dk}"]/when'
        when = tree.xpath(when_query)
        assert len(when) == 1, f"{when_query} should be unique"
        assert when[0].get("state") == "none"
        assert when[0].get("next") == dk
        terminator_query = f'//terminators/when[@state="{dk}"]'
        terminator = tree.xpath(terminator_query)
        assert len(terminator) == 1, f"{terminator_query} should be unique"
        assert len(terminator[0].get("output")) == 1


def test_keylayouts():
    check_keylayout("q-ansi")
    check_keylayout("q-intl")
    check_keylayout("q-prog")
