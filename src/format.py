"""
This module contains functions for formatting text output.
"""


def _gradient_text(text: str, start_hex: str, end_hex: str,
                   bold: bool = True) -> str:
    """
    Return a string with the text colored with a gradient.
    """
    result = ""
    start_hex = start_hex.lstrip('#')
    end_hex = end_hex.lstrip('#')
    start_r, start_g, start_b = (int(start_hex[i:i+2], 16) for i in (0, 2, 4))
    end_r, end_g, end_b = (int(end_hex[i:i+2], 16) for i in (0, 2, 4))
    for i, char in enumerate(text):
        progress = i / (len(text) - 1) if len(text) > 1 else 0
        r = int(start_r + (end_r - start_r) * progress)
        g = int(start_g + (end_g - start_g) * progress)
        b = int(start_b + (end_b - start_b) * progress)
        result += f"\033[{('1;' if bold else '')}38;2;{r};{g};{b}m{char}"
    return result + "\033[0m"


def print_gradient(text: str, gradient: str = "light_gray",
                   line_break: bool = True) -> None:
    """
    Print the text with a gradient color.
    """
    gradients = {
        "red_magenta": ("#FF2828", "#FF28FF"),
        "cyan_blue": ("#28FFFF", "#2828FF"),
        "green_lime": ("#28FF28", "#28FFB4"),
        "yellow_orange": ("#FFFF28", "#FFB428"),
        "light_gray": ("#FAFAFA", "#E1EAEE"),
        "pink_purple": ("#FF28FF", "#B428FF")
    }
    start_hex, end_hex = gradients.get(gradient, gradients["light_gray"])
    print(_gradient_text(text, start_hex, end_hex,
                         bold=gradient != "light_gray"),
          end='\n' if line_break else '')


def box_print(text: str) -> str:
    """
    Return a string with the text in a box.
    """
    lines = text.split('\n')
    width = max(len(line) for line in lines)
    box = f"╭{'─' * (width + 2)}╮\n"
    for line in lines:
        box += f"│ {line:<{width}} │\n"
    box += f"╰{'─' * (width + 2)}╯"
    return box
