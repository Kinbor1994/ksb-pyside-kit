"""Module containing all application constants.

This module centralizes all constant values used across the application.
"""

from typing import Dict, Any
from pathlib import Path

# Application Information
APP_NAME: str = "Fortis School Management System"
APP_DESCRIPTION: str = "A comprehensive school management system."
APP_VERSION: str = "1.0.0"

LOGO: str = "FSMS"
COLLAPSED_LOGO: str = "FS"

# File Paths
ASSETS_DIR: Path = Path(__file__).parent.parent / "assets"

ICONS_DIR: Path = ASSETS_DIR / "icons"
FONT_DIR: Path = ASSETS_DIR / "fonts"
IMAGES_DIR: Path = ASSETS_DIR / "images"


UI_CONSTANTS: Dict[str, int] = {
    "SIDEBAR_WIDTH": 250,
    "COLLAPSED_SIDEBAR_WIDTH": 60,
    "HEADER_HEIGHT": 40,
    "FOOTER_HEIGHT": 20
}
