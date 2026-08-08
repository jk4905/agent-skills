# Diagnosing Long-Running Worker / Cron Failure Modes

Companion to `diagnosing-bugs/SKILL.md`. Use this when the user reports "the cron
keeps failing", "the worker died", "backfill got stuck", "only some items
processed", or any variant where the failing system is a supervisor loop that
repeatedly spawns short-lived subprocesses.

## Symptom signature

Before reaching for `git bisect` or a Phase 3 hypothesis, look for this exact
fingerprint in the logs. If you see ≥2 of these in a row, **the loop is the
bug**, not any individual subprocess:

1. A long-running supervisor (`while X: run_subprocess(); sleep N`).
2. Hundreds of identical "batch failed exit=N; sleep 60s" log lines.
3. The subprocess error is `init_sys_streams: can't initialize sys standard
   streams`, `OSError: [Errno 9] Bad file descriptor`, `BrokenPipeError`, or
   any other error that *fires before user code runs*.
4. The first batch often succeeds, then failures start and never stop.
5. The reported "error" is a misleading downstream effect ("No Patreon
   cookies found", "Login expired", "Timeout") — none of which point at the
   real cause.

If all five match, **stop reading business code**. The Phase 1 feedback loop
for this bug is the supervisor itself: reproduce by running the same shell
wrapper in the foreground and inspecting how its child process inherits stdin
/ stdout / stderr.

## Root-cause checklist (in this order)

### A. Subprocess stream handling

```python
# WRONG — common pattern in long-running supervisors.
result = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
```

Why it's a bug:

- `capture_output=True` keeps the parent's pipes alive for the full child
  lifetime. In a long-running parent (e.g. a cron supervisor), those pipes
  can be invalidated by the host (session logout, log rotation, parent going
  through its own state transitions).
- `text=True` alone does not stream to disk.
- When the child's stdout/stderr fd inherited from the parent is already
  closed at the OS level, Python's interpreter initialization fails before
  user code runs. You see `init_sys_streams`, not your own exception.

Fix:

```python
with log_file.open("a", encoding="utf-8") as log_file:
    result = subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=log_file,
        stderr=subprocess.STDOUT,   # merge so OOM/segfault still appears
        start_new_session=True,     # new session group, not attached to parent
        text=True,
        check=False,
    )
```

And the shell wrapper:

```bash
setsid "$BACKFILL" </dev/null >>"$LOG" 2>&1 &
```

`<dev/null` is the most often-missed part. Without it, the child inherits
the parent's stdin fd which can already be a closed pipe by the time the
child starts.

### B. Venv fallback masking missing dependencies

```bash
# WRONG — silently falls back to system Python when venv is missing.
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON="python3"
fi
```

Symptoms look like authentication / network issues ("No cookies found",
"Login expired") because the system Python lacks `cryptography` / `requests`.
Diagnose by running `python -c "import cryptography, requests"` **inside the
venv path the script claims to use** before suspecting anything else.

Fix: remove the fallback. venv missing is a deploy bug — fail fast.

### C. PID-file "lock" that isn't a lock

```bash
# WRONG — string match is not a process check.
pgrep -f "worker_name.sh"
```

`pgrep -f` matches substrings of any user's command line. After a crash,
the shell that ran `worker_name.sh` may still be present even though the
real worker died. You then skip restart, claim "still running", and the
queue silently stalls.

Fix:

1. Use `fcntl.flock` on a real lockfile for *serialize* (multiple workers must
   not run).
2. Use PIDFILE + `kill -0 "$pid"` for *liveness* (is the one worker still
   alive?).
3. Never combine the two by guessing.

### D. State stored only on success

If the only "completed" signal is a `written` flag written at the very end,
then every process kill (Ctrl-C, OOM, parent session ending) makes you
reprocess from scratch. Worse, the resumable queue widens to "everything that
ever started".

Fix: persist a checkpoint at every stage boundary, and on reload, compare
the saved state to what would be redone. Skip stages whose checkpoint is
present and valid.

### E. Fixed sleep retry on every failure

```python
except Exception:
    time.sleep(60)
```

This converts an unrecoverable error (venv missing, login expired, Python
sys-streams broken) into N hours of identical failures.

Fix: classify errors (`SyncAlreadyRunning`, `NeedsLogin`, `RateLimited`,
`PermanentHTTPError`, `EnvironmentError`) and only sleep-retry the ones that
benefit from it. For everything else, exit with a distinct code and let the
outer supervisor stop spawning you.

## A tight feedback loop for this class of bug

```bash
# 1. Capture the last 5 minutes of failures.
tail -200 ~/.hermes/logs/<worker>.log | grep -E "Bad file descriptor|Fatal|exit="

# 2. Run the worker in the foreground with the exact same args the cron uses,
#    but with stdin from /dev/null.
</dev/null ~/.hermes/scripts/<wrapper>.sh

# 3. If it works in the foreground but not under cron, suspect stream inheritance
#    or session detachment. Add start_new_session=True and setsid.

# 4. Run TWO workers concurrently with the proposed flock-based lock; verify
#    exactly one runs.
~/.hermes/scripts/<wrapper>.sh &
~/.hermes/scripts/<wrapper>.sh &
wait
```

If step 1 shows ≥10 identical "exit=N" lines with N being the same number
across batches, the loop is the bug — don't go deeper.

## What "fixed" looks like

- One fresh subprocess per batch, with explicit `</dev/null`, `start_new_session`,
  and a streaming log fd. No `capture_output=True`.
- A `fcntl.flock` lockfile at the supervisor root; second worker exits with
  code 3 (or whatever your convention is) and does not retry.
- venv path validated at script start; missing venv exits with a distinct
  code, not a silent fallback.
- Per-stage checkpoints written to the queue/state file. After SIGTERM, the
  next worker resumes from the last checkpoint, not from scratch.
- Error classification in place; non-retryable errors abort, retryable
  errors use exponential backoff.

## Why this is its own reference

The diagnosing-bugs skill is written for code-level bugs (one failing test,
one wrong function). Long-running workers look like code-level bugs because
the log message points at user code, but the actual cause is process /
session / IPC plumbing that the user code never touches. Treating this as
"find the line that throws" wastes days. Treat it as "the loop is the bug"
and the answer is structural.