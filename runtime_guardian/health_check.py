from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROPERTIES = (
    "LoadState",
    "ActiveState",
    "SubState",
    "UnitFileState",
    "NRestarts",
    "ExecMainPID",
    "ControlGroup",
    "WorkingDirectory",
    "ExecStart",
)


def run(
    command: list[str],
    timeout: int = 15,
) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env={
            **os.environ,
            "SYSTEMD_PAGER": "cat",
            "PAGER": "cat",
        },
    )

    return (
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
    )


def safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def show_unit(
    manager: str,
    unit: str,
) -> dict[str, str]:
    command = ["systemctl"]

    if manager == "user":
        command.append("--user")

    command.extend([
        "--no-pager",
        "show",
        unit,
    ])

    for property_name in PROPERTIES:
        command.extend([
            "-p",
            property_name,
        ])

    _, stdout, _ = run(command)

    values: dict[str, str] = {}

    for line in stdout.splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key] = value

    return values


def cgroup_pids(control_group: str) -> set[int]:
    if not control_group:
        return set()

    root = (
        Path("/sys/fs/cgroup")
        / control_group.lstrip("/")
    )

    if not root.exists():
        return set()

    files = [root / "cgroup.procs"]
    files.extend(root.rglob("cgroup.procs"))

    pids: set[int] = set()

    for file_path in files:
        try:
            for line in file_path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines():
                if line.strip().isdigit():
                    pids.add(int(line.strip()))
        except OSError:
            continue

    return pids


def read_socket_rows() -> tuple[list[str], str]:
    code, stdout, stderr = run([
        "sudo",
        "-n",
        "ss",
        "-lntpH",
    ])

    if code != 0:
        return [], stderr or "socket inspection failed"

    return stdout.splitlines(), ""


def port_owners(
    port: int,
    socket_rows: list[str],
) -> tuple[set[int], bool]:
    owners: set[int] = set()
    listening = False

    pattern = re.compile(
        rf":{port}\s"
    )

    for row in socket_rows:
        if not pattern.search(row):
            continue

        listening = True

        for match in re.findall(
            r"pid=(\d+)",
            row,
        ):
            owners.add(int(match))

    return owners, listening


def http_status(url: str) -> int:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Universal-Dragon-Guardian/2.0",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=6,
        ) as response:
            return int(response.status)
    except urllib.error.HTTPError as error:
        return int(error.code)
    except Exception:
        return 0


def add_issue(
    issues: list[dict[str, Any]],
    component: dict[str, Any],
    check: str,
    expected: str,
    observed: str,
    message: str,
) -> None:
    issues.append({
        "component": component["id"],
        "check": check,
        "expected": expected,
        "observed": observed,
        "critical": bool(
            component.get("critical", True)
        ),
        "message": message,
    })


def check_canonical_unit(
    component: dict[str, Any],
    socket_rows: list[str],
    socket_error: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    state = show_unit(
        component["manager"],
        component["unit"],
    )

    issues: list[dict[str, Any]] = []

    result: dict[str, Any] = {
        "id": component["id"],
        "healthy": True,
        "checks": {},
    }

    load_state = state.get(
        "LoadState",
        "unknown",
    )

    active_state = state.get(
        "ActiveState",
        "unknown",
    )

    enabled_state = state.get(
        "UnitFileState",
        "unknown",
    )

    restart_count = safe_int(
        state.get("NRestarts")
    )

    main_pid = safe_int(
        state.get("ExecMainPID")
    )

    result["checks"].update({
        "load_state": load_state,
        "active_state": active_state,
        "enabled_state": enabled_state,
        "restart_count": restart_count,
        "main_pid": main_pid,
    })

    if load_state != "loaded":
        add_issue(
            issues,
            component,
            "load_state",
            "loaded",
            load_state,
            "Canonical unit is not loaded.",
        )

    if active_state != "active":
        add_issue(
            issues,
            component,
            "active_state",
            "active",
            active_state,
            "Canonical service is not active.",
        )

    if (
        component.get("expected_enabled")
        and enabled_state != "enabled"
    ):
        add_issue(
            issues,
            component,
            "enabled_state",
            "enabled",
            enabled_state,
            "Canonical service is not enabled.",
        )

    maximum_restarts = int(
        component.get("max_restarts", 5)
    )

    if restart_count > maximum_restarts:
        add_issue(
            issues,
            component,
            "restart_count",
            f"<= {maximum_restarts}",
            str(restart_count),
            "Restart threshold exceeded.",
        )

    expected_directory = component.get(
        "working_directory"
    )

    if expected_directory:
        observed_directory = state.get(
            "WorkingDirectory",
            "",
        ).lstrip("!")

        result["checks"][
            "working_directory_match"
        ] = (
            observed_directory
            == expected_directory
        )

        if observed_directory != expected_directory:
            add_issue(
                issues,
                component,
                "working_directory",
                expected_directory,
                observed_directory,
                "Working directory mismatch.",
            )

    exec_start = state.get(
        "ExecStart",
        "",
    )

    missing_fragments = [
        fragment
        for fragment in component.get(
            "exec_contains",
            [],
        )
        if fragment not in exec_start
    ]

    result["checks"]["exec_contract"] = (
        len(missing_fragments) == 0
    )

    if missing_fragments:
        add_issue(
            issues,
            component,
            "exec_contract",
            "all required fragments",
            ", ".join(missing_fragments),
            "ExecStart contract mismatch.",
        )

    if "port" in component:
        port = int(component["port"])

        if socket_error:
            add_issue(
                issues,
                component,
                "port_ownership",
                f"service owns port {port}",
                socket_error,
                "Socket ownership could not be checked.",
            )
        else:
            owner_pids, listening = port_owners(
                port,
                socket_rows,
            )

            service_pids = cgroup_pids(
                state.get(
                    "ControlGroup",
                    "",
                )
            )

            owned = bool(
                owner_pids.intersection(
                    service_pids
                )
            )

            result["checks"]["port"] = {
                "number": port,
                "listening": listening,
                "owned_by_service": owned,
                "owner_pids": sorted(owner_pids),
            }

            if not listening:
                add_issue(
                    issues,
                    component,
                    "port_listening",
                    "listening",
                    "closed",
                    f"Port {port} is not listening.",
                )
            elif not owned:
                add_issue(
                    issues,
                    component,
                    "port_ownership",
                    "listener inside service cgroup",
                    str(sorted(owner_pids)),
                    "Another runtime owns the port.",
                )

    if "http_url" in component:
        status = http_status(
            component["http_url"]
        )

        expected_statuses = [
            int(value)
            for value in component.get(
                "expected_http",
                [200],
            )
        ]

        result["checks"]["http_status"] = status

        if status not in expected_statuses:
            add_issue(
                issues,
                component,
                "http_status",
                str(expected_statuses),
                str(status),
                "HTTP health response mismatch.",
            )

    result["healthy"] = len(issues) == 0

    return result, issues


def check_parked_unit(
    component: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    state = show_unit(
        component["manager"],
        component["unit"],
    )

    load_state = state.get(
        "LoadState",
        "not-found",
    )

    active_state = state.get(
        "ActiveState",
        "inactive",
    )

    enabled_state = state.get(
        "UnitFileState",
        "disabled",
    )

    main_pid = safe_int(
        state.get("ExecMainPID")
    )

    issues: list[dict[str, Any]] = []

    result = {
        "id": component["id"],
        "healthy": True,
        "checks": {
            "load_state": load_state,
            "active_state": active_state,
            "enabled_state": enabled_state,
            "main_pid": main_pid,
        },
    }

    if (
        load_state == "not-found"
        and component.get("allow_missing", False)
    ):
        result["checks"]["state"] = "safe_absent"
        return result, issues

    if active_state != "inactive":
        add_issue(
            issues,
            {
                **component,
                "critical": True,
            },
            "parked_active_state",
            "inactive",
            active_state,
            "Parked duplicate became active.",
        )

    if enabled_state != "disabled":
        add_issue(
            issues,
            {
                **component,
                "critical": True,
            },
            "parked_enabled_state",
            "disabled",
            enabled_state,
            "Parked duplicate became enabled.",
        )

    if main_pid != 0:
        add_issue(
            issues,
            {
                **component,
                "critical": True,
            },
            "parked_pid",
            "0",
            str(main_pid),
            "Parked duplicate still owns a PID.",
        )

    result["healthy"] = len(issues) == 0

    return result, issues


def check_pm2(
    component: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    code, stdout, stderr = run([
        "pm2",
        "jlist",
    ])

    issues: list[dict[str, Any]] = []

    result: dict[str, Any] = {
        "id": component["id"],
        "healthy": True,
        "checks": {},
    }

    if code != 0:
        add_issue(
            issues,
            component,
            "pm2_query",
            "success",
            stderr or "failed",
            "PM2 query failed.",
        )

        result["healthy"] = False
        return result, issues

    try:
        applications = json.loads(stdout)
    except json.JSONDecodeError:
        add_issue(
            issues,
            component,
            "pm2_json",
            "valid JSON",
            "invalid JSON",
            "PM2 output could not be parsed.",
        )

        result["healthy"] = False
        return result, issues

    matches = [
        application
        for application in applications
        if application.get("name")
        == component["name"]
    ]

    if len(matches) != 1:
        add_issue(
            issues,
            component,
            "pm2_instance_count",
            "1",
            str(len(matches)),
            "PM2 ownership is ambiguous.",
        )

        result["healthy"] = False
        return result, issues

    application = matches[0]
    environment = application.get(
        "pm2_env",
        {},
    )

    observed = {
        "status": environment.get(
            "status",
            "unknown",
        ),
        "cwd": environment.get(
            "pm_cwd",
            "",
        ),
        "script": environment.get(
            "pm_exec_path",
            "",
        ),
        "restarts": safe_int(
            environment.get("restart_time")
        ),
        "pid": safe_int(
            application.get("pid")
        ),
    }

    result["checks"] = observed

    expected = {
        "status":
            component["expected_status"],
        "cwd":
            component["expected_cwd"],
        "script":
            component["expected_script"],
    }

    for key, value in expected.items():
        if observed[key] != value:
            add_issue(
                issues,
                component,
                f"pm2_{key}",
                value,
                str(observed[key]),
                f"PM2 {key} mismatch.",
            )

    if observed["restarts"] > int(
        component.get("max_restarts", 5)
    ):
        add_issue(
            issues,
            component,
            "pm2_restarts",
            f"<= {component.get('max_restarts', 5)}",
            str(observed["restarts"]),
            "PM2 restart threshold exceeded.",
        )

    if observed["pid"] <= 0:
        add_issue(
            issues,
            component,
            "pm2_pid",
            "> 0",
            str(observed["pid"]),
            "PM2 process has no live PID.",
        )

    result["healthy"] = len(issues) == 0

    return result, issues


def check_process_contract(
    component: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    code, stdout, stderr = run([
        "ps",
        "-C",
        component["process_name"],
        "-o",
        "args=",
    ])

    commands = [
        line.strip()
        for line in stdout.splitlines()
        if line.strip()
    ]

    issues: list[dict[str, Any]] = []

    result = {
        "id": component["id"],
        "healthy": True,
        "checks": {
            "count": len(commands),
        },
    }

    if code not in {0, 1}:
        add_issue(
            issues,
            component,
            "process_query",
            "success",
            stderr or "failed",
            "Process query failed.",
        )

    expected_count = int(
        component["exact_count"]
    )

    if len(commands) != expected_count:
        add_issue(
            issues,
            component,
            "process_count",
            str(expected_count),
            str(len(commands)),
            "Process count contract mismatch.",
        )

    for fragment in component.get(
        "required_fragments",
        [],
    ):
        if not any(
            fragment in command
            for command in commands
        ):
            add_issue(
                issues,
                component,
                "process_fragment",
                fragment,
                "missing",
                "Required canonical process is absent.",
            )

    result["healthy"] = len(issues) == 0

    return result, issues


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
    )

    arguments = parser.parse_args()

    manifest = json.loads(
        arguments.manifest.read_text(
            encoding="utf-8",
        )
    )

    socket_rows, socket_error = (
        read_socket_rows()
    )

    report: dict[str, Any] = {
        "schema_version": 2,
        "mode": "observe_only",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "canonical_systemd": [],
        "canonical_pm2": [],
        "parked_systemd": [],
        "process_contracts": [],
        "issues": [],
    }

    all_issues: list[dict[str, Any]] = []

    for component in manifest[
        "canonical_systemd"
    ]:
        result, issues = check_canonical_unit(
            component,
            socket_rows,
            socket_error,
        )

        report["canonical_systemd"].append(
            result
        )

        all_issues.extend(issues)

    for component in manifest[
        "canonical_pm2"
    ]:
        result, issues = check_pm2(component)

        report["canonical_pm2"].append(
            result
        )

        all_issues.extend(issues)

    for component in manifest[
        "parked_systemd"
    ]:
        result, issues = check_parked_unit(
            component
        )

        report["parked_systemd"].append(
            result
        )

        all_issues.extend(issues)

    for component in manifest[
        "process_contracts"
    ]:
        result, issues = (
            check_process_contract(component)
        )

        report["process_contracts"].append(
            result
        )

        all_issues.extend(issues)

    report["issues"] = all_issues

    all_results = (
        report["canonical_systemd"]
        + report["canonical_pm2"]
        + report["parked_systemd"]
        + report["process_contracts"]
    )

    healthy_count = sum(
        1
        for item in all_results
        if item["healthy"]
    )

    critical_count = sum(
        1
        for issue in all_issues
        if issue["critical"]
    )

    report["summary"] = {
        "total_contracts":
            len(all_results),
        "healthy_contracts":
            healthy_count,
        "issues":
            len(all_issues),
        "critical_issues":
            critical_count,
    }

    reports_directory = (
        arguments.manifest.parent
        / "reports"
    )

    reports_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = reports_directory / (
        "health_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("========================================")
    print("🐉 RUNTIME OWNERSHIP HEALTH V2")
    print("========================================")
    print(
        "Healthy contracts : "
        f"{healthy_count}/{len(all_results)}"
    )
    print(
        f"Issues            : {len(all_issues)}"
    )
    print(
        f"Critical issues   : {critical_count}"
    )
    print(f"Report            : {report_path}")
    print("Automatic actions : NONE")
    print("Secrets displayed : NO")

    for issue in all_issues:
        level = (
            "CRITICAL"
            if issue["critical"]
            else "WARNING"
        )

        print(
            f"[{level}] "
            f"{issue['component']} "
            f"{issue['check']}: "
            f"{issue['message']} "
            f"observed={issue['observed']}"
        )

    return 2 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
