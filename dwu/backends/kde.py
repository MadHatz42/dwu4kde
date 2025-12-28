import subprocess
import shutil
import os
from dwu.backends.base import WallpaperBackend

class KdeBackend(WallpaperBackend):
    name = "kde"

    def is_available(self) -> bool:
        # Prefer plasma-apply-wallpaperimage (recommended for Plasma 6)
        # Fallback to qdbus method for older Plasma versions
        return (shutil.which("plasma-apply-wallpaperimage") is not None or
                shutil.which("qdbus") is not None or 
                shutil.which("qdbus-qt6") is not None)

    def set_wallpaper(self, path: str) -> None:
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Verify file exists
        if not os.path.exists(abs_path):
            raise RuntimeError(f"Wallpaper file does not exist: {abs_path}")
        
        # Method 1: Use plasma-apply-wallpaperimage (recommended for Plasma 6)
        plasma_apply = shutil.which("plasma-apply-wallpaperimage")
        if plasma_apply:
            try:
                # Run without capturing output to avoid potential issues with Plasma 6
                # This ensures the command can interact properly with the desktop session
                subprocess.run(
                    [plasma_apply, abs_path],
                    check=True,
                    env=os.environ.copy()
                )
                return
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"plasma-apply-wallpaperimage failed (exit code {e.returncode})"
                )
        
        # Method 2: Fallback to qdbus method (for older Plasma versions)
        # This JS script runs inside Plasmashell to update all monitors
        script = f"""
        const allDesktops = desktops();
        for (let i = 0; i < allDesktops.length; i++) {{
            const d = allDesktops[i];
            d.wallpaperPlugin = "org.kde.image";
            d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
            d.writeConfig("Image", "file://{abs_path}");
        }}
        """
        
        # Find the correct qdbus executable
        qdbus = shutil.which("qdbus") or shutil.which("qdbus-qt6") or shutil.which("qdbus-qt5")
        
        if qdbus:
            try:
                subprocess.run([
                    qdbus, "org.kde.plasmashell", "/PlasmaShell",
                    "org.kde.PlasmaShell.evaluateScript", script
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"qdbus method failed: {e.stderr or e.stdout or str(e)}"
                )
        else:
            raise RuntimeError(
                "Could not find plasma-apply-wallpaperimage or qdbus executable"
            )

    def get_current_wallpaper(self) -> str | None:
        # We return None to force an update every time
        return None