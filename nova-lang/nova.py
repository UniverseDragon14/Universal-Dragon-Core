#!/usr/bin/env python3
import os
import sys
import shlex
import tarfile
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "nova-lang"
MEMORY = ROOT / "memory" / "memory.txt"
HISTORY = ROOT / "memory" / "history.txt"
BACKUPS = ROOT / "backups"

for p in [ROOT, MEMORY.parent, BACKUPS, ROOT / "lib", ROOT / "apps", ROOT / "tools"]:
    p.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(f"{now()} | {msg}\n")

def clean_text(x):
    x = x.strip()
    if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
        return x[1:-1]
    return x

def render_text(text, vars_map):
    out = clean_text(text)
    for k in sorted(vars_map.keys(), key=len, reverse=True):
        out = out.replace("$" + k, vars_map[k])
    return out

def version():
    print("NOVA Python Core v1.3.1")
    print("Runtime: python nova.py")
    print("Mode: Termux Mobile Tool-Language Core")

def identity():
    print("Universal Dragon = ecosystem")
    print("NOVA = language/core")
    print("EVE = control/doctor layer")
    print("Termux = mobile field lab")
    print("Aslam = creator/builder")

def status():
    print("NOVA Python Status")
    print(f"Root: {ROOT}")
    print(f"User: {os.getenv('USER')}")
    print(f"PWD : {os.getcwd()}")
    os.system("uname -a")

def note(args):
    msg = " ".join(args).strip()
    if not msg:
        print("Use: nova note message")
        return
    with open(MEMORY, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    log("noted: " + msg)
    print("Noted.")

def memory():
    if MEMORY.exists():
        print(MEMORY.read_text(encoding="utf-8"))
    else:
        print("No memory yet.")

def history():
    if HISTORY.exists():
        print(HISTORY.read_text(encoding="utf-8"))
    else:
        print("No history yet.")

def backup():
    name = BACKUPS / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    with tarfile.open(name, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if path == BACKUPS or BACKUPS in path.parents:
                continue
            arcname = Path("nova-lang") / path.relative_to(ROOT)
            tar.add(path, arcname=str(arcname))
    log(f"backup created {name}")
    print(f"Backup created: {name}")

def new_file(args):
    name = args[0] if args else "main.nova"
    file = Path(name).expanduser()
    if file.exists():
        print(f"File already exists: {file}")
        return

    file.write_text("""# NOVA language file
say "Universal Dragon online"
identity
status
note "NOVA file created and tested"
history
""", encoding="utf-8")

    log(f"new nova file created {file}")
    print(f"Created NOVA file: {file}")

def calc_value(expr, vars_map):
    expr = render_text(expr, vars_map)
    allowed = set("0123456789+-*/%.() ")
    if not all(c in allowed for c in expr):
        raise ValueError("only numbers and math operators allowed")
    result = eval(expr, {"__builtins__": {}}, {})
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)

def condition_ok(condition, vars_map):
    condition = condition.strip()
    if "==" in condition:
        op = "=="
    elif "!=" in condition:
        op = "!="
    else:
        print(f"NOVA if error: use == or != -> {condition}")
        return False

    left, right = condition.split(op, 1)
    left = left.strip()
    right = render_text(right.strip(), vars_map)
    left_value = vars_map.get(left, "")

    if op == "==":
        return left_value == right
    return left_value != right

def execute_line(line, vars_map):
    if line.startswith("set ") and "=" in line:
        left, right = line[4:].split("=", 1)
        name = left.strip()
        value = clean_text(right.strip())
        if not name.replace("_", "").isalnum():
            print(f"NOVA variable error: bad name {name}")
            return
        vars_map[name] = value
        print(f"{name} = {value}")

    elif line.startswith("calc ") and "=" in line:
        left, right = line[5:].split("=", 1)
        name = left.strip()
        expr = right.strip()
        if not name.replace("_", "").isalnum():
            print(f"NOVA calc error: bad name {name}")
            return
        try:
            value = calc_value(expr, vars_map)
            vars_map[name] = value
            print(f"{name} = {value}")
        except Exception as e:
            print(f"NOVA calc error: {e}")

    elif line.startswith("say "):
        print(render_text(line[4:], vars_map))

    elif line.startswith("note "):
        note([render_text(line[5:], vars_map)])

    elif line == "vars":
        if vars_map:
            for k, v in vars_map.items():
                print(f"{k} = {v}")
        else:
            print("No variables set.")

    elif line == "identity":
        identity()
    elif line == "status":
        status()
    elif line == "memory":
        memory()
    elif line == "history":
        history()
    elif line == "backup":
        backup()
    else:
        print(f"NOVA does not understand: {line}")

def find_block_end(lines, start):
    depth = 0
    for i in range(start, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("define "):
            depth += 1
        elif line.startswith("repeat ") and " then " not in line:
            depth += 1
        elif line.startswith("if ") and " then " not in line:
            depth += 1
        elif line == "end":
            if depth == 0:
                return i
            depth -= 1
    return -1

def execute_lines(lines, vars_map, functions=None, start=0, end=None):
    if functions is None:
        functions = {}
    if end is None:
        end = len(lines)

    i = start
    while i < end:
        line = lines[i].strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        if line == "end":
            return i

        if line.startswith("use "):
            use_path = render_text(line[4:].strip(), vars_map)
            use_file = Path(use_path).expanduser()
            if not use_file.exists():
                print(f"NOVA use error: file not found {use_file}")
                i += 1
                continue
            print(f"using {use_file}")
            log(f"use file {use_file}")
            use_lines = use_file.read_text(encoding="utf-8").splitlines()
            execute_lines(use_lines, vars_map, functions)
            i += 1
            continue

        if line.startswith("define "):
            name = line[7:].strip()
            if not name.replace("_", "").isalnum():
                print(f"NOVA function error: bad name {name}")
                i += 1
                continue
            block_end = find_block_end(lines, i + 1)
            if block_end == -1:
                print(f"NOVA function error: missing end for {name}")
                return i
            functions[name] = lines[i + 1:block_end]
            print(f"function {name} defined")
            i = block_end + 1
            continue

        if line.startswith("call "):
            raw_call = line[5:].strip()
            try:
                parts = shlex.split(raw_call)
            except Exception as e:
                print(f"NOVA call error: {e}")
                i += 1
                continue
            if not parts:
                print("NOVA call error: missing function name")
                i += 1
                continue

            name = parts[0]
            call_args = [render_text(x, vars_map) for x in parts[1:]]

            if name not in functions:
                print(f"NOVA function not found: {name}")
                i += 1
                continue

            old_args = {}
            for k in list(vars_map.keys()):
                if k == "argc" or (k.startswith("arg") and k[3:].isdigit()):
                    old_args[k] = vars_map[k]
                    del vars_map[k]

            vars_map["argc"] = str(len(call_args))
            for idx, value in enumerate(call_args, start=1):
                vars_map[f"arg{idx}"] = value

            execute_lines(functions[name], vars_map, functions)

            for k in list(vars_map.keys()):
                if k == "argc" or (k.startswith("arg") and k[3:].isdigit()):
                    del vars_map[k]
            vars_map.update(old_args)

            i += 1
            continue

        if line == "functions":
            if functions:
                for name in functions:
                    print(f"function {name}")
            else:
                print("No functions defined.")
            i += 1
            continue

        if line.startswith("repeat "):
            body = line[7:].strip()

            if " then " in body:
                count_text, action = body.split(" then ", 1)
                count_text = render_text(count_text.strip(), vars_map)
                try:
                    count = int(count_text)
                except:
                    print(f"NOVA repeat error: bad count {count_text}")
                    i += 1
                    continue
                if count < 0 or count > 100:
                    print("NOVA repeat error: count must be 0..100")
                    i += 1
                    continue
                for n in range(count):
                    vars_map["i"] = str(n + 1)
                    execute_line(action.strip(), vars_map)
                i += 1
                continue

            count_text = render_text(body, vars_map)
            try:
                count = int(count_text)
            except:
                print(f"NOVA repeat error: bad count {count_text}")
                i += 1
                continue
            if count < 0 or count > 100:
                print("NOVA repeat error: count must be 0..100")
                i += 1
                continue

            block_end = find_block_end(lines, i + 1)
            if block_end == -1:
                print("NOVA repeat error: missing end")
                return i

            for n in range(count):
                vars_map["i"] = str(n + 1)
                execute_lines(lines, vars_map, functions, i + 1, block_end)

            i = block_end + 1
            continue

        if line.startswith("if "):
            body = line[3:].strip()

            if " then " in body:
                condition, action = body.split(" then ", 1)
                if condition_ok(condition, vars_map):
                    execute_line(action.strip(), vars_map)
                else:
                    print(f"IF skipped: {condition.strip()}")
                i += 1
                continue

            block_end = find_block_end(lines, i + 1)
            if block_end == -1:
                print("NOVA if error: missing end")
                return i

            if condition_ok(body, vars_map):
                execute_lines(lines, vars_map, functions, i + 1, block_end)
            else:
                print(f"IF skipped: {body}")

            i = block_end + 1
            continue

        execute_line(line, vars_map)
        i += 1

    return i

def run_file(args):
    if not args:
        print("Use: nova run file.nova")
        return

    file = Path(args[0]).expanduser()
    if not file.exists():
        print(f"File not found: {file}")
        return

    vars_map = {}
    functions = {}
    log(f"run file {file}")
    lines = file.read_text(encoding="utf-8").splitlines()
    execute_lines(lines, vars_map, functions)

def doctor():
    print("NOVA DOCTOR v1.3.1")
    print(f"Root: {ROOT}")

    checks = [
        ("memory", MEMORY),
        ("history", HISTORY),
        ("backups", BACKUPS),
        ("lib", ROOT / "lib"),
        ("apps", ROOT / "apps"),
        ("tools", ROOT / "tools"),
    ]

    issues = 0
    for name, path in checks:
        if path.exists():
            print(f"OK   {name}: {path}")
        else:
            print(f"MISS {name}: {path}")
            issues += 1

    if issues == 0:
        print("NOVA DOCTOR RESULT: GREEN")
    else:
        print(f"NOVA DOCTOR RESULT: YELLOW issues={issues}")

def manifest():
    out = ROOT / "UNIVERSAL_DRAGON_MANIFEST.md"
    text = []
    text.append("# Universal Dragon Manifest v1.1")
    text.append("")
    text.append(f"Generated: {now()}")
    text.append("")
    text.append("## Identity")
    text.append("- Creator: Aslam")
    text.append("- Ecosystem: Universal Dragon")
    text.append("- Core: NOVA")
    text.append("- Runtime: Python")
    text.append("- Branch: Termux Mobile Field Lab")
    text.append("")
    text.append("## Paths")
    text.append(f"- Root: {ROOT}")
    text.append(f"- Memory: {MEMORY}")
    text.append(f"- History: {HISTORY}")
    text.append(f"- Backups: {BACKUPS}")
    text.append("")
    text.append("## Latest History")
    if HISTORY.exists():
        lines = HISTORY.read_text(encoding="utf-8").splitlines()[-15:]
        for line in lines:
            text.append(f"- {line}")
    out.write_text("\n".join(text) + "\n", encoding="utf-8")
    log(f"manifest created {out}")
    print(f"Manifest written: {out}")

def export_bundle():
    name = BACKUPS / f"termux_nova_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    with tarfile.open(name, "w:gz") as tar:
        for item in [
            ROOT / "nova.py",
            ROOT / "lib",
            ROOT / "apps",
            ROOT / "tools",
            ROOT / "memory",
            ROOT / "UNIVERSAL_DRAGON_MANIFEST.md",
        ]:
            if item.exists():
                tar.add(item, arcname=str(Path("nova-lang") / item.relative_to(ROOT)))
    log(f"export bundle created {name}")
    print(f"Export bundle created: {name}")

def export_list():
    files = sorted(BACKUPS.glob("termux_nova_export_*.tar.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not files:
        print("No export bundles found.")
        return
    print("NOVA Export Bundles:")
    for f in files[:10]:
        size = f.stat().st_size
        print(f"{f.name}  {size} bytes")

def import_bundle(args):
    preview_root = ROOT / "restore-preview"
    preview_root.mkdir(parents=True, exist_ok=True)

    if not args:
        print("Use: nova import latest OR nova import file.tar.gz")
        return

    target = args[0]

    if target == "latest":
        files = sorted(BACKUPS.glob("termux_nova_export_*.tar.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not files:
            print("No export bundles found.")
            return
        bundle = files[0]
    else:
        bundle = Path(target).expanduser()
        if not bundle.exists():
            bundle = BACKUPS / target

    if not bundle.exists():
        print(f"Import bundle not found: {bundle}")
        return

    out = preview_root / f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out.mkdir(parents=True, exist_ok=True)

    with tarfile.open(bundle, "r:gz") as tar:
        try:
            tar.extractall(out, filter="data")
        except TypeError:
            tar.extractall(out)

    log(f"import preview extracted {bundle} to {out}")
    print(f"Import preview extracted to: {out}")
    print("Nothing overwritten.")

def sync_guide():
    out = ROOT / "PI5_SYNC_GUIDE.md"
    text = []
    text.append("# Universal Dragon NOVA Pi5 Sync Guide v1.3")
    text.append("")
    text.append(f"Generated: {now()}")
    text.append("")
    text.append("TERMUX SIDE:")
    text.append("1. Run: nova syncpack")
    text.append("2. When Pi5 is ON, copy pack:")
    text.append("   scp ~/nova-lang/backups/termux_to_pi5_sync_*.tar.gz aslam@192.168.1.80:/home/aslam/")
    text.append("")
    text.append("PI5 SIDE:")
    text.append("1. SSH: ssh aslam@192.168.1.80")
    text.append("2. Extract:")
    text.append("   mkdir -p ~/nova-sync-preview")
    text.append("   tar -xzf ~/termux_to_pi5_sync_*.tar.gz -C ~/nova-sync-preview")
    text.append("   cd ~/nova-sync-preview/nova-lang")
    text.append("   bash pi5_install_nova.sh")
    text.append("")
    text.append("TEST:")
    text.append("   nova version")
    text.append("   nova doctor")
    text.append("   nova backup")
    out.write_text("\n".join(text) + "\n", encoding="utf-8")
    log(f"sync guide created {out}")
    print(f"Sync guide written: {out}")

def syncpack():
    manifest()
    sync_guide()

    installer = ROOT / "pi5_install_nova.sh"
    installer.write_text("""#!/usr/bin/env bash
set -e

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/nova-lang"

echo "UNIVERSAL DRAGON - Pi5 NOVA Installer"
echo "Source: $SRC"
echo "Dest  : $DEST"

mkdir -p "$DEST/backups"

if [ -f "$DEST/nova.py" ]; then
  cp "$DEST/nova.py" "$DEST/backups/pi5_nova_before_termux_sync_$(date +%Y%m%d_%H%M%S).py"
  echo "Old Pi5 nova.py backed up."
fi

cp -r "$SRC/." "$DEST/"

cat > /tmp/nova_launcher <<'BASH'
#!/usr/bin/env bash
exec python3 "$HOME/nova-lang/nova.py" "$@"
BASH

sudo mv /tmp/nova_launcher /usr/local/bin/nova
sudo chmod +x /usr/local/bin/nova
chmod +x "$DEST/nova.py"

python3 -m py_compile "$DEST/nova.py"

echo "Pi5 NOVA installed from Termux sync pack."
nova version
nova doctor || true
""", encoding="utf-8")

    installer.chmod(0o755)

    name = BACKUPS / f"termux_to_pi5_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"

    items = [
        ROOT / "nova.py",
        ROOT / "lib",
        ROOT / "apps",
        ROOT / "tools",
        ROOT / "memory",
        ROOT / "UNIVERSAL_DRAGON_MANIFEST.md",
        ROOT / "PI5_SYNC_GUIDE.md",
        ROOT / "pi5_install_nova.sh",
    ]

    with tarfile.open(name, "w:gz") as tar:
        for item in items:
            if item.exists():
                tar.add(item, arcname=str(Path("nova-lang") / item.relative_to(ROOT)))

    log(f"pi5 sync pack created {name}")
    print(f"Pi5 sync pack created: {name}")
    print(f"Later copy to Pi5: scp {name} aslam@192.168.1.80:/home/aslam/")

def synccheck():
    packs = sorted(BACKUPS.glob("termux_to_pi5_sync_*.tar.gz"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not packs:
        print("No Pi5 sync packs found.")
        return

    pack = packs[0]
    print(f"Latest Pi5 sync pack: {pack}")
    print(f"Size: {pack.stat().st_size} bytes")

    required = [
        "nova-lang/nova.py",
        "nova-lang/pi5_install_nova.sh",
        "nova-lang/PI5_SYNC_GUIDE.md",
        "nova-lang/UNIVERSAL_DRAGON_MANIFEST.md",
        "nova-lang/memory/history.txt",
    ]

    issues = 0

    with tarfile.open(pack, "r:gz") as tar:
        names = set(tar.getnames())

    for item in required:
        if item in names:
            print(f"OK   {item}")
        else:
            print(f"MISS {item}")
            issues += 1

    if issues == 0:
        print("NOVA SYNCCHECK RESULT: GREEN")
    else:
        print(f"NOVA SYNCCHECK RESULT: YELLOW issues={issues}")

    log(f"synccheck completed {pack} issues={issues}")

def help_menu():
    print("NOVA Python Core v1.3.1 Commands:")
    print("  nova version")
    print("  nova identity")
    print("  nova status")
    print("  nova note message")
    print("  nova memory")
    print("  nova history")
    print("  nova backup")
    print("  nova doctor")
    print("  nova manifest")
    print("  nova export")
    print("  nova syncguide")
    print("  nova syncpack")
    print("  nova synccheck")
    print("  nova exports")
    print("  nova import latest")
    print("  nova import file.tar.gz")
    print("  nova new file.nova")
    print("  nova run file.nova")
    print("  NOVA file commands: say, note, set, calc, vars, use, define/call, if/end, repeat/end, backup")

cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
args = sys.argv[2:]

if cmd == "version":
    version()
elif cmd == "identity":
    identity()
elif cmd == "status":
    status()
elif cmd == "note":
    note(args)
elif cmd == "memory":
    memory()
elif cmd == "history":
    history()
elif cmd == "backup":
    backup()
elif cmd == "doctor":
    doctor()
elif cmd == "manifest":
    manifest()
elif cmd == "export":
    export_bundle()
elif cmd == "exports":
    export_list()
elif cmd == "import":
    import_bundle(args)
elif cmd == "syncguide":
    sync_guide()
elif cmd == "syncpack":
    syncpack()
elif cmd == "synccheck":
    synccheck()
elif cmd == "new":
    new_file(args)
elif cmd == "run":
    run_file(args)
else:
    help_menu()
