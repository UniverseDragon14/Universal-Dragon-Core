#!/usr/bin/env bash
# eve guard — ask Nova Guard whether an action is allowed / needs approval / blocked.

eve_cmd_guard() {
  local action="${1:-}"
  if [ -z "$action" ]; then
    eve_err "usage: ./eve guard <action>   (e.g. check, network, install, delete)"
    return 2
  fi
  eve_pyrun - "$action" <<'PY'
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
try:
    import qbit_nova_guard_approval_v06 as guard
    d = guard.guard_decision(sys.argv[1])
    icon = {"allowed": "✦", "needs_approval": "?", "blocked": "✗"}.get(d.get("decision"), "•")
    print(f"{icon} {sys.argv[1]} -> {d.get('decision')}: {d.get('reason')}")
except Exception as e:
    print(f"guard unavailable: {e}", file=sys.stderr)
    sys.exit(1)
PY
}
