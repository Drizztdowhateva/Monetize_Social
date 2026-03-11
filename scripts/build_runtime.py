from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist_runtime"
BUILD = ROOT / "build_runtime"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=ROOT)


def pyinstaller_build(name: str = "MonetizeSocial") -> Path:
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--windowed",
            "--onedir",
            "--name",
            name,
            "src/monetize_social/gui.py",
            "--distpath",
            str(DIST),
            "--workpath",
            str(BUILD),
            "--specpath",
            str(BUILD),
        ]
    )
    return DIST / name


def build_appimage(app_dir: Path) -> None:
    appimagetool = shutil.which("appimagetool")
    if not appimagetool:
        raise RuntimeError("appimagetool not found. Install AppImage tooling and retry.")

    appdir = BUILD / "MonetizeSocial.AppDir"
    if appdir.exists():
        shutil.rmtree(appdir)

    (appdir / "usr/bin").mkdir(parents=True, exist_ok=True)
    (appdir / "usr/share/applications").mkdir(parents=True, exist_ok=True)

    shutil.copytree(app_dir, appdir / "usr/bin/MonetizeSocial", dirs_exist_ok=True)

    app_run = appdir / "AppRun"
    app_run.write_text(
        "#!/bin/sh\n"
        "HERE=\"$(dirname \"$(readlink -f \"$0\")\")\"\n"
        "exec \"$HERE/usr/bin/MonetizeSocial/MonetizeSocial\"\n",
        encoding="utf-8",
    )
    app_run.chmod(0o755)

    desktop = appdir / "usr/share/applications/monetizesocial.desktop"
    desktop.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=MonetizeSocial\n"
        "Exec=MonetizeSocial\n"
        "Categories=Office;\n",
        encoding="utf-8",
    )

    out = DIST / "MonetizeSocial-x86_64.AppImage"
    run([appimagetool, str(appdir), str(out)])


def build_dmg(app_dir: Path) -> None:
    create_dmg = shutil.which("create-dmg")
    if not create_dmg:
        raise RuntimeError("create-dmg not found. Install it on macOS and retry.")

    app_bundle = DIST / "MonetizeSocial.app"
    if app_bundle.exists():
        shutil.rmtree(app_bundle)
    app_bundle.mkdir(parents=True, exist_ok=True)

    # PyInstaller onedir is wrapped as a bundle-like folder for drag-and-drop distribution.
    shutil.copytree(app_dir, app_bundle / "Contents/MacOS", dirs_exist_ok=True)

    dmg_path = DIST / "MonetizeSocial.dmg"
    run([create_dmg, str(dmg_path), str(app_bundle)])


def build_exe(app_dir: Path) -> None:
    exe_path = app_dir / "MonetizeSocial.exe"
    if not exe_path.exists():
        raise RuntimeError("Windows executable not found after build.")


def main() -> None:
    platform = sys.argv[1] if len(sys.argv) > 1 else sys.platform
    app_dir = pyinstaller_build()

    if platform.startswith("linux"):
        build_appimage(app_dir)
    elif platform.startswith("win"):
        build_exe(app_dir)
    elif platform == "darwin":
        build_dmg(app_dir)
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")

    print("Runtime package build completed.")


if __name__ == "__main__":
    main()