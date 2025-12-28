from __future__ import annotations
import os
import subprocess
import re
from urllib.parse import urlparse
import click
from dwu.wallresult import WallResult

def get_cache_dir() -> str:
    cache_dir = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    path = os.path.join(cache_dir, "dwu")
    os.makedirs(path, exist_ok=True)
    return path

def infer_extension(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in ("jpg", "jpeg", "png"):
        if path.endswith("." + ext):
            return ext
    return "png"

def detect_display_server() -> str:
    if os.environ.get('WAYLAND_DISPLAY'):
        return 'wayland'
    elif os.environ.get('DISPLAY'):
        return 'x11'
    return 'unknown'
    
def get_display_resolution() -> tuple[int, int]:
    """Dynamically fetches resolution using KDE's kscreen-doctor."""
    try:
        result = subprocess.run(
            ["kscreen-doctor", "-o"],
            capture_output=True,
            text=True,
            check=True
        )
        # Looks for pattern like 1800x1125@
        match = re.search(r"(\d+)x(\d+)@", result.stdout)
        if match:
            return (int(match.group(1)), int(match.group(2)))
    except Exception:
        pass
    # Fallback default
    return (1920, 1080)

def print_wall_feedback(result: WallResult) -> None:
    match result:
        case WallResult.TODAY:
            click.echo("Updated to today's wallpaper!")
        case WallResult.MOST_RECENT:
            click.echo("Updated to most recent unskipped wallpaper!")
        case WallResult.ALREADY_SET:
            click.echo("Already using this wallpaper.")
        case WallResult.SET:
            click.echo("Wallpaper set successfully!")
        case WallResult.NO_VALID:
            click.echo("No valid wallpapers available.")