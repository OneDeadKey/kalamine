from textwrap import dedent

from kalamine import KeyboardLayout
from kalamine.generators.keylayout import macos_actions, macos_keymap, macos_terminators

from .util import get_layout_dict


def load_layout(filename: str) -> KeyboardLayout:
    return KeyboardLayout(get_layout_dict(filename))


def split(multiline_str: str):
    return dedent(multiline_str).lstrip().rstrip().splitlines()


EMPTY_KEYMAP = split(
    """
    <!-- Digits -->
    <key code="18"  output="&#x0010;" />
    <key code="19"  output="&#x0010;" />
    <key code="20"  output="&#x0010;" />
    <key code="21"  output="&#x0010;" />
    <key code="23"  output="&#x0010;" />
    <key code="22"  output="&#x0010;" />
    <key code="26"  output="&#x0010;" />
    <key code="28"  output="&#x0010;" />
    <key code="25"  output="&#x0010;" />
    <key code="29"  output="&#x0010;" />

    <!-- Letters, first row -->
    <key code="12"  output="&#x0010;" />
    <key code="13"  output="&#x0010;" />
    <key code="14"  output="&#x0010;" />
    <key code="15"  output="&#x0010;" />
    <key code="17"  output="&#x0010;" />
    <key code="16"  output="&#x0010;" />
    <key code="32"  output="&#x0010;" />
    <key code="34"  output="&#x0010;" />
    <key code="31"  output="&#x0010;" />
    <key code="35"  output="&#x0010;" />

    <!-- Letters, second row -->
    <key code="0"   output="&#x0010;" />
    <key code="1"   output="&#x0010;" />
    <key code="2"   output="&#x0010;" />
    <key code="3"   output="&#x0010;" />
    <key code="5"   output="&#x0010;" />
    <key code="4"   output="&#x0010;" />
    <key code="38"  output="&#x0010;" />
    <key code="40"  output="&#x0010;" />
    <key code="37"  output="&#x0010;" />
    <key code="41"  output="&#x0010;" />

    <!-- Letters, third row -->
    <key code="6"   output="&#x0010;" />
    <key code="7"   output="&#x0010;" />
    <key code="8"   output="&#x0010;" />
    <key code="9"   output="&#x0010;" />
    <key code="11"  output="&#x0010;" />
    <key code="45"  output="&#x0010;" />
    <key code="46"  output="&#x0010;" />
    <key code="43"  output="&#x0010;" />
    <key code="47"  output="&#x0010;" />
    <key code="44"  output="&#x0010;" />

    <!-- Pinky keys -->
    <key code="27"  output="&#x0010;" />
    <key code="24"  output="&#x0010;" />
    <key code="33"  output="&#x0010;" />
    <key code="30"  output="&#x0010;" />
    <key code="39"  output="&#x0010;" />
    <key code="50"  output="&#x0010;" />
    <key code="42"  output="&#x0010;" />
    <key code="10"  output="&#x0010;" />

    <!-- Space bar -->
    <key code="49"  output="&#x0010;" />
    """
)


def test_ansi():
    layout = load_layout("ansi")

    keymap = macos_keymap(layout)

    assert len(keymap[0]) == 60
    assert keymap[0] == split(
        """
        <!-- Digits -->
        <key code="18"  output="1" />
        <key code="19"  output="2" />
        <key code="20"  output="3" />
        <key code="21"  output="4" />
        <key code="23"  output="5" />
        <key code="22"  output="6" />
        <key code="26"  output="7" />
        <key code="28"  output="8" />
        <key code="25"  output="9" />
        <key code="29"  output="0" />

        <!-- Letters, first row -->
        <key code="12"  output="q" />
        <key code="13"  output="w" />
        <key code="14"  output="e" />
        <key code="15"  output="r" />
        <key code="17"  output="t" />
        <key code="16"  output="y" />
        <key code="32"  output="u" />
        <key code="34"  output="i" />
        <key code="31"  output="o" />
        <key code="35"  output="p" />

        <!-- Letters, second row -->
        <key code="0"   output="a" />
        <key code="1"   output="s" />
        <key code="2"   output="d" />
        <key code="3"   output="f" />
        <key code="5"   output="g" />
        <key code="4"   output="h" />
        <key code="38"  output="j" />
        <key code="40"  output="k" />
        <key code="37"  output="l" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   output="z" />
        <key code="7"   output="x" />
        <key code="8"   output="c" />
        <key code="9"   output="v" />
        <key code="11"  output="b" />
        <key code="45"  output="n" />
        <key code="46"  output="m" />
        <key code="43"  output="," />
        <key code="47"  output="." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  output="-" />
        <key code="24"  output="=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  output="'" />
        <key code="50"  output="`" />
        <key code="42"  output="\\" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[1]) == 60
    assert keymap[1] == split(
        """
        <!-- Digits -->
        <key code="18"  output="!" />
        <key code="19"  output="@" />
        <key code="20"  output="#" />
        <key code="21"  output="$" />
        <key code="23"  output="%" />
        <key code="22"  output="^" />
        <key code="26"  output="&#x0026;" />
        <key code="28"  output="*" />
        <key code="25"  output="(" />
        <key code="29"  output=")" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  output="W" />
        <key code="14"  output="E" />
        <key code="15"  output="R" />
        <key code="17"  output="T" />
        <key code="16"  output="Y" />
        <key code="32"  output="U" />
        <key code="34"  output="I" />
        <key code="31"  output="O" />
        <key code="35"  output="P" />

        <!-- Letters, second row -->
        <key code="0"   output="A" />
        <key code="1"   output="S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   output="G" />
        <key code="4"   output="H" />
        <key code="38"  output="J" />
        <key code="40"  output="K" />
        <key code="37"  output="L" />
        <key code="41"  output=":" />

        <!-- Letters, third row -->
        <key code="6"   output="Z" />
        <key code="7"   output="X" />
        <key code="8"   output="C" />
        <key code="9"   output="V" />
        <key code="11"  output="B" />
        <key code="45"  output="N" />
        <key code="46"  output="M" />
        <key code="43"  output="&#x003c;" />
        <key code="47"  output="&#x003e;" />
        <key code="44"  output="?" />

        <!-- Pinky keys -->
        <key code="27"  output="_" />
        <key code="24"  output="+" />
        <key code="33"  output="{" />
        <key code="30"  output="}" />
        <key code="39"  output="&#x0022;" />
        <key code="50"  output="~" />
        <key code="42"  output="|" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[2]) == 60
    assert keymap[2] == split(
        """
        <!-- Digits -->
        <key code="18"  output="1" />
        <key code="19"  output="2" />
        <key code="20"  output="3" />
        <key code="21"  output="4" />
        <key code="23"  output="5" />
        <key code="22"  output="6" />
        <key code="26"  output="7" />
        <key code="28"  output="8" />
        <key code="25"  output="9" />
        <key code="29"  output="0" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  output="W" />
        <key code="14"  output="E" />
        <key code="15"  output="R" />
        <key code="17"  output="T" />
        <key code="16"  output="Y" />
        <key code="32"  output="U" />
        <key code="34"  output="I" />
        <key code="31"  output="O" />
        <key code="35"  output="P" />

        <!-- Letters, second row -->
        <key code="0"   output="A" />
        <key code="1"   output="S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   output="G" />
        <key code="4"   output="H" />
        <key code="38"  output="J" />
        <key code="40"  output="K" />
        <key code="37"  output="L" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   output="Z" />
        <key code="7"   output="X" />
        <key code="8"   output="C" />
        <key code="9"   output="V" />
        <key code="11"  output="B" />
        <key code="45"  output="N" />
        <key code="46"  output="M" />
        <key code="43"  output="," />
        <key code="47"  output="." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  output="-" />
        <key code="24"  output="=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  output="'" />
        <key code="50"  output="`" />
        <key code="42"  output="\\" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[3]) == 60
    assert keymap[3] == EMPTY_KEYMAP

    assert len(keymap[4]) == 60
    assert keymap[4] == EMPTY_KEYMAP

    actions = macos_actions(layout)
    assert actions[1:] == split(
        """
        <!-- Digits -->

        <!-- Letters, first row -->

        <!-- Letters, second row -->

        <!-- Letters, third row -->

        <!-- Pinky keys -->

        <!-- Space bar -->
        <action id="spce_x0020">
          <when state="none"       output="&#x0020;" />
        </action>
        <action id="spce_x00a0">
          <when state="none"       output="&#x00a0;" />
        </action>
        <action id="spce_x202f">
          <when state="none"       output="&#x202f;" />
        </action>
        """
    )

    terminators = macos_terminators(layout)
    assert len(terminators) == 0


def test_intl():
    layout = load_layout("intl")

    keymap = macos_keymap(layout)

    assert len(keymap[0]) == 60
    assert keymap[0] == split(
        """
        <!-- Digits -->
        <key code="18"  action="ae01_1" />
        <key code="19"  action="ae02_2" />
        <key code="20"  action="ae03_3" />
        <key code="21"  action="ae04_4" />
        <key code="23"  action="ae05_5" />
        <key code="22"  action="ae06_6" />
        <key code="26"  action="ae07_7" />
        <key code="28"  action="ae08_8" />
        <key code="25"  action="ae09_9" />
        <key code="29"  action="ae10_0" />

        <!-- Letters, first row -->
        <key code="12"  output="q" />
        <key code="13"  action="ad02_w" />
        <key code="14"  action="ad03_e" />
        <key code="15"  output="r" />
        <key code="17"  output="t" />
        <key code="16"  action="ad06_y" />
        <key code="32"  action="ad07_u" />
        <key code="34"  action="ad08_i" />
        <key code="31"  action="ad09_o" />
        <key code="35"  output="p" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_a" />
        <key code="1"   action="ac02_s" />
        <key code="2"   output="d" />
        <key code="3"   output="f" />
        <key code="5"   action="ac05_g" />
        <key code="4"   action="ac06_h" />
        <key code="38"  action="ac07_j" />
        <key code="40"  output="k" />
        <key code="37"  output="l" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_z" />
        <key code="7"   action="ab02_x" />
        <key code="8"   action="ab03_c" />
        <key code="9"   action="ab04_v" />
        <key code="11"  output="b" />
        <key code="45"  action="ab06_n" />
        <key code="46"  output="m" />
        <key code="43"  output="," />
        <key code="47"  action="ab09_." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  action="ae11_-" />
        <key code="24"  action="ae12_=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  action="dead_1dk" />
        <key code="50"  action="dead_grave" />
        <key code="42"  output="\\" />
        <key code="10"  output="\\" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[1]) == 60
    assert keymap[1] == split(
        """
        <!-- Digits -->
        <key code="18"  output="!" />
        <key code="19"  output="@" />
        <key code="20"  output="#" />
        <key code="21"  output="$" />
        <key code="23"  output="%" />
        <key code="22"  action="dead_circumflex" />
        <key code="26"  output="&#x0026;" />
        <key code="28"  output="*" />
        <key code="25"  action="ae09_(" />
        <key code="29"  action="ae10_)" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  action="ad02_W" />
        <key code="14"  action="ad03_E" />
        <key code="15"  output="R" />
        <key code="17"  output="T" />
        <key code="16"  action="ad06_Y" />
        <key code="32"  action="ad07_U" />
        <key code="34"  action="ad08_I" />
        <key code="31"  action="ad09_O" />
        <key code="35"  output="P" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_A" />
        <key code="1"   action="ac02_S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   action="ac05_G" />
        <key code="4"   action="ac06_H" />
        <key code="38"  action="ac07_J" />
        <key code="40"  output="K" />
        <key code="37"  output="L" />
        <key code="41"  output=":" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_Z" />
        <key code="7"   action="ab02_X" />
        <key code="8"   action="ab03_C" />
        <key code="9"   action="ab04_V" />
        <key code="11"  output="B" />
        <key code="45"  action="ab06_N" />
        <key code="46"  output="M" />
        <key code="43"  action="ab08_x003c" />
        <key code="47"  action="ab09_x003e" />
        <key code="44"  output="?" />

        <!-- Pinky keys -->
        <key code="27"  output="_" />
        <key code="24"  action="ae12_+" />
        <key code="33"  output="{" />
        <key code="30"  output="}" />
        <key code="39"  action="dead_diaeresis" />
        <key code="50"  action="dead_tilde" />
        <key code="42"  output="|" />
        <key code="10"  output="|" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[2]) == 60
    assert keymap[2] == split(
        """
        <!-- Digits -->
        <key code="18"  action="ae01_1" />
        <key code="19"  action="ae02_2" />
        <key code="20"  action="ae03_3" />
        <key code="21"  action="ae04_4" />
        <key code="23"  action="ae05_5" />
        <key code="22"  action="ae06_6" />
        <key code="26"  action="ae07_7" />
        <key code="28"  action="ae08_8" />
        <key code="25"  action="ae09_9" />
        <key code="29"  action="ae10_0" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  action="ad02_W" />
        <key code="14"  action="ad03_E" />
        <key code="15"  output="R" />
        <key code="17"  output="T" />
        <key code="16"  action="ad06_Y" />
        <key code="32"  action="ad07_U" />
        <key code="34"  action="ad08_I" />
        <key code="31"  action="ad09_O" />
        <key code="35"  output="P" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_A" />
        <key code="1"   action="ac02_S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   action="ac05_G" />
        <key code="4"   action="ac06_H" />
        <key code="38"  action="ac07_J" />
        <key code="40"  output="K" />
        <key code="37"  output="L" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_Z" />
        <key code="7"   action="ab02_X" />
        <key code="8"   action="ab03_C" />
        <key code="9"   action="ab04_V" />
        <key code="11"  output="B" />
        <key code="45"  action="ab06_N" />
        <key code="46"  output="M" />
        <key code="43"  output="," />
        <key code="47"  action="ab09_." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  action="ae11_-" />
        <key code="24"  action="ae12_=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  action="dead_1dk" />
        <key code="50"  action="dead_grave" />
        <key code="42"  output="\\" />
        <key code="10"  output="\\" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[3]) == 60
    assert keymap[3] == EMPTY_KEYMAP

    assert len(keymap[4]) == 60
    assert keymap[4] == EMPTY_KEYMAP

    actions = macos_actions(layout)
    assert actions == split(
        """
        <action id="dead_1dk">
          <when state="none" next="1dk" />
        </action>
        <action id="dead_grave">
          <when state="none" next="grave" />
        </action>
        <action id="dead_circumflex">
          <when state="none" next="circumflex" />
        </action>
        <action id="dead_tilde">
          <when state="none" next="tilde" />
        </action>
        <action id="dead_diaeresis">
          <when state="none" next="diaeresis" />
        </action>

        <!-- Digits -->
        <action id="ae01_1">
          <when state="none"       output="1" />
          <when state="circumflex" output="¹" />
        </action>
        <action id="ae02_2">
          <when state="none"       output="2" />
          <when state="circumflex" output="²" />
        </action>
        <action id="ae03_3">
          <when state="none"       output="3" />
          <when state="circumflex" output="³" />
        </action>
        <action id="ae04_4">
          <when state="none"       output="4" />
          <when state="circumflex" output="⁴" />
        </action>
        <action id="ae05_5">
          <when state="none"       output="5" />
          <when state="circumflex" output="⁵" />
        </action>
        <action id="ae06_6">
          <when state="none"       output="6" />
          <when state="circumflex" output="⁶" />
        </action>
        <action id="ae07_7">
          <when state="none"       output="7" />
          <when state="circumflex" output="⁷" />
        </action>
        <action id="ae08_8">
          <when state="none"       output="8" />
          <when state="circumflex" output="⁸" />
        </action>
        <action id="ae09_9">
          <when state="none"       output="9" />
          <when state="circumflex" output="⁹" />
        </action>
        <action id="ae09_(">
          <when state="none"       output="(" />
          <when state="circumflex" output="⁽" />
        </action>
        <action id="ae10_0">
          <when state="none"       output="0" />
          <when state="circumflex" output="⁰" />
        </action>
        <action id="ae10_)">
          <when state="none"       output=")" />
          <when state="circumflex" output="⁾" />
        </action>

        <!-- Letters, first row -->
        <action id="ad02_w">
          <when state="none"       output="w" />
          <when state="grave"      output="ẁ" />
          <when state="circumflex" output="ŵ" />
          <when state="diaeresis"  output="ẅ" />
        </action>
        <action id="ad02_W">
          <when state="none"       output="W" />
          <when state="grave"      output="Ẁ" />
          <when state="circumflex" output="Ŵ" />
          <when state="diaeresis"  output="Ẅ" />
        </action>
        <action id="ad03_e">
          <when state="none"       output="e" />
          <when state="1dk"        output="é" />
          <when state="grave"      output="è" />
          <when state="circumflex" output="ê" />
          <when state="tilde"      output="ẽ" />
          <when state="diaeresis"  output="ë" />
        </action>
        <action id="ad03_E">
          <when state="none"       output="E" />
          <when state="1dk"        output="É" />
          <when state="grave"      output="È" />
          <when state="circumflex" output="Ê" />
          <when state="tilde"      output="Ẽ" />
          <when state="diaeresis"  output="Ë" />
        </action>
        <action id="ad05_t">
          <when state="none"       output="t" />
          <when state="diaeresis"  output="ẗ" />
        </action>
        <action id="ad06_y">
          <when state="none"       output="y" />
          <when state="grave"      output="ỳ" />
          <when state="circumflex" output="ŷ" />
          <when state="tilde"      output="ỹ" />
          <when state="diaeresis"  output="ÿ" />
        </action>
        <action id="ad06_Y">
          <when state="none"       output="Y" />
          <when state="grave"      output="Ỳ" />
          <when state="circumflex" output="Ŷ" />
          <when state="tilde"      output="Ỹ" />
          <when state="diaeresis"  output="Ÿ" />
        </action>
        <action id="ad07_u">
          <when state="none"       output="u" />
          <when state="1dk"        output="ú" />
          <when state="grave"      output="ù" />
          <when state="circumflex" output="û" />
          <when state="tilde"      output="ũ" />
          <when state="diaeresis"  output="ü" />
        </action>
        <action id="ad07_U">
          <when state="none"       output="U" />
          <when state="1dk"        output="Ú" />
          <when state="grave"      output="Ù" />
          <when state="circumflex" output="Û" />
          <when state="tilde"      output="Ũ" />
          <when state="diaeresis"  output="Ü" />
        </action>
        <action id="ad08_i">
          <when state="none"       output="i" />
          <when state="1dk"        output="í" />
          <when state="grave"      output="ì" />
          <when state="circumflex" output="î" />
          <when state="tilde"      output="ĩ" />
          <when state="diaeresis"  output="ï" />
        </action>
        <action id="ad08_I">
          <when state="none"       output="I" />
          <when state="1dk"        output="Í" />
          <when state="grave"      output="Ì" />
          <when state="circumflex" output="Î" />
          <when state="tilde"      output="Ĩ" />
          <when state="diaeresis"  output="Ï" />
        </action>
        <action id="ad09_o">
          <when state="none"       output="o" />
          <when state="1dk"        output="ó" />
          <when state="grave"      output="ò" />
          <when state="circumflex" output="ô" />
          <when state="tilde"      output="õ" />
          <when state="diaeresis"  output="ö" />
        </action>
        <action id="ad09_O">
          <when state="none"       output="O" />
          <when state="1dk"        output="Ó" />
          <when state="grave"      output="Ò" />
          <when state="circumflex" output="Ô" />
          <when state="tilde"      output="Õ" />
          <when state="diaeresis"  output="Ö" />
        </action>

        <!-- Letters, second row -->
        <action id="ac01_a">
          <when state="none"       output="a" />
          <when state="1dk"        output="á" />
          <when state="grave"      output="à" />
          <when state="circumflex" output="â" />
          <when state="tilde"      output="ã" />
          <when state="diaeresis"  output="ä" />
        </action>
        <action id="ac01_A">
          <when state="none"       output="A" />
          <when state="1dk"        output="Á" />
          <when state="grave"      output="À" />
          <when state="circumflex" output="Â" />
          <when state="tilde"      output="Ã" />
          <when state="diaeresis"  output="Ä" />
        </action>
        <action id="ac02_s">
          <when state="none"       output="s" />
          <when state="circumflex" output="ŝ" />
        </action>
        <action id="ac02_S">
          <when state="none"       output="S" />
          <when state="circumflex" output="Ŝ" />
        </action>
        <action id="ac05_g">
          <when state="none"       output="g" />
          <when state="circumflex" output="ĝ" />
        </action>
        <action id="ac05_G">
          <when state="none"       output="G" />
          <when state="circumflex" output="Ĝ" />
        </action>
        <action id="ac06_h">
          <when state="none"       output="h" />
          <when state="circumflex" output="ĥ" />
          <when state="diaeresis"  output="ḧ" />
        </action>
        <action id="ac06_H">
          <when state="none"       output="H" />
          <when state="circumflex" output="Ĥ" />
          <when state="diaeresis"  output="Ḧ" />
        </action>
        <action id="ac07_j">
          <when state="none"       output="j" />
          <when state="circumflex" output="ĵ" />
        </action>
        <action id="ac07_J">
          <when state="none"       output="J" />
          <when state="circumflex" output="Ĵ" />
        </action>

        <!-- Letters, third row -->
        <action id="ab01_z">
          <when state="none"       output="z" />
          <when state="circumflex" output="ẑ" />
        </action>
        <action id="ab01_Z">
          <when state="none"       output="Z" />
          <when state="circumflex" output="Ẑ" />
        </action>
        <action id="ab02_x">
          <when state="none"       output="x" />
          <when state="diaeresis"  output="ẍ" />
        </action>
        <action id="ab02_X">
          <when state="none"       output="X" />
          <when state="diaeresis"  output="Ẍ" />
        </action>
        <action id="ab03_c">
          <when state="none"       output="c" />
          <when state="1dk"        output="ç" />
          <when state="circumflex" output="ĉ" />
        </action>
        <action id="ab03_C">
          <when state="none"       output="C" />
          <when state="1dk"        output="Ç" />
          <when state="circumflex" output="Ĉ" />
        </action>
        <action id="ab04_v">
          <when state="none"       output="v" />
          <when state="tilde"      output="ṽ" />
        </action>
        <action id="ab04_V">
          <when state="none"       output="V" />
          <when state="tilde"      output="Ṽ" />
        </action>
        <action id="ab06_n">
          <when state="none"       output="n" />
          <when state="grave"      output="ǹ" />
          <when state="tilde"      output="ñ" />
        </action>
        <action id="ab06_N">
          <when state="none"       output="N" />
          <when state="grave"      output="Ǹ" />
          <when state="tilde"      output="Ñ" />
        </action>
        <action id="ab08_x003c">
          <when state="none"       output="&#x003c;" />
          <when state="tilde"      output="≲" />
        </action>
        <action id="ab09_.">
          <when state="none"       output="." />
          <when state="1dk"        output="…" />
        </action>
        <action id="ab09_x003e">
          <when state="none"       output="&#x003e;" />
          <when state="tilde"      output="≳" />
        </action>

        <!-- Pinky keys -->
        <action id="ae11_-">
          <when state="none"       output="-" />
          <when state="circumflex" output="⁻" />
        </action>
        <action id="ae12_=">
          <when state="none"       output="=" />
          <when state="circumflex" output="⁼" />
          <when state="tilde"      output="≃" />
        </action>
        <action id="ae12_+">
          <when state="none"       output="+" />
          <when state="circumflex" output="⁺" />
        </action>

        <!-- Space bar -->
        <action id="spce_x0020">
          <when state="none"       output="&#x0020;" />
          <when state="1dk"        output="'" />
          <when state="grave"      output="`" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        <action id="spce_x00a0">
          <when state="none"       output="&#x00a0;" />
          <when state="1dk"        output="'" />
          <when state="grave"      output="`" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        <action id="spce_x202f">
          <when state="none"       output="&#x202f;" />
          <when state="1dk"        output="'" />
          <when state="grave"      output="`" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        """
    )

    terminators = macos_terminators(layout)
    assert len(terminators) == 5
    assert terminators == split(
        """
        <when state="1dk"        output="\'" />
        <when state="grave"      output="`" />
        <when state="circumflex" output="^" />
        <when state="tilde"      output="~" />
        <when state="diaeresis"  output="¨" />
        """
    )


def test_prog():
    layout = load_layout("prog")

    keymap = macos_keymap(layout)

    assert len(keymap[0]) == 60
    assert keymap[0] == split(
        """
        <!-- Digits -->
        <key code="18"  action="ae01_1" />
        <key code="19"  action="ae02_2" />
        <key code="20"  action="ae03_3" />
        <key code="21"  action="ae04_4" />
        <key code="23"  action="ae05_5" />
        <key code="22"  action="ae06_6" />
        <key code="26"  action="ae07_7" />
        <key code="28"  action="ae08_8" />
        <key code="25"  action="ae09_9" />
        <key code="29"  action="ae10_0" />

        <!-- Letters, first row -->
        <key code="12"  output="q" />
        <key code="13"  action="ad02_w" />
        <key code="14"  action="ad03_e" />
        <key code="15"  action="ad04_r" />
        <key code="17"  output="t" />
        <key code="16"  action="ad06_y" />
        <key code="32"  action="ad07_u" />
        <key code="34"  action="ad08_i" />
        <key code="31"  action="ad09_o" />
        <key code="35"  action="ad10_p" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_a" />
        <key code="1"   action="ac02_s" />
        <key code="2"   output="d" />
        <key code="3"   output="f" />
        <key code="5"   action="ac05_g" />
        <key code="4"   action="ac06_h" />
        <key code="38"  action="ac07_j" />
        <key code="40"  action="ac08_k" />
        <key code="37"  action="ac09_l" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_z" />
        <key code="7"   action="ab02_x" />
        <key code="8"   action="ab03_c" />
        <key code="9"   action="ab04_v" />
        <key code="11"  output="b" />
        <key code="45"  action="ab06_n" />
        <key code="46"  action="ab07_m" />
        <key code="43"  output="," />
        <key code="47"  output="." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  action="ae11_-" />
        <key code="24"  action="ae12_=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  output="'" />
        <key code="50"  output="`" />
        <key code="42"  output="\\" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[1]) == 60
    assert keymap[1] == split(
        """
        <!-- Digits -->
        <key code="18"  output="!" />
        <key code="19"  output="@" />
        <key code="20"  output="#" />
        <key code="21"  output="$" />
        <key code="23"  output="%" />
        <key code="22"  output="^" />
        <key code="26"  output="&#x0026;" />
        <key code="28"  output="*" />
        <key code="25"  action="ae09_(" />
        <key code="29"  action="ae10_)" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  action="ad02_W" />
        <key code="14"  action="ad03_E" />
        <key code="15"  action="ad04_R" />
        <key code="17"  output="T" />
        <key code="16"  action="ad06_Y" />
        <key code="32"  action="ad07_U" />
        <key code="34"  action="ad08_I" />
        <key code="31"  action="ad09_O" />
        <key code="35"  action="ad10_P" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_A" />
        <key code="1"   action="ac02_S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   action="ac05_G" />
        <key code="4"   action="ac06_H" />
        <key code="38"  action="ac07_J" />
        <key code="40"  action="ac08_K" />
        <key code="37"  action="ac09_L" />
        <key code="41"  output=":" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_Z" />
        <key code="7"   action="ab02_X" />
        <key code="8"   action="ab03_C" />
        <key code="9"   action="ab04_V" />
        <key code="11"  output="B" />
        <key code="45"  action="ab06_N" />
        <key code="46"  action="ab07_M" />
        <key code="43"  action="ab08_x003c" />
        <key code="47"  action="ab09_x003e" />
        <key code="44"  output="?" />

        <!-- Pinky keys -->
        <key code="27"  output="_" />
        <key code="24"  action="ae12_+" />
        <key code="33"  output="{" />
        <key code="30"  output="}" />
        <key code="39"  output="&#x0022;" />
        <key code="50"  output="~" />
        <key code="42"  output="|" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[2]) == 60
    assert keymap[2] == split(
        """
        <!-- Digits -->
        <key code="18"  action="ae01_1" />
        <key code="19"  action="ae02_2" />
        <key code="20"  action="ae03_3" />
        <key code="21"  action="ae04_4" />
        <key code="23"  action="ae05_5" />
        <key code="22"  action="ae06_6" />
        <key code="26"  action="ae07_7" />
        <key code="28"  action="ae08_8" />
        <key code="25"  action="ae09_9" />
        <key code="29"  action="ae10_0" />

        <!-- Letters, first row -->
        <key code="12"  output="Q" />
        <key code="13"  action="ad02_W" />
        <key code="14"  action="ad03_E" />
        <key code="15"  action="ad04_R" />
        <key code="17"  output="T" />
        <key code="16"  action="ad06_Y" />
        <key code="32"  action="ad07_U" />
        <key code="34"  action="ad08_I" />
        <key code="31"  action="ad09_O" />
        <key code="35"  action="ad10_P" />

        <!-- Letters, second row -->
        <key code="0"   action="ac01_A" />
        <key code="1"   action="ac02_S" />
        <key code="2"   output="D" />
        <key code="3"   output="F" />
        <key code="5"   action="ac05_G" />
        <key code="4"   action="ac06_H" />
        <key code="38"  action="ac07_J" />
        <key code="40"  action="ac08_K" />
        <key code="37"  action="ac09_L" />
        <key code="41"  output=";" />

        <!-- Letters, third row -->
        <key code="6"   action="ab01_Z" />
        <key code="7"   action="ab02_X" />
        <key code="8"   action="ab03_C" />
        <key code="9"   action="ab04_V" />
        <key code="11"  output="B" />
        <key code="45"  action="ab06_N" />
        <key code="46"  action="ab07_M" />
        <key code="43"  output="," />
        <key code="47"  output="." />
        <key code="44"  output="/" />

        <!-- Pinky keys -->
        <key code="27"  action="ae11_-" />
        <key code="24"  action="ae12_=" />
        <key code="33"  output="[" />
        <key code="30"  output="]" />
        <key code="39"  output="'" />
        <key code="50"  output="`" />
        <key code="42"  output="\\" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[3]) == 60
    assert keymap[3] == split(
        """
        <!-- Digits -->
        <key code="18"  output="!" />
        <key code="19"  action="ae02_(" />
        <key code="20"  action="ae03_)" />
        <key code="21"  output="'" />
        <key code="23"  output="&#x0022;" />
        <key code="22"  action="dead_circumflex" />
        <key code="26"  action="ae07_7" />
        <key code="28"  action="ae08_8" />
        <key code="25"  action="ae09_9" />
        <key code="29"  output="/" />

        <!-- Letters, first row -->
        <key code="12"  action="ad01_=" />
        <key code="13"  action="ad02_x003c" />
        <key code="14"  action="ad03_x003e" />
        <key code="15"  action="ad04_-" />
        <key code="17"  action="ad05_+" />
        <key code="16"  output="&#x0010;" />
        <key code="32"  action="ad07_4" />
        <key code="34"  action="ad08_5" />
        <key code="31"  action="ad09_6" />
        <key code="35"  output="*" />

        <!-- Letters, second row -->
        <key code="0"   output="{" />
        <key code="1"   output="[" />
        <key code="2"   output="]" />
        <key code="3"   output="}" />
        <key code="5"   output="/" />
        <key code="4"   output="&#x0010;" />
        <key code="38"  action="ac07_1" />
        <key code="40"  action="ac08_2" />
        <key code="37"  action="ac09_3" />
        <key code="41"  action="ac10_-" />

        <!-- Letters, third row -->
        <key code="6"   output="~" />
        <key code="7"   output="`" />
        <key code="8"   output="|" />
        <key code="9"   output="_" />
        <key code="11"  output="\\" />
        <key code="45"  output="&#x0010;" />
        <key code="46"  action="ab07_0" />
        <key code="43"  output="," />
        <key code="47"  output="." />
        <key code="44"  action="ab10_+" />

        <!-- Pinky keys -->
        <key code="27"  output="&#x0010;" />
        <key code="24"  output="&#x0010;" />
        <key code="33"  output="&#x0010;" />
        <key code="30"  output="&#x0010;" />
        <key code="39"  action="dead_acute" />
        <key code="50"  action="dead_grave" />
        <key code="42"  output="&#x0010;" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    assert len(keymap[4]) == 60
    assert keymap[4] == split(
        """
        <!-- Digits -->
        <key code="18"  output="&#x0010;" />
        <key code="19"  output="&#x0010;" />
        <key code="20"  output="&#x0010;" />
        <key code="21"  output="&#x0010;" />
        <key code="23"  output="&#x0010;" />
        <key code="22"  output="&#x0010;" />
        <key code="26"  output="&#x0010;" />
        <key code="28"  output="&#x0010;" />
        <key code="25"  output="&#x0010;" />
        <key code="29"  output="&#x0010;" />

        <!-- Letters, first row -->
        <key code="12"  output="&#x0010;" />
        <key code="13"  output="≤" />
        <key code="14"  output="≥" />
        <key code="15"  output="&#x0010;" />
        <key code="17"  output="&#x0010;" />
        <key code="16"  output="&#x0010;" />
        <key code="32"  output="&#x0010;" />
        <key code="34"  output="&#x0010;" />
        <key code="31"  output="&#x0010;" />
        <key code="35"  output="&#x0010;" />

        <!-- Letters, second row -->
        <key code="0"   output="&#x0010;" />
        <key code="1"   output="&#x0010;" />
        <key code="2"   output="&#x0010;" />
        <key code="3"   output="&#x0010;" />
        <key code="5"   output="&#x0010;" />
        <key code="4"   output="&#x0010;" />
        <key code="38"  output="&#x0010;" />
        <key code="40"  output="&#x0010;" />
        <key code="37"  output="&#x0010;" />
        <key code="41"  output="&#x0010;" />

        <!-- Letters, third row -->
        <key code="6"   output="&#x0010;" />
        <key code="7"   output="&#x0010;" />
        <key code="8"   output="¦" />
        <key code="9"   output="&#x0010;" />
        <key code="11"  output="&#x0010;" />
        <key code="45"  output="&#x0010;" />
        <key code="46"  output="&#x0010;" />
        <key code="43"  output="&#x0010;" />
        <key code="47"  output="&#x0010;" />
        <key code="44"  output="&#x0010;" />

        <!-- Pinky keys -->
        <key code="27"  output="&#x0010;" />
        <key code="24"  output="&#x0010;" />
        <key code="33"  output="&#x0010;" />
        <key code="30"  output="&#x0010;" />
        <key code="39"  action="dead_diaeresis" />
        <key code="50"  action="dead_tilde" />
        <key code="42"  output="&#x0010;" />
        <key code="10"  output="&#x0010;" />

        <!-- Space bar -->
        <key code="49"  action="spce_x0020" />
        """
    )

    actions = macos_actions(layout)
    assert actions == split(
        """
        <action id="dead_grave">
          <when state="none" next="grave" />
        </action>
        <action id="dead_acute">
          <when state="none" next="acute" />
        </action>
        <action id="dead_circumflex">
          <when state="none" next="circumflex" />
        </action>
        <action id="dead_tilde">
          <when state="none" next="tilde" />
        </action>
        <action id="dead_diaeresis">
          <when state="none" next="diaeresis" />
        </action>

        <!-- Digits -->
        <action id="ae01_1">
          <when state="none"       output="1" />
          <when state="circumflex" output="¹" />
        </action>
        <action id="ae02_2">
          <when state="none"       output="2" />
          <when state="circumflex" output="²" />
        </action>
        <action id="ae02_(">
          <when state="none"       output="(" />
          <when state="circumflex" output="⁽" />
        </action>
        <action id="ae03_3">
          <when state="none"       output="3" />
          <when state="circumflex" output="³" />
        </action>
        <action id="ae03_)">
          <when state="none"       output=")" />
          <when state="circumflex" output="⁾" />
        </action>
        <action id="ae04_4">
          <when state="none"       output="4" />
          <when state="circumflex" output="⁴" />
        </action>
        <action id="ae05_5">
          <when state="none"       output="5" />
          <when state="circumflex" output="⁵" />
        </action>
        <action id="ae06_6">
          <when state="none"       output="6" />
          <when state="circumflex" output="⁶" />
        </action>
        <action id="ae07_7">
          <when state="none"       output="7" />
          <when state="circumflex" output="⁷" />
        </action>
        <action id="ae08_8">
          <when state="none"       output="8" />
          <when state="circumflex" output="⁸" />
        </action>
        <action id="ae09_9">
          <when state="none"       output="9" />
          <when state="circumflex" output="⁹" />
        </action>
        <action id="ae09_(">
          <when state="none"       output="(" />
          <when state="circumflex" output="⁽" />
        </action>
        <action id="ae10_0">
          <when state="none"       output="0" />
          <when state="circumflex" output="⁰" />
        </action>
        <action id="ae10_)">
          <when state="none"       output=")" />
          <when state="circumflex" output="⁾" />
        </action>

        <!-- Letters, first row -->
        <action id="ad01_=">
          <when state="none"       output="=" />
          <when state="circumflex" output="⁼" />
          <when state="tilde"      output="≃" />
        </action>
        <action id="ad02_w">
          <when state="none"       output="w" />
          <when state="grave"      output="ẁ" />
          <when state="acute"      output="ẃ" />
          <when state="circumflex" output="ŵ" />
          <when state="diaeresis"  output="ẅ" />
        </action>
        <action id="ad02_W">
          <when state="none"       output="W" />
          <when state="grave"      output="Ẁ" />
          <when state="acute"      output="Ẃ" />
          <when state="circumflex" output="Ŵ" />
          <when state="diaeresis"  output="Ẅ" />
        </action>
        <action id="ad02_x003c">
          <when state="none"       output="&#x003c;" />
          <when state="tilde"      output="≲" />
        </action>
        <action id="ad03_e">
          <when state="none"       output="e" />
          <when state="grave"      output="è" />
          <when state="acute"      output="é" />
          <when state="circumflex" output="ê" />
          <when state="tilde"      output="ẽ" />
          <when state="diaeresis"  output="ë" />
        </action>
        <action id="ad03_E">
          <when state="none"       output="E" />
          <when state="grave"      output="È" />
          <when state="acute"      output="É" />
          <when state="circumflex" output="Ê" />
          <when state="tilde"      output="Ẽ" />
          <when state="diaeresis"  output="Ë" />
        </action>
        <action id="ad03_x003e">
          <when state="none"       output="&#x003e;" />
          <when state="tilde"      output="≳" />
        </action>
        <action id="ad04_r">
          <when state="none"       output="r" />
          <when state="acute"      output="ŕ" />
        </action>
        <action id="ad04_R">
          <when state="none"       output="R" />
          <when state="acute"      output="Ŕ" />
        </action>
        <action id="ad04_-">
          <when state="none"       output="-" />
          <when state="circumflex" output="⁻" />
        </action>
        <action id="ad05_t">
          <when state="none"       output="t" />
          <when state="diaeresis"  output="ẗ" />
        </action>
        <action id="ad05_+">
          <when state="none"       output="+" />
          <when state="circumflex" output="⁺" />
        </action>
        <action id="ad06_y">
          <when state="none"       output="y" />
          <when state="grave"      output="ỳ" />
          <when state="acute"      output="ý" />
          <when state="circumflex" output="ŷ" />
          <when state="tilde"      output="ỹ" />
          <when state="diaeresis"  output="ÿ" />
        </action>
        <action id="ad06_Y">
          <when state="none"       output="Y" />
          <when state="grave"      output="Ỳ" />
          <when state="acute"      output="Ý" />
          <when state="circumflex" output="Ŷ" />
          <when state="tilde"      output="Ỹ" />
          <when state="diaeresis"  output="Ÿ" />
        </action>
        <action id="ad07_u">
          <when state="none"       output="u" />
          <when state="grave"      output="ù" />
          <when state="acute"      output="ú" />
          <when state="circumflex" output="û" />
          <when state="tilde"      output="ũ" />
          <when state="diaeresis"  output="ü" />
        </action>
        <action id="ad07_U">
          <when state="none"       output="U" />
          <when state="grave"      output="Ù" />
          <when state="acute"      output="Ú" />
          <when state="circumflex" output="Û" />
          <when state="tilde"      output="Ũ" />
          <when state="diaeresis"  output="Ü" />
        </action>
        <action id="ad07_4">
          <when state="none"       output="4" />
          <when state="circumflex" output="⁴" />
        </action>
        <action id="ad08_i">
          <when state="none"       output="i" />
          <when state="grave"      output="ì" />
          <when state="acute"      output="í" />
          <when state="circumflex" output="î" />
          <when state="tilde"      output="ĩ" />
          <when state="diaeresis"  output="ï" />
        </action>
        <action id="ad08_I">
          <when state="none"       output="I" />
          <when state="grave"      output="Ì" />
          <when state="acute"      output="Í" />
          <when state="circumflex" output="Î" />
          <when state="tilde"      output="Ĩ" />
          <when state="diaeresis"  output="Ï" />
        </action>
        <action id="ad08_5">
          <when state="none"       output="5" />
          <when state="circumflex" output="⁵" />
        </action>
        <action id="ad09_o">
          <when state="none"       output="o" />
          <when state="grave"      output="ò" />
          <when state="acute"      output="ó" />
          <when state="circumflex" output="ô" />
          <when state="tilde"      output="õ" />
          <when state="diaeresis"  output="ö" />
        </action>
        <action id="ad09_O">
          <when state="none"       output="O" />
          <when state="grave"      output="Ò" />
          <when state="acute"      output="Ó" />
          <when state="circumflex" output="Ô" />
          <when state="tilde"      output="Õ" />
          <when state="diaeresis"  output="Ö" />
        </action>
        <action id="ad09_6">
          <when state="none"       output="6" />
          <when state="circumflex" output="⁶" />
        </action>
        <action id="ad10_p">
          <when state="none"       output="p" />
          <when state="acute"      output="ṕ" />
        </action>
        <action id="ad10_P">
          <when state="none"       output="P" />
          <when state="acute"      output="Ṕ" />
        </action>

        <!-- Letters, second row -->
        <action id="ac01_a">
          <when state="none"       output="a" />
          <when state="grave"      output="à" />
          <when state="acute"      output="á" />
          <when state="circumflex" output="â" />
          <when state="tilde"      output="ã" />
          <when state="diaeresis"  output="ä" />
        </action>
        <action id="ac01_A">
          <when state="none"       output="A" />
          <when state="grave"      output="À" />
          <when state="acute"      output="Á" />
          <when state="circumflex" output="Â" />
          <when state="tilde"      output="Ã" />
          <when state="diaeresis"  output="Ä" />
        </action>
        <action id="ac02_s">
          <when state="none"       output="s" />
          <when state="acute"      output="ś" />
          <when state="circumflex" output="ŝ" />
        </action>
        <action id="ac02_S">
          <when state="none"       output="S" />
          <when state="acute"      output="Ś" />
          <when state="circumflex" output="Ŝ" />
        </action>
        <action id="ac05_g">
          <when state="none"       output="g" />
          <when state="acute"      output="ǵ" />
          <when state="circumflex" output="ĝ" />
        </action>
        <action id="ac05_G">
          <when state="none"       output="G" />
          <when state="acute"      output="Ǵ" />
          <when state="circumflex" output="Ĝ" />
        </action>
        <action id="ac06_h">
          <when state="none"       output="h" />
          <when state="circumflex" output="ĥ" />
          <when state="diaeresis"  output="ḧ" />
        </action>
        <action id="ac06_H">
          <when state="none"       output="H" />
          <when state="circumflex" output="Ĥ" />
          <when state="diaeresis"  output="Ḧ" />
        </action>
        <action id="ac07_j">
          <when state="none"       output="j" />
          <when state="circumflex" output="ĵ" />
        </action>
        <action id="ac07_J">
          <when state="none"       output="J" />
          <when state="circumflex" output="Ĵ" />
        </action>
        <action id="ac07_1">
          <when state="none"       output="1" />
          <when state="circumflex" output="¹" />
        </action>
        <action id="ac08_k">
          <when state="none"       output="k" />
          <when state="acute"      output="ḱ" />
        </action>
        <action id="ac08_K">
          <when state="none"       output="K" />
          <when state="acute"      output="Ḱ" />
        </action>
        <action id="ac08_2">
          <when state="none"       output="2" />
          <when state="circumflex" output="²" />
        </action>
        <action id="ac09_l">
          <when state="none"       output="l" />
          <when state="acute"      output="ĺ" />
        </action>
        <action id="ac09_L">
          <when state="none"       output="L" />
          <when state="acute"      output="Ĺ" />
        </action>
        <action id="ac09_3">
          <when state="none"       output="3" />
          <when state="circumflex" output="³" />
        </action>
        <action id="ac10_-">
          <when state="none"       output="-" />
          <when state="circumflex" output="⁻" />
        </action>

        <!-- Letters, third row -->
        <action id="ab01_z">
          <when state="none"       output="z" />
          <when state="acute"      output="ź" />
          <when state="circumflex" output="ẑ" />
        </action>
        <action id="ab01_Z">
          <when state="none"       output="Z" />
          <when state="acute"      output="Ź" />
          <when state="circumflex" output="Ẑ" />
        </action>
        <action id="ab02_x">
          <when state="none"       output="x" />
          <when state="diaeresis"  output="ẍ" />
        </action>
        <action id="ab02_X">
          <when state="none"       output="X" />
          <when state="diaeresis"  output="Ẍ" />
        </action>
        <action id="ab03_c">
          <when state="none"       output="c" />
          <when state="acute"      output="ć" />
          <when state="circumflex" output="ĉ" />
        </action>
        <action id="ab03_C">
          <when state="none"       output="C" />
          <when state="acute"      output="Ć" />
          <when state="circumflex" output="Ĉ" />
        </action>
        <action id="ab04_v">
          <when state="none"       output="v" />
          <when state="tilde"      output="ṽ" />
        </action>
        <action id="ab04_V">
          <when state="none"       output="V" />
          <when state="tilde"      output="Ṽ" />
        </action>
        <action id="ab06_n">
          <when state="none"       output="n" />
          <when state="grave"      output="ǹ" />
          <when state="acute"      output="ń" />
          <when state="tilde"      output="ñ" />
        </action>
        <action id="ab06_N">
          <when state="none"       output="N" />
          <when state="grave"      output="Ǹ" />
          <when state="acute"      output="Ń" />
          <when state="tilde"      output="Ñ" />
        </action>
        <action id="ab07_m">
          <when state="none"       output="m" />
          <when state="acute"      output="ḿ" />
        </action>
        <action id="ab07_M">
          <when state="none"       output="M" />
          <when state="acute"      output="Ḿ" />
        </action>
        <action id="ab07_0">
          <when state="none"       output="0" />
          <when state="circumflex" output="⁰" />
        </action>
        <action id="ab08_x003c">
          <when state="none"       output="&#x003c;" />
          <when state="tilde"      output="≲" />
        </action>
        <action id="ab09_x003e">
          <when state="none"       output="&#x003e;" />
          <when state="tilde"      output="≳" />
        </action>
        <action id="ab10_+">
          <when state="none"       output="+" />
          <when state="circumflex" output="⁺" />
        </action>

        <!-- Pinky keys -->
        <action id="ae11_-">
          <when state="none"       output="-" />
          <when state="circumflex" output="⁻" />
        </action>
        <action id="ae12_=">
          <when state="none"       output="=" />
          <when state="circumflex" output="⁼" />
          <when state="tilde"      output="≃" />
        </action>
        <action id="ae12_+">
          <when state="none"       output="+" />
          <when state="circumflex" output="⁺" />
        </action>

        <!-- Space bar -->
        <action id="spce_x0020">
          <when state="none"       output="&#x0020;" />
          <when state="grave"      output="`" />
          <when state="acute"      output="'" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        <action id="spce_x00a0">
          <when state="none"       output="&#x00a0;" />
          <when state="grave"      output="`" />
          <when state="acute"      output="'" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        <action id="spce_x202f">
          <when state="none"       output="&#x202f;" />
          <when state="grave"      output="`" />
          <when state="acute"      output="'" />
          <when state="circumflex" output="^" />
          <when state="tilde"      output="~" />
          <when state="diaeresis"  output="&#x0022;" />
        </action>
        """
    )

    terminators = macos_terminators(layout)
    assert len(terminators) == 5
    assert terminators == split(
        """
        <when state="grave"      output="`" />
        <when state="acute"      output="´" />
        <when state="circumflex" output="^" />
        <when state="tilde"      output="~" />
        <when state="diaeresis"  output="¨" />
        """
    )
