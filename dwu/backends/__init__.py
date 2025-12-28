from dwu.backends.kde import KdeBackend
from dwu.backends.base import WallpaperBackend

def get_backend(display_server: str) -> WallpaperBackend | None:
    # We force it to use your KDE backend regardless of Wayland/X11
    backend = KdeBackend()
    if backend.is_available():
        return backend
    
    raise RuntimeError("KDE wallpaper utility (plasma-apply-wallpaperimage) not found!")