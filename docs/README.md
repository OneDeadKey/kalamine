# Sample Layouts

## Qwerty-ANSI

The standard Qwerty-US layout.

## Qwerty-intl

Same layout, but ``'"^`~`` are turned into dead keys:

- `"`, `a` = ä
- `'`, `e` = è

Notice that in the YAML description, these ``'"^`~`` signs are turned into their combining diacritics equivalent:

- `´` → `space` + `U+301` (combining acute)
- `~` → `space` + `U+303` (combining tilde)

## Qwerty-prog

A qwerty-intl variant with an AltGr layer for dead diacritics and coding symbols.

- `AltGr`+`a` = {
- `AltGr`+`s` = [
- `AltGr`+`d` = ]
- `AltGr`+`f` = }
- `AltGr`+`"`, `a` = ä
- `AltGr`+`'`, `e` = è

## See Also…

- [“One Dead Key”](https://github.com/fabi1cazenave/1dk)
- [Qwerty-Lafayette](https://github.com/fabi1cazenave/qwerty-lafayette)
