"""Where the reverse-engineering tools read and write, and where CS2 is installed.

Everything the tools write lives in this repository: the scripts here and in
tools/ghidra_scripts, the name lists, and (gitignored) the copies of Valve's
DLL builds, patch_check's state and reports, and tool output. The third-party
installs stay outside it, each found from an environment variable:

    CS2_DIR          the Counter-Strike 2 install (the folder holding game/);
                     unset, it is found through Steam (cs2_dir below)
    S2C_BINARIES     the archived DLL builds (default tools/re/binaries)
    S2C_GHIDRA_ROOT  Ghidra, its project databases and the pyghidra / ReVa venv
                     (default .tools/ in this clone, gitignored)
    GHIDRA_INSTALL_DIR  Ghidra itself (default S2C_GHIDRA_ROOT/ghidra_12.1.3_PUBLIC)
"""
import os
import re
import sys

RE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(RE))

# Copies of each analysed DLL build, <dll>_<yyyymmdd>.dll (gitignored).
BINARIES = os.environ.get("S2C_BINARIES", os.path.join(RE, "binaries"))
# Builds imported into Ghidra under their original names.
STAGING = os.path.join(BINARIES, "staging")
NAMES = os.path.join(RE, "names")
PATCH_STATE = os.path.join(RE, "patch_state")
PATCH_REPORTS = os.path.join(RE, "patch_reports")
# Tool output: logs, decompile dumps (gitignored).
OUT = os.path.join(RE, "out")
DUMPS = os.path.join(OUT, "dumps")
REVA_CALL = os.path.join(RE, "reva_call.py")
GHIDRA_SCRIPTS = os.path.join(REPO, "tools", "ghidra_scripts")

GHIDRA_ROOT = os.environ.get("S2C_GHIDRA_ROOT", os.path.join(REPO, ".tools"))
GHIDRA_INSTALL = os.environ.get("GHIDRA_INSTALL_DIR", os.path.join(GHIDRA_ROOT, "ghidra_12.1.3_PUBLIC"))
GHIDRA_PROJECTS = os.path.join(GHIDRA_ROOT, "ghidra_projects")
REVA_PYTHON = os.path.join(GHIDRA_ROOT, "reva-venv", "Scripts" if os.name == "nt" else "bin",
                           "python.exe" if os.name == "nt" else "python")

CS2_APPID = "730"
CS2_FOLDER = "Counter-Strike Global Offensive"


def _steam_roots():
    """Steam's install folders: the registry's on Windows, the usual ones elsewhere."""
    roots = []
    if os.name == "nt":
        try:
            import winreg
            for hive, key, value in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                                     (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath")):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        roots.append(winreg.QueryValueEx(k, value)[0])
                except OSError:
                    pass
        except ImportError:
            pass
        roots.append(os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Steam"))
    else:
        home = os.path.expanduser("~")
        roots += [os.path.join(home, ".steam", "steam"), os.path.join(home, ".local", "share", "Steam")]
    return roots


def _libraries(root):
    """Every Steam library a root's libraryfolders.vdf lists that holds CS2, the root itself first."""
    libs = [root]
    vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
    try:
        with open(vdf, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return libs
    # each library block: "path" "<folder>" ... "apps" { "730" "<size>" ... }
    for m in re.finditer(r'"path"\s+"([^"]+)"(.*?)(?="path"|\Z)', text, re.S):
        if re.search(r'"%s"\s+"' % CS2_APPID, m.group(2)):
            libs.insert(0, m.group(1).replace("\\\\", "\\"))
        else:
            libs.append(m.group(1).replace("\\\\", "\\"))
    return libs


def cs2_dir(required=True):
    """The CS2 install (the folder that holds game/): CS2_DIR, else the Steam library that has app 730.
    Not found: exits with what to set, or returns None when not required."""
    env = os.environ.get("CS2_DIR")
    if env:
        return env
    seen = set()
    for root in _steam_roots():
        for lib in _libraries(root):
            p = os.path.normpath(os.path.join(lib, "steamapps", "common", CS2_FOLDER))
            if p not in seen and os.path.isdir(os.path.join(p, "game")):
                return p
            seen.add(p)
    if not required:
        return None
    sys.exit("CS2 not found: set CS2_DIR to the Counter-Strike 2 install (the folder that holds game/)")


def binary(name):
    """A DLL by file name (resourcecompiler_20260923.dll) or alias (rc), else the path as given."""
    name = ALIASES.get(name, name)
    for d in (BINARIES, STAGING):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return name


# Short names for the builds most read, as ReVa programs and as files.
ALIASES = {
    "rc": "resourcecompiler_20260923.dll",
    "vis": "visbuilder_20260923.dll",
    "ms": "meshsystem_20260923.dll",
    "ms1001": "meshsystem_20261001.dll",
    "pb": "physicsbuilder_20260924.dll",
    "pv": "vphysics2_20260924.dll",
    "sp": "smartprops_20260923.dll",
    "t0": "tier0_20260923.dll",
    "vrad3": "vrad3_20261001.dll",
    "ss": "scenesystem_20261015.dll",
    "mat": "materialsystem2_20261015.dll",
    "mt": "modtools_20261015.dll",
    "navs": "navsystem_20261015.dll",
    "srv": "server_20261015.dll",
    "cl": "client_20261015.dll",
    "wr": "worldrenderer_20261023.dll",
    "ss1023": "scenesystem_20261023.dll",
    "sa": "steamaudio_20261023.dll",
    "ph": "phonon_20260923.dll",
}
