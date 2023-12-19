Defining a Keyboard Layout
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
┃ ↹      ┃   @ │   < │   > │   $ │   % │   ^ │   & │   * │   ' │   ` │ [   │ ]   │ \     │
┣━━━━━━━━┻┱────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┬────┴┲━━━━┷━━━━━━━┪
┃         ┃ A   │ S   │ D   │ F   │ G   │ H   │ J   │ K   │ L   │ :   │ "*¨ ┃            ┃
┃ ⇬       ┃   { │   ( │   ) │   } │   = │   \ │   + │   - │   / │ ; " │ '*´ ┃ ⏎          ┃
┣━━━━━━━━━┻━━┱──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┲━━┻━━━━━━━━━━━━┫
┃            ┃ Z   │ X   │ C   │ V   │ B   │ N   │ M   │ <   │ >   │ ?   ┃               ┃
┃ ⇧          ┃   ~ │   [ │   ] │   _ │   # │   | │   ! │ , ; │ . : │ / ? ┃ ⇧             ┃
┣━━━━━━━┳━━━━┻━━┳━━┷━━━━┱┴─────┴─────┴─────┴─────┴─────┴─┲━━━┷━━━┳━┷━━━━━╋━━━━━━━┳━━━━━━━┫
┃       ┃       ┃       ┃                                ┃       ┃       ┃       ┃       ┃
┃ Ctrl  ┃ super ┃ Alt   ┃ ␣                              ┃ AltGr ┃ super ┃ menu  ┃ Ctrl  ┃
┗━━━━━━━┻━━━━━━━┻━━━━━━━┹────────────────────────────────┺━━━━━━━┻━━━━━━━┻━━━━━━━┻━━━━━━━┛
'''
```


Layers
--------------------------------------------------------------------------------

### base

The `base` layer contains the base and shifted keys:

                   +-----+
    shift -------> | ?   |
    base --------> | /   |
                   +-----+

When the base and shift keys correspond to the same character, you may only
specify the uppercase char:

                   +-----+
    shift -------> | A   |
    (base = a) --> |     |
                   +-----+

### altgr

The `altgr` layer contains the altgr and shift+altgr symbols:

                   +-----+
                   |     | <----- (altgr+shift+key is undefined)
                   |   { | <----- altgr+key = {
                   +-----+

### full

The `full` view lets you specify the `base` and `altgr` levels together:

                   +-----+
    shift -------> | A   | <----- (altgr+shift+key is undefined)
    (base = a) --> |   { | <----- altgr+key = {
                   +-----+


Dead Keys
--------------------------------------------------------------------------------

### Usage

Dead keys are preceded by a `*` sign. They can be used in the `base` layer:

                   +-----+
    shift -------> |*"   |  = dead diaeresis
    base --------> |*'   |  = dead acute accent
                   +-----+

… as well as in the `altgr` layer:

                   +-----+
    shift = " ---> | "*" | <----- altgr+shift+key = dead diaeresis
    base = ' ----> | '*' | <----- altgt+key       = dead acute accent
                   +-----+

### Standard Dead Keys

The following dead keys are supported, and their behavior cannot be customized:

    id  XKB name          base/accented chars

    *`  grave             AAAaEeIiNnOoUuWwYyЕеИи
                       -> ÀÀÀàÈèÌìǸǹÒòÙùẀẁỲỳЀѐЍѝ
    *‟  doublegrave       AAAaEeIiOoRrUuѴѴ
                       -> ȀȀȀȁȄȅȈȉȌȍȐȑȔȕѶѷ
    *´  acute             AAAaCcEeGgIiKkLlMmNnOoPpRrSsUuWwYyZzΑαΕεΗηΙιΟοΥυΩωГгКк
                       -> ÁÁÁáĆćÉéǴǵÍíḰḱĹĺḾḿŃńÓóṔṕŔŕŚśÚúẂẃÝýŹźΆάΈέΉήΊίΌόΎύΏώЃѓЌќ
    *”  doubleacute       OOOoUuУу
                       -> ŐŐŐőŰűӲӳ
    *^  circumflex        AAAaCcEeGgHhIiJjOoSsUuWwYyZz0123456789()+-=
                       -> ÂÂÂâĈĉÊêĜĝĤĥÎîĴĵÔôŜŝÛûŴŵŶŷẐẑ⁰¹²³⁴⁵⁶⁷⁸⁹⁽⁾⁺⁻⁼
    *ˇ  caron             AAAaCcDdEeGgHhIiKkLlNnOoRrSsTtUuZzƷʒ0123456789()+-=
                       -> ǍǍǍǎČčĎďĚěǦǧȞȟǏǐǨǩĽľŇňǑǒŘřŠšŤťǓǔŽžǮǯ₀₁₂₃₄₅₆₇₈₉₍₎₊₋₌
    *˘  breve             AAAaEeGgIiOoUuΑαΙιΥυАаЕеЖжИиУу
                       -> ĂĂĂăĔĕĞğĬĭŎŏŬŭᾸᾰῘῐῨῠӐӑӖӗӁӂЙйЎў
    *⁻  invertedbreve     AAAaEeIiOoUuRr
                       -> ȂȂȂȃȆȇȊȋȎȏȖȗȒȓ
    *~  tilde             AAAaEeIiNnOoUuVvYy<>=
                       -> ÃÃÃãẼẽĨĩÑñÕõŨũṼṽỸỹ≲≳≃
    *¯  macron            AAAaÆæEeGgIiOoUuYy
                       -> ĀĀĀāǢǣĒēḠḡĪīŌōŪūȲȳ
    *¨  diaeresis         AAAaEeHhIiOotUuWwXxYyΙιΥυАаЕеӘәЖжЗзИиІіОоӨөУуЧчЫыЭэ
                       -> ÄÄÄäËëḦḧÏïÖöẗÜüẄẅẌẍŸÿΪϊΫϋӒӓЁёӚӛӜӝӞӟӤӥЇїӦӧӪӫӰӱӴӵӸӹӬӭ
    *˚  abovering         AAAaUuwy
                       -> ÅÅÅåŮůẘẙ
    *¸  cedilla           CCCcDdEeGgHhKkLlNnRrSsTt
                       -> ÇÇÇçḐḑȨȩĢģḨḩĶķĻļŅņŖŗŞşŢţ
    *,  belowcomma        SSSsTt
                       -> ȘȘȘșȚț
    *˛  ogonek            AAAaEeIiOoUu
                       -> ĄĄĄąĘęĮįǪǫŲų
    */  stroke            AAAaBbCcDdEeGgHhIiJjLlOoPpRrTtUuYyZz<≤≥>=
                       -> ȺȺȺⱥɃƀȻȼĐđɆɇǤǥĦħƗɨɈɉŁłØøⱣᵽɌɍŦŧɄʉɎɏƵƶ≮≰≱≯≠
    *˙  abovedot          AAAaBbCcDdEeFfGgHhIijLlMmNnOoPpRrSsTtWwXxYyZz
                       -> ȦȦȦȧḂḃĊċḊḋĖėḞḟĠġḢḣİıȷĿŀṀṁṄṅȮȯṖṗṘṙṠṡṪṫẆẇẊẋẎẏŻż
    *.  belowdot          AAAaBbDdEeHhIiKkLlMmNnOoRrSsTtUuVvWwYyZz
                       -> ẠẠẠạḄḅḌḍẸẹḤḥỊịḲḳḶḷṂṃṆṇỌọṚṛṢṣṬṭỤụṾṿẈẉỴỵẒẓ
    *µ  greek             AAAaBbDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuWwXxYyZz
                       -> ΑΑΑαΒβΔδΕεΦφΓγΗηΙιΘθΚκΛλΜμΝνΟοΠπΧχΡρΣσΤτΥυΩωΞξΨψΖζ
    *¤  currency          AAAaBbÇCçcDdEeFfGgHhIiKkLlMmNnOoPpRrSsTtþÞUuWwYy
                       -> ₳₳₳؋₱฿₵₡₵¢₯₫₠€₣ƒ₲₲₴₴៛﷼₭₭₤£ℳ₥₦₦૱௹₧₰₨₢$₪₮৳৲৲圓元₩₩円¥

### Custom Dead Key

There is one dead key (1dk), noted `**`, that can be customized by specifying
how it modifies each character in the `base` layer:

                   +-----+
    shift -------> | ? ¿ | <----- 1dk, shift+key
    base --------> | / ÷ | <----- 1dk, key
                   +-----+

When the base and shift keys correspond to the same accented character, you may
only specify the lowercase accented char in the `base` layer:

                   +-----+
    shift -------> | A   | <----- (1dk, shift+key = À)
    (base = a) --> |   à | <----- 1dk, key = à
                   +-----+

You may also chain dead keys by specifying a dead key in the `1dk` layer:

                   +-----+
    shift -------> | G   |
    (base = g) --> |  *µ | <----- 1dk, key = dead Greek
                   +-----+

**Warning:** chained dead keys are not supported by MSKLC, and KbdEdit will be
required to build a Windows driver for such a keyboard layout.


Space Bar
--------------------------------------------------------------------------------

Kalamine descriptor files have an optional section to define specific behaviors
of the space bar in non-base layers:

    [spacebar]
    shift       = "\u202f"  # NARROW NO-BREAK SPACE
    altgr       = "\u0020"  # SPACE
    altgr_shift = "\u00a0"  # NO-BREAK SPACE
    1dk         = "\u2019"  # RIGHT SINGLE QUOTATION MARK
    1dk_shift   = "\u2019"  # RIGHT SINGLE QUOTATION MARK

Kalamine doesn’t support non-space chars on the `base` layer for the space bar.
Space characters outside of the space bar are not supported either.
