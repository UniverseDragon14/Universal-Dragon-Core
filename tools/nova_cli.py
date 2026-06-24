#!/usr/bin/env python3
from pathlib import Path
import sys
import subprocess
import datetime
import tarfile

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "nova-lang" / "v2" / "nova2_run.py"

def help_text():
    print("NOVA commands:")
    print("  nova run <file.nova>")
    print("  nova qbit <file.nova>")
    print("  nova note <message>")
    print("  nova backup")
    print("  nova doctor")

def resolve_file(name: str) -> Path:
    p = Path(name)
    if p.exists():
        return p
    rp = ROOT / name
    if rp.exists():
        return rp
    print(f"NOVA file not found: {name}")
    sys.exit(2)

def run_nova(file_arg: str) -> int:
    if not RUNNER.exists():
        print(f"NOVA v2 runner not found: {RUNNER}")
        return 1
    target = resolve_file(file_arg)
    return subprocess.call([sys.executable, str(RUNNER), str(target)])

def note(args):
    notes_dir = Path.home() / "nova-lang" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    msg = " ".join(args).strip()
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(notes_dir / "nova_notes.log", "a", encoding="utf-8") as f:
        f.write(f"{stamp} {msg}\n")
    print("Noted.")

def backup():
    backup_dir = Path.home() / "nova-lang" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"backup_{stamp}.tar.gz"

    skip_names = {".git", "node_modules", ".next", "dist", "build"}

    with tarfile.open(dest, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if any(part in skip_names for part in path.parts):
                continue
            arc = Path(ROOT.name) / path.relative_to(ROOT)
            tar.add(path, arcname=str(arc), recursive=False)

    print(f"Backup created: {dest}")

def doctor():
    print("NOVA doctor")
    print(f"ROOT   : {ROOT}")
    print(f"RUNNER : {RUNNER}")
    print(f"Python : {sys.version.split()[0]}")
    print(f"Runner : {'OK' if RUNNER.exists() else 'MISSING'}")
    help_text()

def main():
    if len(sys.argv) < 2:
        help_text()
        return 0

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd in ("run", "qbit"):
        if not args:
            print(f"Usage: nova {cmd} <file.nova>")
            return 1
        return run_nova(args[0])

    if cmd == "note":
        note(args)
        return 0

    if cmd == "backup":
        backup()
        return 0

    if cmd in ("doctor", "version"):
        doctor()
        return 0

    help_text()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
