"""Strawberry Timer Size Presets.

Choose the right size based on your needs:
- TINY (20×15) - Minimal, hard to read, best for background
- SMALL (30×22) - Better readability, good compromise
- MEDIUM (40×30) - Easy to read and interact, recommended
- LARGE (50×38) - Very readable, more prominent
"""

from enum import Enum
from dataclasses import dataclass


class TimerSize(Enum):
    """Timer size presets."""
    TINY = "tiny"      # 20×15 - Very small, hard to read
    SMALL = "small"    # 30×22 - Better readability
    MEDIUM = "medium"  # 40×30 - Recommended (easy to read + minimal)
    LARGE = "large"    # 50×38 - Very readable, more prominent


@dataclass
class SizeConfig:
    """Configuration for a specific timer size."""
    width: int
    height: int
    font_size: int
    padding: int
    corner_radius: int
    description: str


# Size presets
SIZE_PRESETS = {
    TimerSize.TINY: SizeConfig(
        width=20,
        height=15,
        font_size=6,
        padding=1,
        corner_radius=2,
        description="Tiny - Minimal footprint, hard to read on high-DPI displays"
    ),
    TimerSize.SMALL: SizeConfig(
        width=30,
        height=22,
        font_size=10,
        padding=2,
        corner_radius=3,
        description="Small - Better readability, minimal space"
    ),
    TimerSize.MEDIUM: SizeConfig(
        width=40,
        height=30,
        font_size=14,
        padding=3,
        corner_radius=4,
        description="Medium - Recommended, easy to read + small footprint"
    ),
    TimerSize.LARGE: SizeConfig(
        width=50,
        height=38,
        font_size=18,
        padding=4,
        corner_radius=5,
        description="Large - Very readable, more prominent on desktop"
    ),
}


def get_config(size: TimerSize = TimerSize.MEDIUM) -> SizeConfig:
    """Get size configuration.

    Args:
        size: TimerSize enum value.

    Returns:
        SizeConfig with dimensions and styling.
    """
    return SIZE_PRESETS[size]


def get_recommended_size() -> TimerSize:
    """Get recommended size based on typical use case.

    Returns:
        TimerSize.MEDIUM as the recommended default.
    """
    return TimerSize.MEDIUM


# Quick reference for users
if __name__ == "__main__":
    print("🍓 Strawberry Timer Size Options:")
    print("=" * 50)
    for size, config in SIZE_PRESETS.items():
        print(f"\n{size.value.upper()}: {config.width}×{config.height}px")
        print(f"  Font: {config.font_size}px")
        print(f"  {config.description}")
    print("\n" + "=" * 50)
    print(f"\n✓ Recommended: {get_recommended_size().value.upper()} ({SIZE_PRESETS[get_recommended_size()].width}×{SIZE_PRESETS[get_recommended_size()].height}px)")
