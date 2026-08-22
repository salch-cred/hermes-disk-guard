---
name: disk-guard
description: Watch disk space and deliver low-space alerts on schedule.
version: 1.0.0
author: salch-cred (https://github.com/salch-cred)
license: MIT
metadata:
  hermes:
    tags: [System, Monitoring, DevOps, Blueprint]
    related_skills: []
    config:
      - key: diskguard.paths
        description: Comma-separated paths to watch
        default: ""
        prompt: Paths to watch (blank = OS root)
      - key: diskguard.min_free_gb
        description: Alert when free space drops below this many GiB
        default: "5"
        prompt: Minimum free GiB before alerting
      - key: diskguard.max_used_percent
        description: Alert when used space exceeds this percentage
        default: "90"
        prompt: Maximum used percentage before alerting
    blueprint:
      schedule: "0 * * * *"
      deliver: origin
      prompt: "Run the disk-guard check and alert only if a volume is running low."
---

# Disk Guard Skill

Checks free space on one or more volumes with `shutil.disk_usage` and alerts
when free space falls below a GiB floor or used space exceeds a percentage.
Stdlib-only; no third-party dependencies. Ships as a
[blueprint](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills#blueprints-skills-that-are-also-automations),
so it can run hourly as a scheduled watchdog.

It does not delete files, move data, or unmount anything — monitoring only.

## When to Use

- The user asks how much disk space is free or wants low-space warnings.
- A scheduled watchdog should flag volumes before they fill.

## Prerequisites

- Read access to the watched paths. None of them need to be mounted at load
  time; unreachable paths are reported as alerts, not crashes.

## How to Run

Run the bundled script through the `terminal` tool:

```
python ${HERMES_SKILL_DIR}/scripts/check_disk.py --path / --min-free-gb 10
```

Omit `--path` to use the configured values from `config.yaml`
(`diskguard.paths`), which the agent receives in the activation message.

## Quick Reference

| Task | Command |
|------|---------|
| Check OS root | `python ${HERMES_SKILL_DIR}/scripts/check_disk.py` |
| Watch several paths | add `--path C:\ --path D:\` |
| Custom floor | add `--min-free-gb 20 --max-used-percent 85` |
| Cron-friendly silence | add `--quiet-ok` (prints nothing when healthy) |

## Procedure

1. Read configured paths/thresholds from the skill config injected at load time.
2. Run the script via the `terminal` tool.
3. Exit code `0` = healthy: summarize the table in one line, or stay quiet
   for scheduled runs. Exit code `1` = alert: surface every 🚨 line verbatim,
   then list the three largest directories if the user asks for cleanup help.

## Pitfalls

- **Windows drive roots**: pass `C:\` (or another drive letter), not `/`.
- **Network mounts** can be slow or hang — keep them out of the hourly
  blueprint and check them on demand instead.
- **Small volumes**: percentage thresholds trip early on tiny volumes;
  prefer `--min-free-gb` there.

## Verification

- Healthy volume prints the Markdown table plus `✅ All volumes healthy.`
  and exits `0`.
- A threshold trip prints the 🚨 alert line and exits `1`.
- `--quiet-ok` prints nothing at all while everything is healthy.
