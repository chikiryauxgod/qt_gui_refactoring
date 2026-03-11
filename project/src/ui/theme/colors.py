from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    main_background: str
    group_border: str
    group_title_padding: str


LIGHT_PALETTE = ColorPalette(
    main_background="#f0f0f0",
    group_border="#cccccc",
    group_title_padding="#000000",  
)