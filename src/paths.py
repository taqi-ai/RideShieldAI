"""Where the app finds its files.

Running from source nothing changes: everything lives in the repository folder. In the packaged Windows
build the models, images and stylesheet are read from the bundle next to the .exe, while the database and
alert snapshots are written to the user's data folder (%APPDATA%\\RideShieldAI), because the folder the
.exe sits in may be read-only and should not collect personal data.
"""
import os
import sys

FROZEN = getattr(sys, "frozen", False)
_SRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def bundle_root() -> str:
    """Folder holding the read-only files (models, assets)."""
    if FROZEN:
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return _SRC_ROOT


def user_root() -> str:
    """Folder the app may write to (database, snapshots). RIDESHIELD_HOME overrides it (used for testing)."""
    override = os.environ.get("RIDESHIELD_HOME")
    if override:
        return override
    if FROZEN:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "RideShieldAI")
    return _SRC_ROOT


def resource(*parts: str) -> str:
    return os.path.join(bundle_root(), *parts)


def user_file(*parts: str) -> str:
    return os.path.join(user_root(), *parts)
