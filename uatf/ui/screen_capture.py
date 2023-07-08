from dataclasses import dataclass


@dataclass
class DrawableType:
    text: str = 'default'
    is_highlighted: bool = True

def make_screen_for_gif(driver, element, type_of_action, data):
    pass
