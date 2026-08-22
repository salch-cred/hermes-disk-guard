# disk-guard — a Hermes Agent skill

Low-disk-space watchdog for [Hermes Agent](https://github.com/NousResearch/hermes-agent).
Checks volumes with `shutil.disk_usage` and alerts when free space drops
below a GiB floor or used space exceeds a percentage. Stdlib-only.

Ships as a **blueprint**: install it and Hermes offers an hourly cron that
stays silent while every volume is healthy and speaks up the moment one is
running low (`/suggestions accept 1`).

## Install

```
hermes skills install salch-cred/hermes-disk-guard
```

or copy this folder into `~/.hermes/skills/`.

## Usage

In a session:

> Use the disk-guard skill to check my drives

Direct script use (any platform):

```
python scripts/check_disk.py --path C:\ --path D:\ --min-free-gb 10 [--quiet-ok]
```

Exit codes: `0` healthy · `1` alert · `2` usage error.

## Configure

```
hermes config set skills.config.diskguard.paths "C:\,D:\"
hermes config set skills.config.diskguard.min_free_gb 10
hermes config set skills.config.diskguard.max_used_percent 85
```

## Schedule

After install: `/suggestions` → accept the disk-guard blueprint for an hourly
watchdog. Pair with `--quiet-ok` so it only ever messages you when something
is wrong.

## Test

```
python -m pytest tests/ -q
```

## License

MIT © 2026 salch-cred
