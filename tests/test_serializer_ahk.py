from textwrap import dedent

from kalamine import KeyboardLayout
from kalamine.template import ahk_keymap, ahk_shortcuts

from .util import get_layout_dict


def load_layout(filename: str) -> KeyboardLayout:
    return KeyboardLayout(get_layout_dict(filename))


def split(multiline_str: str):
    return dedent(multiline_str).lstrip().splitlines()


QWERTY_INTL = split(
    """
    ;  Digits

     SC02::SendKey("U+0031", {"*^": "U+00b9"}) ; 1
    +SC02::SendKey("U+0021", {}) ; !

     SC03::SendKey("U+0032", {"*^": "U+00b2"}) ; 2
    +SC03::SendKey("U+0040", {}) ; @

     SC04::SendKey("U+0033", {"*^": "U+00b3"}) ; 3
    +SC04::SendKey("U+0023", {}) ; #

     SC05::SendKey("U+0034", {"*^": "U+2074"}) ; 4
    +SC05::SendKey("U+0024", {}) ; $

     SC06::SendKey("U+0035", {"*^": "U+2075"}) ; 5
    +SC06::SendKey("U+0025", {}) ; %

     SC07::SendKey("U+0036", {"*^": "U+2076"}) ; 6
    +SC07::SendKey("*^", {"*^": "^"})

     SC08::SendKey("U+0037", {"*^": "U+2077"}) ; 7
    +SC08::SendKey("U+0026", {}) ; &

     SC09::SendKey("U+0038", {"*^": "U+2078"}) ; 8
    +SC09::SendKey("U+002a", {}) ; *

     SC0a::SendKey("U+0039", {"*^": "U+2079"}) ; 9
    +SC0a::SendKey("U+0028", {"*^": "U+207d"}) ; (

     SC0b::SendKey("U+0030", {"*^": "U+2070"}) ; 0
    +SC0b::SendKey("U+0029", {"*^": "U+207e"}) ; )

    ;  Letters, first row

     SC10::SendKey("U+0071", {}) ; q
    +SC10::SendKey("U+0051", {}) ; Q

     SC11::SendKey("U+0077", {"*``": "U+1e81", "*^": "U+0175", "*¨": "U+1e85"}) ; w
    +SC11::SendKey("U+0057", {"*``": "U+1e80", "*^": "U+0174", "*¨": "U+1e84"}) ; W

     SC12::SendKey("U+0065", {"*``": "U+00e8", "*~": "U+1ebd", "*^": "U+00ea", "**": "U+00e9", "*¨": "U+00eb"}) ; e
    +SC12::SendKey("U+0045", {"*``": "U+00c8", "*~": "U+1ebc", "*^": "U+00ca", "**": "U+00c9", "*¨": "U+00cb"}) ; E

     SC13::SendKey("U+0072", {}) ; r
    +SC13::SendKey("U+0052", {}) ; R

     SC14::SendKey("U+0074", {"*¨": "U+1e97"}) ; t
    +SC14::SendKey("U+0054", {}) ; T

     SC15::SendKey("U+0079", {"*``": "U+1ef3", "*~": "U+1ef9", "*^": "U+0177", "*¨": "U+00ff"}) ; y
    +SC15::SendKey("U+0059", {"*``": "U+1ef2", "*~": "U+1ef8", "*^": "U+0176", "*¨": "U+0178"}) ; Y

     SC16::SendKey("U+0075", {"*``": "U+00f9", "*~": "U+0169", "*^": "U+00fb", "**": "U+00fa", "*¨": "U+00fc"}) ; u
    +SC16::SendKey("U+0055", {"*``": "U+00d9", "*~": "U+0168", "*^": "U+00db", "**": "U+00da", "*¨": "U+00dc"}) ; U

     SC17::SendKey("U+0069", {"*``": "U+00ec", "*~": "U+0129", "*^": "U+00ee", "**": "U+00ed", "*¨": "U+00ef"}) ; i
    +SC17::SendKey("U+0049", {"*``": "U+00cc", "*~": "U+0128", "*^": "U+00ce", "**": "U+00cd", "*¨": "U+00cf"}) ; I

     SC18::SendKey("U+006f", {"*``": "U+00f2", "*~": "U+00f5", "*^": "U+00f4", "**": "U+00f3", "*¨": "U+00f6"}) ; o
    +SC18::SendKey("U+004f", {"*``": "U+00d2", "*~": "U+00d5", "*^": "U+00d4", "**": "U+00d3", "*¨": "U+00d6"}) ; O

     SC19::SendKey("U+0070", {}) ; p
    +SC19::SendKey("U+0050", {}) ; P

    ;  Letters, second row

     SC1e::SendKey("U+0061", {"*``": "U+00e0", "*~": "U+00e3", "*^": "U+00e2", "**": "U+00e1", "*¨": "U+00e4"}) ; a
    +SC1e::SendKey("U+0041", {"*``": "U+00c0", "*~": "U+00c3", "*^": "U+00c2", "**": "U+00c1", "*¨": "U+00c4"}) ; A

     SC1f::SendKey("U+0073", {"*^": "U+015d"}) ; s
    +SC1f::SendKey("U+0053", {"*^": "U+015c"}) ; S

     SC20::SendKey("U+0064", {}) ; d
    +SC20::SendKey("U+0044", {}) ; D

     SC21::SendKey("U+0066", {}) ; f
    +SC21::SendKey("U+0046", {}) ; F

     SC22::SendKey("U+0067", {"*^": "U+011d"}) ; g
    +SC22::SendKey("U+0047", {"*^": "U+011c"}) ; G

     SC23::SendKey("U+0068", {"*^": "U+0125", "*¨": "U+1e27"}) ; h
    +SC23::SendKey("U+0048", {"*^": "U+0124", "*¨": "U+1e26"}) ; H

     SC24::SendKey("U+006a", {"*^": "U+0135"}) ; j
    +SC24::SendKey("U+004a", {"*^": "U+0134"}) ; J

     SC25::SendKey("U+006b", {}) ; k
    +SC25::SendKey("U+004b", {}) ; K

     SC26::SendKey("U+006c", {}) ; l
    +SC26::SendKey("U+004c", {}) ; L

     SC27::SendKey("U+003b", {}) ; ;
    +SC27::SendKey("U+003a", {}) ; :

    ;  Letters, third row

     SC2c::SendKey("U+007a", {"*^": "U+1e91"}) ; z
    +SC2c::SendKey("U+005a", {"*^": "U+1e90"}) ; Z

     SC2d::SendKey("U+0078", {"*¨": "U+1e8d"}) ; x
    +SC2d::SendKey("U+0058", {"*¨": "U+1e8c"}) ; X

     SC2e::SendKey("U+0063", {"*^": "U+0109", "**": "U+00e7"}) ; c
    +SC2e::SendKey("U+0043", {"*^": "U+0108", "**": "U+00c7"}) ; C

     SC2f::SendKey("U+0076", {"*~": "U+1e7d"}) ; v
    +SC2f::SendKey("U+0056", {"*~": "U+1e7c"}) ; V

     SC30::SendKey("U+0062", {}) ; b
    +SC30::SendKey("U+0042", {}) ; B

     SC31::SendKey("U+006e", {"*``": "U+01f9", "*~": "U+00f1"}) ; n
    +SC31::SendKey("U+004e", {"*``": "U+01f8", "*~": "U+00d1"}) ; N

     SC32::SendKey("U+006d", {}) ; m
    +SC32::SendKey("U+004d", {}) ; M

     SC33::SendKey("U+002c", {}) ; ,
    +SC33::SendKey("U+003c", {"*~": "U+2272"}) ; <

     SC34::SendKey("U+002e", {"**": "U+2026"}) ; .
    +SC34::SendKey("U+003e", {"*~": "U+2273"}) ; >

     SC35::SendKey("U+002f", {}) ; /
    +SC35::SendKey("U+003f", {}) ; ?

    ;  Pinky keys

     SC0c::SendKey("U+002d", {"*^": "U+207b"}) ; -
    +SC0c::SendKey("U+005f", {}) ; _

     SC0d::SendKey("U+003d", {"*~": "U+2243", "*^": "U+207c"}) ; =
    +SC0d::SendKey("U+002b", {"*^": "U+207a"}) ; +

     SC1a::SendKey("U+005b", {}) ; [
    +SC1a::SendKey("U+007b", {}) ; {

     SC1b::SendKey("U+005d", {}) ; ]
    +SC1b::SendKey("U+007d", {}) ; }

     SC28::SendKey("**", {"**": "´"})
    +SC28::SendKey("*¨", {"*¨": "¨"})

     SC29::SendKey("*``", {"*``": "`"}) ; *`
    +SC29::SendKey("*~", {"*~": "~"})

     SC2b::SendKey("U+005c", {}) ; \\
    +SC2b::SendKey("U+007c", {}) ; |

     SC56::SendKey("U+005c", {}) ; \\
    +SC56::SendKey("U+007c", {}) ; |

    ;  Space bar

     SC39::SendKey("U+0020", {"*``": "U+0060", "*~": "U+007e", "*^": "U+005e", "**": "U+0027", "*¨": "U+0022"}) ;  
    +SC39::SendKey("U+0020", {"*``": "U+0060", "*~": "U+007e", "*^": "U+005e", "**": "U+0027", "*¨": "U+0022"}) ;  

    """
)


QWERTY_SHORTCUTS = split(
    """
    ;  Digits

    ;  Letters, first row

     ^SC10::Send  ^q
    ^+SC10::Send ^+Q

     ^SC11::Send  ^w
    ^+SC11::Send ^+W

     ^SC12::Send  ^e
    ^+SC12::Send ^+E

     ^SC13::Send  ^r
    ^+SC13::Send ^+R

     ^SC14::Send  ^t
    ^+SC14::Send ^+T

     ^SC15::Send  ^y
    ^+SC15::Send ^+Y

     ^SC16::Send  ^u
    ^+SC16::Send ^+U

     ^SC17::Send  ^i
    ^+SC17::Send ^+I

     ^SC18::Send  ^o
    ^+SC18::Send ^+O

     ^SC19::Send  ^p
    ^+SC19::Send ^+P

    ;  Letters, second row

     ^SC1e::Send  ^a
    ^+SC1e::Send ^+A

     ^SC1f::Send  ^s
    ^+SC1f::Send ^+S

     ^SC20::Send  ^d
    ^+SC20::Send ^+D

     ^SC21::Send  ^f
    ^+SC21::Send ^+F

     ^SC22::Send  ^g
    ^+SC22::Send ^+G

     ^SC23::Send  ^h
    ^+SC23::Send ^+H

     ^SC24::Send  ^j
    ^+SC24::Send ^+J

     ^SC25::Send  ^k
    ^+SC25::Send ^+K

     ^SC26::Send  ^l
    ^+SC26::Send ^+L

    ;  Letters, third row

     ^SC2c::Send  ^z
    ^+SC2c::Send ^+Z

     ^SC2d::Send  ^x
    ^+SC2d::Send ^+X

     ^SC2e::Send  ^c
    ^+SC2e::Send ^+C

     ^SC2f::Send  ^v
    ^+SC2f::Send ^+V

     ^SC30::Send  ^b
    ^+SC30::Send ^+B

     ^SC31::Send  ^n
    ^+SC31::Send ^+N

     ^SC32::Send  ^m
    ^+SC32::Send ^+M

    ;  Pinky keys

    ;  Space bar

    """
)


def test_ansi():
    layout = load_layout("ansi")

    keymap = ahk_keymap(layout)
    assert len(keymap) == 156
    assert keymap == split(
        """
        ;  Digits

         SC02::SendKey("U+0031", {}) ; 1
        +SC02::SendKey("U+0021", {}) ; !

         SC03::SendKey("U+0032", {}) ; 2
        +SC03::SendKey("U+0040", {}) ; @

         SC04::SendKey("U+0033", {}) ; 3
        +SC04::SendKey("U+0023", {}) ; #

         SC05::SendKey("U+0034", {}) ; 4
        +SC05::SendKey("U+0024", {}) ; $

         SC06::SendKey("U+0035", {}) ; 5
        +SC06::SendKey("U+0025", {}) ; %

         SC07::SendKey("U+0036", {}) ; 6
        +SC07::SendKey("U+005e", {}) ; ^

         SC08::SendKey("U+0037", {}) ; 7
        +SC08::SendKey("U+0026", {}) ; &

         SC09::SendKey("U+0038", {}) ; 8
        +SC09::SendKey("U+002a", {}) ; *

         SC0a::SendKey("U+0039", {}) ; 9
        +SC0a::SendKey("U+0028", {}) ; (

         SC0b::SendKey("U+0030", {}) ; 0
        +SC0b::SendKey("U+0029", {}) ; )

        ;  Letters, first row

         SC10::SendKey("U+0071", {}) ; q
        +SC10::SendKey("U+0051", {}) ; Q

         SC11::SendKey("U+0077", {}) ; w
        +SC11::SendKey("U+0057", {}) ; W

         SC12::SendKey("U+0065", {}) ; e
        +SC12::SendKey("U+0045", {}) ; E

         SC13::SendKey("U+0072", {}) ; r
        +SC13::SendKey("U+0052", {}) ; R

         SC14::SendKey("U+0074", {}) ; t
        +SC14::SendKey("U+0054", {}) ; T

         SC15::SendKey("U+0079", {}) ; y
        +SC15::SendKey("U+0059", {}) ; Y

         SC16::SendKey("U+0075", {}) ; u
        +SC16::SendKey("U+0055", {}) ; U

         SC17::SendKey("U+0069", {}) ; i
        +SC17::SendKey("U+0049", {}) ; I

         SC18::SendKey("U+006f", {}) ; o
        +SC18::SendKey("U+004f", {}) ; O

         SC19::SendKey("U+0070", {}) ; p
        +SC19::SendKey("U+0050", {}) ; P

        ;  Letters, second row

         SC1e::SendKey("U+0061", {}) ; a
        +SC1e::SendKey("U+0041", {}) ; A

         SC1f::SendKey("U+0073", {}) ; s
        +SC1f::SendKey("U+0053", {}) ; S

         SC20::SendKey("U+0064", {}) ; d
        +SC20::SendKey("U+0044", {}) ; D

         SC21::SendKey("U+0066", {}) ; f
        +SC21::SendKey("U+0046", {}) ; F

         SC22::SendKey("U+0067", {}) ; g
        +SC22::SendKey("U+0047", {}) ; G

         SC23::SendKey("U+0068", {}) ; h
        +SC23::SendKey("U+0048", {}) ; H

         SC24::SendKey("U+006a", {}) ; j
        +SC24::SendKey("U+004a", {}) ; J

         SC25::SendKey("U+006b", {}) ; k
        +SC25::SendKey("U+004b", {}) ; K

         SC26::SendKey("U+006c", {}) ; l
        +SC26::SendKey("U+004c", {}) ; L

         SC27::SendKey("U+003b", {}) ; ;
        +SC27::SendKey("U+003a", {}) ; :

        ;  Letters, third row

         SC2c::SendKey("U+007a", {}) ; z
        +SC2c::SendKey("U+005a", {}) ; Z

         SC2d::SendKey("U+0078", {}) ; x
        +SC2d::SendKey("U+0058", {}) ; X

         SC2e::SendKey("U+0063", {}) ; c
        +SC2e::SendKey("U+0043", {}) ; C

         SC2f::SendKey("U+0076", {}) ; v
        +SC2f::SendKey("U+0056", {}) ; V

         SC30::SendKey("U+0062", {}) ; b
        +SC30::SendKey("U+0042", {}) ; B

         SC31::SendKey("U+006e", {}) ; n
        +SC31::SendKey("U+004e", {}) ; N

         SC32::SendKey("U+006d", {}) ; m
        +SC32::SendKey("U+004d", {}) ; M

         SC33::SendKey("U+002c", {}) ; ,
        +SC33::SendKey("U+003c", {}) ; <

         SC34::SendKey("U+002e", {}) ; .
        +SC34::SendKey("U+003e", {}) ; >

         SC35::SendKey("U+002f", {}) ; /
        +SC35::SendKey("U+003f", {}) ; ?

        ;  Pinky keys

         SC0c::SendKey("U+002d", {}) ; -
        +SC0c::SendKey("U+005f", {}) ; _

         SC0d::SendKey("U+003d", {}) ; =
        +SC0d::SendKey("U+002b", {}) ; +

         SC1a::SendKey("U+005b", {}) ; [
        +SC1a::SendKey("U+007b", {}) ; {

         SC1b::SendKey("U+005d", {}) ; ]
        +SC1b::SendKey("U+007d", {}) ; }

         SC28::SendKey("U+0027", {}) ; '
        +SC28::SendKey("U+0022", {}) ; "

         SC29::SendKey("U+0060", {}) ; `
        +SC29::SendKey("U+007e", {}) ; ~
 
         SC2b::SendKey("U+005c", {}) ; \\
        +SC2b::SendKey("U+007c", {}) ; |

        ;  Space bar

         SC39::SendKey("U+0020", {}) ;  
        +SC39::SendKey("U+0020", {}) ;  

        """
    )

    assert len(ahk_keymap(layout, True)) == 12

    shortcuts = ahk_shortcuts(layout)
    assert len(shortcuts) == len(QWERTY_SHORTCUTS)
    assert shortcuts == QWERTY_SHORTCUTS


def test_intl():
    layout = load_layout("intl")

    keymap = ahk_keymap(layout)
    assert len(keymap) == 159
    assert keymap == split(
        """
        ;  Digits

         SC02::SendKey("U+0031", {"*^": "U+00b9"}) ; 1
        +SC02::SendKey("U+0021", {}) ; !

         SC03::SendKey("U+0032", {"*^": "U+00b2"}) ; 2
        +SC03::SendKey("U+0040", {}) ; @

         SC04::SendKey("U+0033", {"*^": "U+00b3"}) ; 3
        +SC04::SendKey("U+0023", {}) ; #

         SC05::SendKey("U+0034", {"*^": "U+2074"}) ; 4
        +SC05::SendKey("U+0024", {}) ; $

         SC06::SendKey("U+0035", {"*^": "U+2075"}) ; 5
        +SC06::SendKey("U+0025", {}) ; %

         SC07::SendKey("U+0036", {"*^": "U+2076"}) ; 6
        +SC07::SendKey("*^", {"*^": "^"})

         SC08::SendKey("U+0037", {"*^": "U+2077"}) ; 7
        +SC08::SendKey("U+0026", {}) ; &

         SC09::SendKey("U+0038", {"*^": "U+2078"}) ; 8
        +SC09::SendKey("U+002a", {}) ; *

         SC0a::SendKey("U+0039", {"*^": "U+2079"}) ; 9
        +SC0a::SendKey("U+0028", {"*^": "U+207d"}) ; (

         SC0b::SendKey("U+0030", {"*^": "U+2070"}) ; 0
        +SC0b::SendKey("U+0029", {"*^": "U+207e"}) ; )

        ;  Letters, first row

         SC10::SendKey("U+0071", {}) ; q
        +SC10::SendKey("U+0051", {}) ; Q

         SC11::SendKey("U+0077", {"*``": "U+1e81", "*^": "U+0175", "*¨": "U+1e85"}) ; w
        +SC11::SendKey("U+0057", {"*``": "U+1e80", "*^": "U+0174", "*¨": "U+1e84"}) ; W

         SC12::SendKey("U+0065", {"**": "U+00e9", "*``": "U+00e8", "*^": "U+00ea", "*~": "U+1ebd", "*¨": "U+00eb"}) ; e
        +SC12::SendKey("U+0045", {"**": "U+00c9", "*``": "U+00c8", "*^": "U+00ca", "*~": "U+1ebc", "*¨": "U+00cb"}) ; E

         SC13::SendKey("U+0072", {}) ; r
        +SC13::SendKey("U+0052", {}) ; R

         SC14::SendKey("U+0074", {"*¨": "U+1e97"}) ; t
        +SC14::SendKey("U+0054", {}) ; T

         SC15::SendKey("U+0079", {"*``": "U+1ef3", "*^": "U+0177", "*~": "U+1ef9", "*¨": "U+00ff"}) ; y
        +SC15::SendKey("U+0059", {"*``": "U+1ef2", "*^": "U+0176", "*~": "U+1ef8", "*¨": "U+0178"}) ; Y

         SC16::SendKey("U+0075", {"**": "U+00fa", "*``": "U+00f9", "*^": "U+00fb", "*~": "U+0169", "*¨": "U+00fc"}) ; u
        +SC16::SendKey("U+0055", {"**": "U+00da", "*``": "U+00d9", "*^": "U+00db", "*~": "U+0168", "*¨": "U+00dc"}) ; U

         SC17::SendKey("U+0069", {"**": "U+00ed", "*``": "U+00ec", "*^": "U+00ee", "*~": "U+0129", "*¨": "U+00ef"}) ; i
        +SC17::SendKey("U+0049", {"**": "U+00cd", "*``": "U+00cc", "*^": "U+00ce", "*~": "U+0128", "*¨": "U+00cf"}) ; I

         SC18::SendKey("U+006f", {"**": "U+00f3", "*``": "U+00f2", "*^": "U+00f4", "*~": "U+00f5", "*¨": "U+00f6"}) ; o
        +SC18::SendKey("U+004f", {"**": "U+00d3", "*``": "U+00d2", "*^": "U+00d4", "*~": "U+00d5", "*¨": "U+00d6"}) ; O

         SC19::SendKey("U+0070", {}) ; p
        +SC19::SendKey("U+0050", {}) ; P

        ;  Letters, second row

         SC1e::SendKey("U+0061", {"**": "U+00e1", "*``": "U+00e0", "*^": "U+00e2", "*~": "U+00e3", "*¨": "U+00e4"}) ; a
        +SC1e::SendKey("U+0041", {"**": "U+00c1", "*``": "U+00c0", "*^": "U+00c2", "*~": "U+00c3", "*¨": "U+00c4"}) ; A

         SC1f::SendKey("U+0073", {"*^": "U+015d"}) ; s
        +SC1f::SendKey("U+0053", {"*^": "U+015c"}) ; S

         SC20::SendKey("U+0064", {}) ; d
        +SC20::SendKey("U+0044", {}) ; D

         SC21::SendKey("U+0066", {}) ; f
        +SC21::SendKey("U+0046", {}) ; F

         SC22::SendKey("U+0067", {"*^": "U+011d"}) ; g
        +SC22::SendKey("U+0047", {"*^": "U+011c"}) ; G

         SC23::SendKey("U+0068", {"*^": "U+0125", "*¨": "U+1e27"}) ; h
        +SC23::SendKey("U+0048", {"*^": "U+0124", "*¨": "U+1e26"}) ; H

         SC24::SendKey("U+006a", {"*^": "U+0135"}) ; j
        +SC24::SendKey("U+004a", {"*^": "U+0134"}) ; J

         SC25::SendKey("U+006b", {}) ; k
        +SC25::SendKey("U+004b", {}) ; K

         SC26::SendKey("U+006c", {}) ; l
        +SC26::SendKey("U+004c", {}) ; L

         SC27::SendKey("U+003b", {}) ; ;
        +SC27::SendKey("U+003a", {}) ; :

        ;  Letters, third row

         SC2c::SendKey("U+007a", {"*^": "U+1e91"}) ; z
        +SC2c::SendKey("U+005a", {"*^": "U+1e90"}) ; Z

         SC2d::SendKey("U+0078", {"*¨": "U+1e8d"}) ; x
        +SC2d::SendKey("U+0058", {"*¨": "U+1e8c"}) ; X

         SC2e::SendKey("U+0063", {"**": "U+00e7", "*^": "U+0109"}) ; c
        +SC2e::SendKey("U+0043", {"**": "U+00c7", "*^": "U+0108"}) ; C

         SC2f::SendKey("U+0076", {"*~": "U+1e7d"}) ; v
        +SC2f::SendKey("U+0056", {"*~": "U+1e7c"}) ; V

         SC30::SendKey("U+0062", {}) ; b
        +SC30::SendKey("U+0042", {}) ; B

         SC31::SendKey("U+006e", {"*``": "U+01f9", "*~": "U+00f1"}) ; n
        +SC31::SendKey("U+004e", {"*``": "U+01f8", "*~": "U+00d1"}) ; N

         SC32::SendKey("U+006d", {}) ; m
        +SC32::SendKey("U+004d", {}) ; M

         SC33::SendKey("U+002c", {}) ; ,
        +SC33::SendKey("U+003c", {"*~": "U+2272"}) ; <

         SC34::SendKey("U+002e", {"**": "U+2026"}) ; .
        +SC34::SendKey("U+003e", {"*~": "U+2273"}) ; >

         SC35::SendKey("U+002f", {}) ; /
        +SC35::SendKey("U+003f", {}) ; ?

        ;  Pinky keys

         SC0c::SendKey("U+002d", {"*^": "U+207b"}) ; -
        +SC0c::SendKey("U+005f", {}) ; _

         SC0d::SendKey("U+003d", {"*^": "U+207c", "*~": "U+2243"}) ; =
        +SC0d::SendKey("U+002b", {"*^": "U+207a"}) ; +

         SC1a::SendKey("U+005b", {}) ; [
        +SC1a::SendKey("U+007b", {}) ; {

         SC1b::SendKey("U+005d", {}) ; ]
        +SC1b::SendKey("U+007d", {}) ; }

         SC28::SendKey("**", {"**": "\'"})
        +SC28::SendKey("*¨", {"*¨": "¨"})

         SC29::SendKey("*``", {"*``": "`"}) ; *`
        +SC29::SendKey("*~", {"*~": "~"})

         SC2b::SendKey("U+005c", {}) ; \\
        +SC2b::SendKey("U+007c", {}) ; |

         SC56::SendKey("U+005c", {}) ; \\
        +SC56::SendKey("U+007c", {}) ; |

        ;  Space bar

         SC39::SendKey("U+0020", {"**": "U+0027", "*``": "U+0060", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  
        +SC39::SendKey("U+0020", {"**": "U+0027", "*``": "U+0060", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  

        """
    )

    assert len(ahk_keymap(layout, True)) == 12

    shortcuts = ahk_shortcuts(layout)
    assert len(shortcuts) == 90
    assert shortcuts == QWERTY_SHORTCUTS


def test_prog():
    layout = load_layout("prog")

    keymap = ahk_keymap(layout)
    assert len(keymap) == 156
    assert keymap == split(
        """
        ;  Digits

         SC02::SendKey("U+0031", {"*^": "U+00b9"}) ; 1
        +SC02::SendKey("U+0021", {}) ; !

         SC03::SendKey("U+0032", {"*^": "U+00b2"}) ; 2
        +SC03::SendKey("U+0040", {}) ; @

         SC04::SendKey("U+0033", {"*^": "U+00b3"}) ; 3
        +SC04::SendKey("U+0023", {}) ; #

         SC05::SendKey("U+0034", {"*^": "U+2074"}) ; 4
        +SC05::SendKey("U+0024", {}) ; $

         SC06::SendKey("U+0035", {"*^": "U+2075"}) ; 5
        +SC06::SendKey("U+0025", {}) ; %

         SC07::SendKey("U+0036", {"*^": "U+2076"}) ; 6
        +SC07::SendKey("U+005e", {}) ; ^

         SC08::SendKey("U+0037", {"*^": "U+2077"}) ; 7
        +SC08::SendKey("U+0026", {}) ; &

         SC09::SendKey("U+0038", {"*^": "U+2078"}) ; 8
        +SC09::SendKey("U+002a", {}) ; *

         SC0a::SendKey("U+0039", {"*^": "U+2079"}) ; 9
        +SC0a::SendKey("U+0028", {"*^": "U+207d"}) ; (

         SC0b::SendKey("U+0030", {"*^": "U+2070"}) ; 0
        +SC0b::SendKey("U+0029", {"*^": "U+207e"}) ; )

        ;  Letters, first row

         SC10::SendKey("U+0071", {}) ; q
        +SC10::SendKey("U+0051", {}) ; Q

         SC11::SendKey("U+0077", {"*``": "U+1e81", "*´": "U+1e83", "*^": "U+0175", "*¨": "U+1e85"}) ; w
        +SC11::SendKey("U+0057", {"*``": "U+1e80", "*´": "U+1e82", "*^": "U+0174", "*¨": "U+1e84"}) ; W

         SC12::SendKey("U+0065", {"*``": "U+00e8", "*´": "U+00e9", "*^": "U+00ea", "*~": "U+1ebd", "*¨": "U+00eb"}) ; e
        +SC12::SendKey("U+0045", {"*``": "U+00c8", "*´": "U+00c9", "*^": "U+00ca", "*~": "U+1ebc", "*¨": "U+00cb"}) ; E

         SC13::SendKey("U+0072", {"*´": "U+0155"}) ; r
        +SC13::SendKey("U+0052", {"*´": "U+0154"}) ; R

         SC14::SendKey("U+0074", {"*¨": "U+1e97"}) ; t
        +SC14::SendKey("U+0054", {}) ; T

         SC15::SendKey("U+0079", {"*``": "U+1ef3", "*´": "U+00fd", "*^": "U+0177", "*~": "U+1ef9", "*¨": "U+00ff"}) ; y
        +SC15::SendKey("U+0059", {"*``": "U+1ef2", "*´": "U+00dd", "*^": "U+0176", "*~": "U+1ef8", "*¨": "U+0178"}) ; Y

         SC16::SendKey("U+0075", {"*``": "U+00f9", "*´": "U+00fa", "*^": "U+00fb", "*~": "U+0169", "*¨": "U+00fc"}) ; u
        +SC16::SendKey("U+0055", {"*``": "U+00d9", "*´": "U+00da", "*^": "U+00db", "*~": "U+0168", "*¨": "U+00dc"}) ; U

         SC17::SendKey("U+0069", {"*``": "U+00ec", "*´": "U+00ed", "*^": "U+00ee", "*~": "U+0129", "*¨": "U+00ef"}) ; i
        +SC17::SendKey("U+0049", {"*``": "U+00cc", "*´": "U+00cd", "*^": "U+00ce", "*~": "U+0128", "*¨": "U+00cf"}) ; I

         SC18::SendKey("U+006f", {"*``": "U+00f2", "*´": "U+00f3", "*^": "U+00f4", "*~": "U+00f5", "*¨": "U+00f6"}) ; o
        +SC18::SendKey("U+004f", {"*``": "U+00d2", "*´": "U+00d3", "*^": "U+00d4", "*~": "U+00d5", "*¨": "U+00d6"}) ; O

         SC19::SendKey("U+0070", {"*´": "U+1e55"}) ; p
        +SC19::SendKey("U+0050", {"*´": "U+1e54"}) ; P

        ;  Letters, second row

         SC1e::SendKey("U+0061", {"*``": "U+00e0", "*´": "U+00e1", "*^": "U+00e2", "*~": "U+00e3", "*¨": "U+00e4"}) ; a
        +SC1e::SendKey("U+0041", {"*``": "U+00c0", "*´": "U+00c1", "*^": "U+00c2", "*~": "U+00c3", "*¨": "U+00c4"}) ; A

         SC1f::SendKey("U+0073", {"*´": "U+015b", "*^": "U+015d"}) ; s
        +SC1f::SendKey("U+0053", {"*´": "U+015a", "*^": "U+015c"}) ; S

         SC20::SendKey("U+0064", {}) ; d
        +SC20::SendKey("U+0044", {}) ; D

         SC21::SendKey("U+0066", {}) ; f
        +SC21::SendKey("U+0046", {}) ; F

         SC22::SendKey("U+0067", {"*´": "U+01f5", "*^": "U+011d"}) ; g
        +SC22::SendKey("U+0047", {"*´": "U+01f4", "*^": "U+011c"}) ; G

         SC23::SendKey("U+0068", {"*^": "U+0125", "*¨": "U+1e27"}) ; h
        +SC23::SendKey("U+0048", {"*^": "U+0124", "*¨": "U+1e26"}) ; H

         SC24::SendKey("U+006a", {"*^": "U+0135"}) ; j
        +SC24::SendKey("U+004a", {"*^": "U+0134"}) ; J

         SC25::SendKey("U+006b", {"*´": "U+1e31"}) ; k
        +SC25::SendKey("U+004b", {"*´": "U+1e30"}) ; K

         SC26::SendKey("U+006c", {"*´": "U+013a"}) ; l
        +SC26::SendKey("U+004c", {"*´": "U+0139"}) ; L

         SC27::SendKey("U+003b", {}) ; ;
        +SC27::SendKey("U+003a", {}) ; :

        ;  Letters, third row

         SC2c::SendKey("U+007a", {"*´": "U+017a", "*^": "U+1e91"}) ; z
        +SC2c::SendKey("U+005a", {"*´": "U+0179", "*^": "U+1e90"}) ; Z

         SC2d::SendKey("U+0078", {"*¨": "U+1e8d"}) ; x
        +SC2d::SendKey("U+0058", {"*¨": "U+1e8c"}) ; X

         SC2e::SendKey("U+0063", {"*´": "U+0107", "*^": "U+0109"}) ; c
        +SC2e::SendKey("U+0043", {"*´": "U+0106", "*^": "U+0108"}) ; C

         SC2f::SendKey("U+0076", {"*~": "U+1e7d"}) ; v
        +SC2f::SendKey("U+0056", {"*~": "U+1e7c"}) ; V

         SC30::SendKey("U+0062", {}) ; b
        +SC30::SendKey("U+0042", {}) ; B

         SC31::SendKey("U+006e", {"*``": "U+01f9", "*´": "U+0144", "*~": "U+00f1"}) ; n
        +SC31::SendKey("U+004e", {"*``": "U+01f8", "*´": "U+0143", "*~": "U+00d1"}) ; N

         SC32::SendKey("U+006d", {"*´": "U+1e3f"}) ; m
        +SC32::SendKey("U+004d", {"*´": "U+1e3e"}) ; M

         SC33::SendKey("U+002c", {}) ; ,
        +SC33::SendKey("U+003c", {"*~": "U+2272"}) ; <

         SC34::SendKey("U+002e", {}) ; .
        +SC34::SendKey("U+003e", {"*~": "U+2273"}) ; >

         SC35::SendKey("U+002f", {}) ; /
        +SC35::SendKey("U+003f", {}) ; ?

        ;  Pinky keys

         SC0c::SendKey("U+002d", {"*^": "U+207b"}) ; -
        +SC0c::SendKey("U+005f", {}) ; _

         SC0d::SendKey("U+003d", {"*^": "U+207c", "*~": "U+2243"}) ; =
        +SC0d::SendKey("U+002b", {"*^": "U+207a"}) ; +

         SC1a::SendKey("U+005b", {}) ; [
        +SC1a::SendKey("U+007b", {}) ; {

         SC1b::SendKey("U+005d", {}) ; ]
        +SC1b::SendKey("U+007d", {}) ; }

         SC28::SendKey("U+0027", {}) ; '
        +SC28::SendKey("U+0022", {}) ; "

         SC29::SendKey("U+0060", {}) ; `
        +SC29::SendKey("U+007e", {}) ; ~

         SC2b::SendKey("U+005c", {}) ; \\
        +SC2b::SendKey("U+007c", {}) ; |

        ;  Space bar

         SC39::SendKey("U+0020", {"*``": "U+0060", "*´": "U+0027", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  
        +SC39::SendKey("U+0020", {"*``": "U+0060", "*´": "U+0027", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  

        """
    )

    altgr = ahk_keymap(layout, True)
    assert len(altgr) == 98
    assert altgr == split(
        """
        ;  Digits

         <^>!SC02::SendKey("U+0021", {}) ; !

         <^>!SC03::SendKey("U+0028", {"*^": "U+207d"}) ; (

         <^>!SC04::SendKey("U+0029", {"*^": "U+207e"}) ; )

         <^>!SC05::SendKey("U+0027", {}) ; '

         <^>!SC06::SendKey("U+0022", {}) ; "

         <^>!SC07::SendKey("*^", {"*^": "^"})

         <^>!SC08::SendKey("U+0037", {"*^": "U+2077"}) ; 7

         <^>!SC09::SendKey("U+0038", {"*^": "U+2078"}) ; 8

         <^>!SC0a::SendKey("U+0039", {"*^": "U+2079"}) ; 9

         <^>!SC0b::SendKey("U+002f", {}) ; /

        ;  Letters, first row

         <^>!SC10::SendKey("U+003d", {"*^": "U+207c", "*~": "U+2243"}) ; =

         <^>!SC11::SendKey("U+003c", {"*~": "U+2272"}) ; <
        <^>!+SC11::SendKey("U+2264", {}) ; ≤

         <^>!SC12::SendKey("U+003e", {"*~": "U+2273"}) ; >
        <^>!+SC12::SendKey("U+2265", {}) ; ≥

         <^>!SC13::SendKey("U+002d", {"*^": "U+207b"}) ; -

         <^>!SC14::SendKey("U+002b", {"*^": "U+207a"}) ; +

         <^>!SC16::SendKey("U+0034", {"*^": "U+2074"}) ; 4

         <^>!SC17::SendKey("U+0035", {"*^": "U+2075"}) ; 5

         <^>!SC18::SendKey("U+0036", {"*^": "U+2076"}) ; 6

         <^>!SC19::SendKey("U+002a", {}) ; *

        ;  Letters, second row

         <^>!SC1e::SendKey("U+007b", {}) ; {

         <^>!SC1f::SendKey("U+005b", {}) ; [

         <^>!SC20::SendKey("U+005d", {}) ; ]

         <^>!SC21::SendKey("U+007d", {}) ; }

         <^>!SC22::SendKey("U+002f", {}) ; /

         <^>!SC24::SendKey("U+0031", {"*^": "U+00b9"}) ; 1

         <^>!SC25::SendKey("U+0032", {"*^": "U+00b2"}) ; 2

         <^>!SC26::SendKey("U+0033", {"*^": "U+00b3"}) ; 3

         <^>!SC27::SendKey("U+002d", {"*^": "U+207b"}) ; -

        ;  Letters, third row

         <^>!SC2c::SendKey("U+007e", {}) ; ~

         <^>!SC2d::SendKey("U+0060", {}) ; `

         <^>!SC2e::SendKey("U+007c", {}) ; |
        <^>!+SC2e::SendKey("U+00a6", {}) ; ¦

         <^>!SC2f::SendKey("U+005f", {}) ; _

         <^>!SC30::SendKey("U+005c", {}) ; \\

         <^>!SC32::SendKey("U+0030", {"*^": "U+2070"}) ; 0

         <^>!SC33::SendKey("U+002c", {}) ; ,

         <^>!SC34::SendKey("U+002e", {}) ; .

         <^>!SC35::SendKey("U+002b", {"*^": "U+207a"}) ; +

        ;  Pinky keys

         <^>!SC28::SendKey("*´", {"*´": "´"})
        <^>!+SC28::SendKey("*¨", {"*¨": "¨"})

         <^>!SC29::SendKey("*``", {"*``": "`"}) ; *`
        <^>!+SC29::SendKey("*~", {"*~": "~"})

        ;  Space bar

         <^>!SC39::SendKey("U+0020", {"*``": "U+0060", "*´": "U+0027", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  
        <^>!+SC39::SendKey("U+0020", {"*``": "U+0060", "*´": "U+0027", "*^": "U+005e", "*~": "U+007e", "*¨": "U+0022"}) ;  

        """
    )

    shortcuts = ahk_shortcuts(layout)
    assert len(shortcuts) == 90
    assert shortcuts == QWERTY_SHORTCUTS
