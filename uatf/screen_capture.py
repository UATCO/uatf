from dataclasses import dataclass


@dataclass
class DrawableType:
    text: str = 'default'
    is_highlighted: bool = True
