from dataclasses import dataclass
from enum import Enum, Flag, auto, unique
from typing import Any, Dict, Optional, Self

from kalamine.utils import load_data


@unique
class Hand(Enum):
    Left = auto()
    Right = auto()

    @classmethod
    def parse(cls, raw: str) -> Self:
        for h in cls:
            if h.name.casefold() == raw.casefold():
                return h
        else:
            raise ValueError(f"Cannot parse hand: “{raw}”")


@unique
class KeyCategory(Flag):
    Digits = auto()
    Letters1 = auto()
    Letters2 = auto()
    Letters3 = auto()
    PinkyKeys = auto()
    SpaceBar = auto()
    System = auto()
    Modifiers = auto()
    InputMethod = auto()
    Miscellaneous = auto()
    AlphaNum = Digits | Letters1 | Letters2 | Letters3 | PinkyKeys | SpaceBar

    @classmethod
    def parse(cls, raw: str) -> Self:
        for kc in cls:
            if kc.name.casefold() == raw.casefold():
                return kc
        else:
            raise ValueError(f"Cannot parse key category: “{raw}”")

    @property
    def description(self) -> str:
        match self:
            case KeyCategory.Digits:
                return "Digits"
            case KeyCategory.Letters1:
                return "Letters, first row"
            case KeyCategory.Letters2:
                return "Letters, second row"
            case KeyCategory.Letters3:
                return "Letters, third row"
            case KeyCategory.PinkyKeys:
                return "Pinky keys"
            case KeyCategory.SpaceBar:
                return "Space bar"
            case KeyCategory.System:
                return "System"
            case KeyCategory.Modifiers:
                return "Modifiers"
            case KeyCategory.InputMethod:
                return "Input method"
            case KeyCategory.Miscellaneous:
                return "Miscellaneous"
            case _:
                raise ValueError(f"No description ofr KeyCategory: {self}")


@dataclass
class Key:
    xkb: str
    web: Optional[str] = None
    windows: Optional[str] = None
    macos: Optional[str] = None
    hand: Optional[Hand] = None
    category: KeyCategory = KeyCategory.Miscellaneous
    "Usual hand on standard (ISO, etc.) keyboard"

    @classmethod
    def load_data(cls, data: Dict[str, Any]) -> Dict[str, Self]:
        return {
            key.xkb: key
            for category, keys in data.items()
            for key in (cls.parse(category=category, **entry) for entry in keys)
        }

    @classmethod
    def parse(cls, category: str, xkb: str, web: Optional[str], windows: Optional[str], macos: Optional[str], hand: Optional[str]) -> Self:
        return cls(
            category=KeyCategory.parse(category),
            xkb=xkb,
            web=web,
            windows=windows,
            macos=macos,
            hand=Hand.parse(hand) if hand else None
        )

    @property
    def id(self) -> str:
        return self.xkb

    @property
    def alphanum(self) -> bool:
        return bool(self.category & KeyCategory.AlphaNum)

KEYS = Key.load_data(load_data("scan_codes"))
