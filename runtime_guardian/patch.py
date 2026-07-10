from __future__ import annotations


def main() -> int:
    print("[GUARD] owner_approval = REQUIRED")
    print("[GUARD] dangerous_action = DENY")
    print("Observer mode: automatic patching is disabled.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
