from textwrap import dedent

from kalamine import KeyboardLayout
from kalamine.template import xkb_keymap

from .util import get_layout_dict


def load_layout(filename: str) -> KeyboardLayout:
    return KeyboardLayout(get_layout_dict(filename))


def split(multiline_str: str):
    return dedent(multiline_str).lstrip().rstrip().splitlines()


def test_ansi():
    layout = load_layout("ansi")

    expected = split(
        """
        // Digits
        key <AE01> {[ 1               , exclam          , VoidSymbol      , VoidSymbol      ]}; // 1 !
        key <AE02> {[ 2               , at              , VoidSymbol      , VoidSymbol      ]}; // 2 @
        key <AE03> {[ 3               , numbersign      , VoidSymbol      , VoidSymbol      ]}; // 3 #
        key <AE04> {[ 4               , dollar          , VoidSymbol      , VoidSymbol      ]}; // 4 $
        key <AE05> {[ 5               , percent         , VoidSymbol      , VoidSymbol      ]}; // 5 %
        key <AE06> {[ 6               , asciicircum     , VoidSymbol      , VoidSymbol      ]}; // 6 ^
        key <AE07> {[ 7               , ampersand       , VoidSymbol      , VoidSymbol      ]}; // 7 &
        key <AE08> {[ 8               , asterisk        , VoidSymbol      , VoidSymbol      ]}; // 8 *
        key <AE09> {[ 9               , parenleft       , VoidSymbol      , VoidSymbol      ]}; // 9 (
        key <AE10> {[ 0               , parenright      , VoidSymbol      , VoidSymbol      ]}; // 0 )

        // Letters, first row
        key <AD01> {[ q               , Q               , VoidSymbol      , VoidSymbol      ]}; // q Q
        key <AD02> {[ w               , W               , VoidSymbol      , VoidSymbol      ]}; // w W
        key <AD03> {[ e               , E               , VoidSymbol      , VoidSymbol      ]}; // e E
        key <AD04> {[ r               , R               , VoidSymbol      , VoidSymbol      ]}; // r R
        key <AD05> {[ t               , T               , VoidSymbol      , VoidSymbol      ]}; // t T
        key <AD06> {[ y               , Y               , VoidSymbol      , VoidSymbol      ]}; // y Y
        key <AD07> {[ u               , U               , VoidSymbol      , VoidSymbol      ]}; // u U
        key <AD08> {[ i               , I               , VoidSymbol      , VoidSymbol      ]}; // i I
        key <AD09> {[ o               , O               , VoidSymbol      , VoidSymbol      ]}; // o O
        key <AD10> {[ p               , P               , VoidSymbol      , VoidSymbol      ]}; // p P

        // Letters, second row
        key <AC01> {[ a               , A               , VoidSymbol      , VoidSymbol      ]}; // a A
        key <AC02> {[ s               , S               , VoidSymbol      , VoidSymbol      ]}; // s S
        key <AC03> {[ d               , D               , VoidSymbol      , VoidSymbol      ]}; // d D
        key <AC04> {[ f               , F               , VoidSymbol      , VoidSymbol      ]}; // f F
        key <AC05> {[ g               , G               , VoidSymbol      , VoidSymbol      ]}; // g G
        key <AC06> {[ h               , H               , VoidSymbol      , VoidSymbol      ]}; // h H
        key <AC07> {[ j               , J               , VoidSymbol      , VoidSymbol      ]}; // j J
        key <AC08> {[ k               , K               , VoidSymbol      , VoidSymbol      ]}; // k K
        key <AC09> {[ l               , L               , VoidSymbol      , VoidSymbol      ]}; // l L
        key <AC10> {[ semicolon       , colon           , VoidSymbol      , VoidSymbol      ]}; // ; :

        // Letters, third row
        key <AB01> {[ z               , Z               , VoidSymbol      , VoidSymbol      ]}; // z Z
        key <AB02> {[ x               , X               , VoidSymbol      , VoidSymbol      ]}; // x X
        key <AB03> {[ c               , C               , VoidSymbol      , VoidSymbol      ]}; // c C
        key <AB04> {[ v               , V               , VoidSymbol      , VoidSymbol      ]}; // v V
        key <AB05> {[ b               , B               , VoidSymbol      , VoidSymbol      ]}; // b B
        key <AB06> {[ n               , N               , VoidSymbol      , VoidSymbol      ]}; // n N
        key <AB07> {[ m               , M               , VoidSymbol      , VoidSymbol      ]}; // m M
        key <AB08> {[ comma           , less            , VoidSymbol      , VoidSymbol      ]}; // , <
        key <AB09> {[ period          , greater         , VoidSymbol      , VoidSymbol      ]}; // . >
        key <AB10> {[ slash           , question        , VoidSymbol      , VoidSymbol      ]}; // / ?

        // Pinky keys
        key <AE11> {[ minus           , underscore      , VoidSymbol      , VoidSymbol      ]}; // - _
        key <AE12> {[ equal           , plus            , VoidSymbol      , VoidSymbol      ]}; // = +
        key <AE13> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <AD11> {[ bracketleft     , braceleft       , VoidSymbol      , VoidSymbol      ]}; // [ {
        key <AD12> {[ bracketright    , braceright      , VoidSymbol      , VoidSymbol      ]}; // ] }
        key <AC11> {[ apostrophe      , quotedbl        , VoidSymbol      , VoidSymbol      ]}; // ' "
        key <AB11> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <TLDE> {[ grave           , asciitilde      , VoidSymbol      , VoidSymbol      ]}; // ` ~
        key <BKSL> {[ backslash       , bar             , VoidSymbol      , VoidSymbol      ]}; // \\ |
        key <LSGT> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //

        // Space bar
        key <SPCE> {[ space           , space           , apostrophe      , apostrophe      ]}; //     ' '
        """
    )

    xkbcomp = xkb_keymap(layout, xkbcomp=True)
    assert len(xkbcomp) == len(expected)
    assert xkbcomp == expected

    xkbpatch = xkb_keymap(layout, xkbcomp=False)
    assert len(xkbpatch) == len(expected)
    assert xkbpatch == expected


def test_intl():
    layout = load_layout("intl")

    expected = split(
        """
        // Digits
        key <AE01> {[ 1               , exclam          , VoidSymbol      , VoidSymbol      ]}; // 1 !
        key <AE02> {[ 2               , at              , VoidSymbol      , VoidSymbol      ]}; // 2 @
        key <AE03> {[ 3               , numbersign      , VoidSymbol      , VoidSymbol      ]}; // 3 #
        key <AE04> {[ 4               , dollar          , VoidSymbol      , VoidSymbol      ]}; // 4 $
        key <AE05> {[ 5               , percent         , VoidSymbol      , VoidSymbol      ]}; // 5 %
        key <AE06> {[ 6               , dead_circumflex , VoidSymbol      , VoidSymbol      ]}; // 6 ^
        key <AE07> {[ 7               , ampersand       , VoidSymbol      , VoidSymbol      ]}; // 7 &
        key <AE08> {[ 8               , asterisk        , VoidSymbol      , VoidSymbol      ]}; // 8 *
        key <AE09> {[ 9               , parenleft       , VoidSymbol      , VoidSymbol      ]}; // 9 (
        key <AE10> {[ 0               , parenright      , VoidSymbol      , VoidSymbol      ]}; // 0 )

        // Letters, first row
        key <AD01> {[ q               , Q               , VoidSymbol      , VoidSymbol      ]}; // q Q
        key <AD02> {[ w               , W               , VoidSymbol      , VoidSymbol      ]}; // w W
        key <AD03> {[ e               , E               , eacute          , Eacute          ]}; // e E é É
        key <AD04> {[ r               , R               , VoidSymbol      , VoidSymbol      ]}; // r R
        key <AD05> {[ t               , T               , VoidSymbol      , VoidSymbol      ]}; // t T
        key <AD06> {[ y               , Y               , VoidSymbol      , VoidSymbol      ]}; // y Y
        key <AD07> {[ u               , U               , uacute          , Uacute          ]}; // u U ú Ú
        key <AD08> {[ i               , I               , iacute          , Iacute          ]}; // i I í Í
        key <AD09> {[ o               , O               , oacute          , Oacute          ]}; // o O ó Ó
        key <AD10> {[ p               , P               , VoidSymbol      , VoidSymbol      ]}; // p P

        // Letters, second row
        key <AC01> {[ a               , A               , aacute          , Aacute          ]}; // a A á Á
        key <AC02> {[ s               , S               , VoidSymbol      , VoidSymbol      ]}; // s S
        key <AC03> {[ d               , D               , VoidSymbol      , VoidSymbol      ]}; // d D
        key <AC04> {[ f               , F               , VoidSymbol      , VoidSymbol      ]}; // f F
        key <AC05> {[ g               , G               , VoidSymbol      , VoidSymbol      ]}; // g G
        key <AC06> {[ h               , H               , VoidSymbol      , VoidSymbol      ]}; // h H
        key <AC07> {[ j               , J               , VoidSymbol      , VoidSymbol      ]}; // j J
        key <AC08> {[ k               , K               , VoidSymbol      , VoidSymbol      ]}; // k K
        key <AC09> {[ l               , L               , VoidSymbol      , VoidSymbol      ]}; // l L
        key <AC10> {[ semicolon       , colon           , VoidSymbol      , VoidSymbol      ]}; // ; :

        // Letters, third row
        key <AB01> {[ z               , Z               , VoidSymbol      , VoidSymbol      ]}; // z Z
        key <AB02> {[ x               , X               , VoidSymbol      , VoidSymbol      ]}; // x X
        key <AB03> {[ c               , C               , ccedilla        , Ccedilla        ]}; // c C ç Ç
        key <AB04> {[ v               , V               , VoidSymbol      , VoidSymbol      ]}; // v V
        key <AB05> {[ b               , B               , VoidSymbol      , VoidSymbol      ]}; // b B
        key <AB06> {[ n               , N               , VoidSymbol      , VoidSymbol      ]}; // n N
        key <AB07> {[ m               , M               , VoidSymbol      , VoidSymbol      ]}; // m M
        key <AB08> {[ comma           , less            , VoidSymbol      , VoidSymbol      ]}; // , <
        key <AB09> {[ period          , greater         , ellipsis        , VoidSymbol      ]}; // . > …
        key <AB10> {[ slash           , question        , VoidSymbol      , VoidSymbol      ]}; // / ?

        // Pinky keys
        key <AE11> {[ minus           , underscore      , VoidSymbol      , VoidSymbol      ]}; // - _
        key <AE12> {[ equal           , plus            , VoidSymbol      , VoidSymbol      ]}; // = +
        key <AE13> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <AD11> {[ bracketleft     , braceleft       , VoidSymbol      , VoidSymbol      ]}; // [ {
        key <AD12> {[ bracketright    , braceright      , VoidSymbol      , VoidSymbol      ]}; // ] }
        key <AC11> {[ ISO_Level3_Latch, dead_diaeresis  , apostrophe      , VoidSymbol      ]}; // ' ¨ '
        key <AB11> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <TLDE> {[ dead_grave      , dead_tilde      , VoidSymbol      , VoidSymbol      ]}; // ` ~
        key <BKSL> {[ backslash       , bar             , VoidSymbol      , VoidSymbol      ]}; // \\ |
        key <LSGT> {[ backslash       , bar             , VoidSymbol      , VoidSymbol      ]}; // \\ |

        // Space bar
        key <SPCE> {[ space           , space           , apostrophe      , apostrophe      ]}; //     ' '
        """
    )

    xkbcomp = xkb_keymap(layout, xkbcomp=True)
    assert len(xkbcomp) == len(expected)
    assert xkbcomp == expected

    xkbpatch = xkb_keymap(layout, xkbcomp=False)
    assert len(xkbpatch) == len(expected)
    assert xkbpatch == expected


def test_prog():
    layout = load_layout("prog")

    expected = split(
        """
        // Digits
        key <AE01> {[ 1               , exclam          , exclam          , VoidSymbol      ]}; // 1 ! !
        key <AE02> {[ 2               , at              , parenleft       , VoidSymbol      ]}; // 2 @ (
        key <AE03> {[ 3               , numbersign      , parenright      , VoidSymbol      ]}; // 3 # )
        key <AE04> {[ 4               , dollar          , apostrophe      , VoidSymbol      ]}; // 4 $ '
        key <AE05> {[ 5               , percent         , quotedbl        , VoidSymbol      ]}; // 5 % "
        key <AE06> {[ 6               , asciicircum     , dead_circumflex , VoidSymbol      ]}; // 6 ^ ^
        key <AE07> {[ 7               , ampersand       , 7               , VoidSymbol      ]}; // 7 & 7
        key <AE08> {[ 8               , asterisk        , 8               , VoidSymbol      ]}; // 8 * 8
        key <AE09> {[ 9               , parenleft       , 9               , VoidSymbol      ]}; // 9 ( 9
        key <AE10> {[ 0               , parenright      , slash           , VoidSymbol      ]}; // 0 ) /

        // Letters, first row
        key <AD01> {[ q               , Q               , equal           , VoidSymbol      ]}; // q Q =
        key <AD02> {[ w               , W               , less            , lessthanequal   ]}; // w W < ≤
        key <AD03> {[ e               , E               , greater         , greaterthanequal]}; // e E > ≥
        key <AD04> {[ r               , R               , minus           , VoidSymbol      ]}; // r R -
        key <AD05> {[ t               , T               , plus            , VoidSymbol      ]}; // t T +
        key <AD06> {[ y               , Y               , VoidSymbol      , VoidSymbol      ]}; // y Y
        key <AD07> {[ u               , U               , 4               , VoidSymbol      ]}; // u U 4
        key <AD08> {[ i               , I               , 5               , VoidSymbol      ]}; // i I 5
        key <AD09> {[ o               , O               , 6               , VoidSymbol      ]}; // o O 6
        key <AD10> {[ p               , P               , asterisk        , VoidSymbol      ]}; // p P *

        // Letters, second row
        key <AC01> {[ a               , A               , braceleft       , VoidSymbol      ]}; // a A {
        key <AC02> {[ s               , S               , bracketleft     , VoidSymbol      ]}; // s S [
        key <AC03> {[ d               , D               , bracketright    , VoidSymbol      ]}; // d D ]
        key <AC04> {[ f               , F               , braceright      , VoidSymbol      ]}; // f F }
        key <AC05> {[ g               , G               , slash           , VoidSymbol      ]}; // g G /
        key <AC06> {[ h               , H               , VoidSymbol      , VoidSymbol      ]}; // h H
        key <AC07> {[ j               , J               , 1               , VoidSymbol      ]}; // j J 1
        key <AC08> {[ k               , K               , 2               , VoidSymbol      ]}; // k K 2
        key <AC09> {[ l               , L               , 3               , VoidSymbol      ]}; // l L 3
        key <AC10> {[ semicolon       , colon           , minus           , VoidSymbol      ]}; // ; : -

        // Letters, third row
        key <AB01> {[ z               , Z               , asciitilde      , VoidSymbol      ]}; // z Z ~
        key <AB02> {[ x               , X               , grave           , VoidSymbol      ]}; // x X `
        key <AB03> {[ c               , C               , bar             , brokenbar       ]}; // c C | ¦
        key <AB04> {[ v               , V               , underscore      , VoidSymbol      ]}; // v V _
        key <AB05> {[ b               , B               , backslash       , VoidSymbol      ]}; // b B \\ 
        key <AB06> {[ n               , N               , VoidSymbol      , VoidSymbol      ]}; // n N
        key <AB07> {[ m               , M               , 0               , VoidSymbol      ]}; // m M 0
        key <AB08> {[ comma           , less            , comma           , VoidSymbol      ]}; // , < ,
        key <AB09> {[ period          , greater         , period          , VoidSymbol      ]}; // . > .
        key <AB10> {[ slash           , question        , plus            , VoidSymbol      ]}; // / ? +

        // Pinky keys
        key <AE11> {[ minus           , underscore      , VoidSymbol      , VoidSymbol      ]}; // - _
        key <AE12> {[ equal           , plus            , VoidSymbol      , VoidSymbol      ]}; // = +
        key <AE13> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <AD11> {[ bracketleft     , braceleft       , VoidSymbol      , VoidSymbol      ]}; // [ {
        key <AD12> {[ bracketright    , braceright      , VoidSymbol      , VoidSymbol      ]}; // ] }
        key <AC11> {[ apostrophe      , quotedbl        , dead_acute      , dead_diaeresis  ]}; // ' " ´ ¨
        key <AB11> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //
        key <TLDE> {[ grave           , asciitilde      , dead_grave      , dead_tilde      ]}; // ` ~ ` ~
        key <BKSL> {[ backslash       , bar             , VoidSymbol      , VoidSymbol      ]}; // \\ |
        key <LSGT> {[ VoidSymbol      , VoidSymbol      , VoidSymbol      , VoidSymbol      ]}; //

        // Space bar
        key <SPCE> {[ space           , space           , space           , space           ]}; //
        """
    )

    xkbcomp = xkb_keymap(layout, xkbcomp=True)
    assert len(xkbcomp) == len(expected)
    assert xkbcomp == expected

    xkbpatch = xkb_keymap(layout, xkbcomp=False)
    assert len(xkbpatch) == len(expected)
    assert xkbpatch == expected
