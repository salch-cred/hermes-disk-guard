#!/usr/bin/env python3
"""Check free disk space and alert when a volume runs low.

Stdlib-only (shutil) so the skill works on every Hermes platform.
Prints a Markdown status line per checked path; exits non-zero when a
threshold trips so cron/blueprint deliveries surface the alert.
"""

import argparse
import os
import shutil
import sys

GIB = 1024 ** 3


def default_path():
    """Return the OS-appropriate root path."""
    return "C:\\" if os.name == "nt" else "/"


def render_status(path, total, used, free):
    """Render one Markdown status row from raw byte counts."""
    total_gib = total / GIB
    free_gib = free / GIB
    used_pct = (used / total * 100) if total else 0.0
    return (
        f"| `{path}` | {total_gib:,.1f} GiB | {free_gib:,.1f} GiB | {used_pct:.1f}% |"
    )


def is_alert(free, total, min_free_gib, max_used_percent):
    """Return True when either low-space threshold trips."""
    if free < min_free_gib * GIB:
        return True
    if total > 0:
        used_percent = (total - free) / total * 100
        if used_percent > max_used_percent:
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", dest="paths",
                        help="Path to check (repeatable; default: OS root)")
    parser.add_argument("--min-free-gb", type=float, default=5.0,
                        help="Alert when free space drops below this many GiB")
    parser.add_argument("--max-used-percent", type=float, default=90.0,
                        help="Alert when used space exceeds this percentage")
    parser.add_argument("--quiet-ok", action="store_true",
                        help="Suppress the table when all volumes are healthy")
    args = parser.parse_args(argv)

    paths = [p.strip() for p in (args.paths or []) if p.strip()] or [default_path()]

    rows = ["| Path | Total | Free | Used % |", "|------|------:|-----:|-------:|"]
    alerts = []
    for path in paths:
        if not os.path.exists(path):
            alerts.append(f"⚠ Path not found: `{path}`")
            continue
        try:
            total, _used, free = shutil.disk_usage(path)
        except OSError as error:
            print(f"error: cannot stat {path}: {error}", file=sys.stderr)
            return 1
        rows.append(render_status(path, total, total - free, free))
        if is_alert(free, total, args.min_free_gb, args.max_used_percent):
            free_gib = free / GIB
            alerts.append(
                f"🚨 Low disk space on `{path}`: only {free_gib:.1f} GiB free "
                f"(min {args.min_free_gb:g} GiB / max {args.max_used_percent:g}% used)"
            )

    if not (args.quiet_ok and not alerts):
        print("\n".join(rows))
    if alerts:
        print("\n".join(alerts))
        return 1
    if not args.quiet_ok:
        print("✅ All volumes healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
