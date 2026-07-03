#!/usr/bin/env python3
"""PyScicompTool — Launcher for PyQalculate (CLI / GUI / Tests / Demo).
Replaces PyScicompTool.bat with a cross-platform Python equivalent.
See PyScicompTool.bat for the original Windows-only implementation.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
IS_WINDOWS = sys.platform == "win32"


def _clear() -> None:
    """Clear terminal screen, cross-platform."""
    os.system("cls" if IS_WINDOWS else "clear")


def _venv_python(venv_dir: Path) -> Path:
    """Returns .venv/Scripts/python.exe on Windows, .venv/bin/python on Unix."""
    if IS_WINDOWS:
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _run(cmd, **kwargs) -> subprocess.CompletedProcess:
    """Thin wrapper: subprocess.run([str(c) for c in cmd], check=False, **kwargs)."""
    return subprocess.run([str(c) for c in cmd], check=False, **kwargs)


def check_python() -> None:
    """Check sys.version_info >= (3, 10). Exit if too old."""
    print("[1/2] Checking Python...")
    if sys.version_info < (3, 10):
        print()
        print("Python 3.10 or later is required!")
        print(f"Current version: Python {sys.version.split()[0]}")
        print("Download: https://www.python.org/downloads/")
        print()
        sys.exit(1)
    print(f"Found Python {sys.version}")


def ensure_venv(venv_dir: Path) -> Path:
    """Two-step validation: file exists AND python works.
    If broken, remove and recreate. Returns venv python path."""
    print("[2/2] Checking virtual environment...")
    python_exe = _venv_python(venv_dir)
    venv_valid = False
    if python_exe.exists():
        result = subprocess.run([str(python_exe), "-c", ""],
                                 capture_output=True)
        venv_valid = result.returncode == 0

    if not venv_valid:
        if venv_dir.exists():
            print("Virtual environment is incomplete. Recreating...")
            shutil.rmtree(venv_dir, ignore_errors=True)
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        python_exe = _venv_python(venv_dir)
        print("Virtual environment created successfully.")
    else:
        print("Virtual environment found.")

    return python_exe


def install_deps(python_exe: Path, upgrade: bool = False) -> None:
    """Run pip install -e . (retry without --require-virtualenv on failure).
    Then install optional deps: matplotlib sympy gmpy2."""
    print("Installing core dependencies...")
    result = _run([python_exe, "-m", "pip", "install", "-e", ".",
                   "--require-virtualenv"])
    if result.returncode != 0:
        print("ERROR: Failed to install dependencies.")
        print("Retrying without --require-virtualenv...")
        _run([python_exe, "-m", "pip", "install", "-e", "."])

    print("Installing optional dependencies...")
    _run([python_exe, "-m", "pip", "install", "matplotlib", "sympy", "gmpy2",
          "--require-virtualenv"])


def verify_imports(python_exe: Path) -> None:
    """Verify key imports work. Force-reinstall all if any are broken.
    On Windows also checks pyreadline3."""
    imports = ("sympy,gmpy2,mpmath,pint,convertdate,matplotlib,"
               "numpy,scipy,requests,PIL,dateutil")
    force_pkgs = ["sympy", "gmpy2", "mpmath", "pint", "convertdate",
                   "matplotlib", "numpy", "scipy", "requests", "Pillow",
                   "python-dateutil"]

    if IS_WINDOWS:
        imports += ",pyreadline3"
        force_pkgs.append("pyreadline3")

    result = _run([python_exe, "-c", f"import {imports}"])
    if result.returncode != 0:
        print("[!] Broken packages detected. Force-reinstalling...")
        _run([python_exe, "-m", "pip", "install", "--force-reinstall",
              *force_pkgs])


def run_cli(python_exe: Path) -> None:
    """Run the CLI calculator."""
    subprocess.run([str(python_exe), str(PROJECT_ROOT / "scripts" / "cli.py")])


def run_gui(python_exe: Path) -> None:
    """Run the GUI calculator."""
    print("\nStarting GUI Mode...")
    subprocess.run([str(python_exe), str(PROJECT_ROOT / "scripts" / "gui.py")])


def run_tests(python_exe: Path) -> None:
    """Install test deps, then run the test suite."""
    print("\nInstalling test dependencies...")
    _run([python_exe, "-m", "pip", "install", "-e", ".[dev]", "-q"])
    subprocess.run([str(python_exe),
                    str(PROJECT_ROOT / "scripts" / "test_runner.py")])


def run_demo(python_exe: Path) -> None:
    """Run the demo script."""
    subprocess.run([str(python_exe), str(PROJECT_ROOT / "scripts" / "demo.py")])


def menu_loop(python_exe: Path) -> None:
    """Display the main menu and dispatch to requested mode.
    Invalid input silently reprints the menu."""
    while True:
        _clear()
        print("========================================")
        print("           Main Menu")
        print("========================================")
        print("  [1] CLI Mode     - Command line calculator")
        print("  [2] GUI Mode     - Graphical calculator")
        print("  [3] Run Tests    - Run all test suites")
        print("  [4] Run Demo     - Run all demos")
        print("  [0] Exit")
        print("========================================")
        print()
        choice = input("Select [0-4]: ").strip()

        if choice == "1":
            print("\nStarting CLI Mode...")
            print("Type 'quit' to exit the calculator.")
            _clear()
            run_cli(python_exe)
        elif choice == "2":
            _clear()
            run_gui(python_exe)
        elif choice == "3":
            _clear()
            run_tests(python_exe)
        elif choice == "4":
            _clear()
            run_demo(python_exe)
        elif choice == "0":
            print("\nGoodbye!\n")
            break
        else:
            # Invalid input — silently reprint menu (no error, no pause)
            print()
            continue

        input("\nPress Enter to continue...")


def main() -> None:
    """Print banner, bootstrap venv + deps, then enter menu loop."""
    print()
    print("========================================")
    print("  PyQalculate - Python Calculator")
    print("========================================")
    print()

    check_python()
    venv_dir = PROJECT_ROOT / ".venv"
    python_exe = ensure_venv(venv_dir)
    install_deps(python_exe)
    verify_imports(python_exe)

    _clear()
    menu_loop(python_exe)


if __name__ == "__main__":
    main()
