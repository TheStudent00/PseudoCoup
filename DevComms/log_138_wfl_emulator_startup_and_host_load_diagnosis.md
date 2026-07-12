# log_138 — WFL emulator startup, install, and host-load diagnosis

**Date:** 2026-07-12
**Context:** User was starting the `WFL_Compare_AVD` emulator in the WFL_MixingCenter workspace and
couldn't tell if the first startup was stuck. This log captures the full diagnostic arc, the
(corrected) root causes, the final working recipe, and the host cleanup performed at the end.
User was shutting down Antigravity and switching to Zed; asked to close old/unused processes.

---

## TL;DR

- **WFL code is fine** — `:app:assembleDebug` compiles clean. Nothing here was an app bug.
- **First emulator launch hung** on a corrupt AVD **snapshot**, not the GPU. Fixed with a cold boot
  (`-no-snapshot-load`).
- **`-gpu swiftshader_indirect` was stable but far too slow** on this host → launcher ANRs,
  wellbeing crash, activity-manager unresponsive, ddmlib install timeout. All were
  **emulator-performance symptoms, not WFL**.
- **`-gpu host` fixed it**: clean **~12 s** boot, responsive system. The original hang did NOT recur
  → confirms the first hang was the snapshot, not hardware GPU.
- **Plain `./gradlew installDebug` fails** with
  `INSTALL_FAILED_MISSING_SHARED_LIBRARY: com.google.android.wearable` because it also tries to
  install the **`:wear`** (Wear OS) module onto a **phone** AVD. **Use `:app:installDebug`.**
- App installed and launched successfully: `topResumedActivity = com.sara.workoutforlife/.MainActivity`,
  no WFL crash/ANR in logcat.
- **Host was overloaded** (load ~18 on 12 cores) — this is what made the whole session slow.

---

## The working recipe (WFL on a phone AVD)

```bash
# Launch with hardware GPU + clean cold boot (avoids the snapshot hang)
~/Android/Sdk/emulator/emulator -avd WFL_Compare_AVD -no-snapshot-load -gpu host &

# Wait until actually booted before installing (don't rush — timeouts happen under load)
ADB=~/Android/Sdk/platform-tools/adb
$ADB wait-for-device
until [ "$($ADB shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do sleep 2; done

# Install ONLY the phone module — bare `installDebug` fails on the :wear module (phone AVD lacks
# the com.google.android.wearable shared library)
cd ~/Programming/WFL_MixingCenter/WFL && ./gradlew :app:installDebug

# Launch
$ADB shell am start -n com.sara.workoutforlife/.MainActivity
```

Package: `com.sara.workoutforlife` · Main activity: `.MainActivity`

---

## Symptom → cause map (everything that looked scary, and what it really was)

| Symptom observed | Actual cause | Not caused by |
|---|---|---|
| Emulator "stuck" on first boot (9 min, ~0 CPU, device `offline`) | Corrupt AVD **snapshot**; qemu idle in `poll_schedule_timeout` | GPU, WFL |
| `com.google.android.apps.wellbeing` FATAL, `audioserver` SIGABRT | Stock emulator system-app noise | WFL |
| "Pixel Launcher isn't responding" ANR | swiftshader software rendering too slow → launcher CPU-starved | WFL |
| `installDebug` "BUILD FAILED in 4m32s" (first) | `ShellCommandUnresponsiveException` — ddmlib **timeout**; APK actually installed anyway | code/signing |
| "Unable to connect to activity manager" on launch | `system_server` unresponsive under swiftshader load | WFL |
| `installDebug` FAILED (`INSTALL_FAILED_MISSING_SHARED_LIBRARY`) | `:wear` module installed onto a phone AVD | phone `:app` (installs fine) |
| "workoutforlife isn't responding" ANR | Emulator starved by saturated encrypted disk + overloaded host | WFL app logic |

---

## Host-load diagnosis (12 cores)

- Load average sat at **~17–21** for most of the session = ~1.5× oversubscribed.
- `vmstat` showed **I/O-wait up to 96%** and heavy `bo` (block writes) → **disk-bound**, not
  compute-bound. Disk is **encrypted (dm-crypt)**, so a wall of `kcryptd` kernel threads burned CPU
  encrypting that I/O.
- Swap was barely used (`si/so` ≈ 0) → **not** swap thrashing (an earlier guess of mine was wrong).

### CORRECTION — do not trust `/proc/<pid>/io: write_bytes` on this host
Mid-session I read `write_bytes` and concluded an **Antigravity terminal was a 1.9 TB runaway**.
**That was wrong.** The target file (`~/.config/Antigravity/logs/.../ptyhost.log`) was only **589 bytes**
and Antigravity was near-idle (~10% CPU total). The counter reported ~2 TB for that tiny-file bash,
for qemu, *and* for gnome-shell simultaneously — impossible. On this **dm-crypt** setup `write_bytes`
appears massively inflated / unreliable. **Use `vmstat` iowait + load average, not per-proc
`write_bytes`, to judge disk load here.**

### What actually carried the load
The emulator itself (~1 core of qemu) **plus** the `kcryptd` threads serving its disk I/O. Evidence:
when the emulator exited near the end, **load fell from ~18 to 7.68** immediately.

---

## Cleanup performed at end of session

- Killed **3 idle Gradle daemons** (no active build; they respawn on demand): pids `875448`,
  `875921`, `1031051` (~1.6 GB combined).
- Result: **used RAM 6.5 → 4.3 GB**, **available 8 → 10 GB**, **load → 5.50**.
- The stale 9-hour orphan qemu (earlier pid `4179935`) and the swiftshader instance were already
  gone. No leftover background monitors.

## State at handoff
- **Emulator:** not running (exited during session; `adb: no devices/emulators found`).
- **WFL:** confirmed installed & launchable earlier via `:app:installDebug` + `-gpu host`.
- **Host:** healthy — load 5.50, 10 GB RAM available, all Gradle daemons closed.
- **User action in progress:** shutting down Antigravity, opening Zed. (Antigravity was NOT the load
  culprit — see correction above; user chose to close it independently.)

## If the emulator is slow again
1. Relaunch with `-gpu host` (not swiftshader).
2. Check host load first (`cat /proc/loadavg`, `vmstat 1 3`) — if `wa` is high, the encrypted disk is
   saturated; reduce concurrent disk-heavy work rather than blaming the emulator.
3. Never run parallel Gradle installs against a loaded emulator — that's what caused the ddmlib
   install timeout.
