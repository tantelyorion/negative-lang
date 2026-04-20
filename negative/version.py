"""
Version information for Negative Language
"""

__version__ = "1.1.0"
__version_info__ = (1, 1, 0)

def get_version() -> str:
    """Return the version string."""
    return __version__

def get_version_info() -> tuple:
    """Return the version as a tuple."""
    return __version_info__