# Experiment Report 1

**Date:** 11 October 2026
**Track:** Corkscrew (approximately 3 608 m)
**File raced:** snakeoil3_v2.py
**Racer:** Siphamandla Radebe (solo entry)

---

## Summary Table

| Row | Value |
|-----|-------|
| **Baseline** | snakeoil3_v1.py (never edited): 03:55.07, damage 0, top speed 69 km/h (screenshot V1_results.png) |
| **Hypothesis** | Above 15 km/h the corner brake (`abs(steer) * 0.8`) comes back while the wheel is still turned hard, so the car is pulled down to a crawl in corners and restarts slowly. Releasing the brake up to 40 km/h should reduce this. *(Hypothesis — not proven by the data.)* |
| **AI recommendation** | Change line 552: `if S['speedX'] < 15: R['brake'] = 0` → `if S['speedX'] < 40: R['brake'] = 0` |
| **Change made** | Line 552 of snakeoil3_v2.py: threshold changed from 15 to 40. One line only. |
| **Predicted result** | [Car will finish less quicker than the last lap |
| **Actual lap time** | 03:24.86.15 (1 lap, screenshot FINAL_V2_RESULTS.png) |
| **Damage** | 0 |
| **Top speed** | 88 km/h |
| **What surprised us** | [CAR WAS FASTER BUT NOT FAST ENOUGH TO COMPLETE THE LAB IN LESS THAN 2MIN] |
| **Keep / modify / revert** | KEEP — damage 0, lap faster than both earlier laps. Save point: snakeoil3_v2_clean.py |
| **Next experiment** | [TRY TO MAKE THE CAR COMPLETE THE LAP IN LESS THAN 2MINS] |

---

## Evidence from the Lap Data

- Log file: 63 435 rows, two runs. Neither run finished a lap.
- **Run 1:** car spun out. Damage reached 169 at approximately 80 m and 252 by the end of the run.
  - At 44.6 m: speed 39.4 km/h, steer 1.15, brake 0.92.
  - At 57.0 m: speed 36.4 km/h, brake 1.0.
- **Run 2:** damage 0, but the car stopped at approximately 309 m, 361 m, and 420 m.
  - At each of the three stops the brake value was already 0 in the log, so the log shows what led up to the stops, not proof of their cause.
- The last 58 285 rows of the log are identical because TORCS stopped updating.

*These observations are consistent with the hypothesis but do not prove it.*

---

## Code Facts

The following lines of snakeoil3_v2.py were relevant to this experiment (none of these were changed except line 552):

| Line | Code |
|------|------|
| 533 | `target_speed = 300` |
| 536 | `R['steer'] = S['angle'] * 15 / PI` |
| 551 | `R['brake'] = clip(abs(R['steer']) * 0.8, 0, 1)` |
| 552 (before) | `if S['speedX'] < 15: R['brake'] = 0` |
| 552 (after) | `if S['speedX'] < 40: R['brake'] = 0` |

---

## Analysis (with Limits)

The lap time improved by 2.21 seconds relative to the v1 baseline (03:55.07 → 03:52.86) and by approximately 91 seconds relative to the previous v2 run (approximately 05:24 → 03:52.86). Damage was 0 in the final run.

The lap-log data from the pre-change runs shows the brake rising above 0.9 at speeds of 36–40 km/h while the wheel was turned hard. This is consistent with the hypothesis that the corner-brake formula was holding the car back in slow corners. However:

- Only one race was run after the change. No control lap was run with the change reverted.
- The Session 3 deck measured approximately 0.55 s of run-to-run noise on the coach's machine. Run-to-run noise on this machine has not been measured.
- The improvement of 2.21 s over v1 is larger than the measured noise floor on the coach's machine, but this cannot be confirmed for this machine.
- The log data shows what happened before the stops, not the direct cause of the stops.

---

## Decision and Why

**Decision: KEEP.**

Damage is 0 and the lap time (03:52.86) is faster than both the v1 baseline (03:55.07) and the previous v2 run (approximately 05:24). The change is minimal (one integer on one line). The clean save point is snakeoil3_v2_clean.py.

---

## Ideas Not Tested

- **Softer steering gain (line 536):** `R['steer'] = S['angle'] * 15 / PI` — the car reaches full lock at approximately 0.21 rad. A smaller multiplier might reduce peak brake values.
- **Corner brake only above a steer threshold:** apply `clip(abs(R['steer']) * 0.8, 0, 1)` only when `abs(R['steer'])` exceeds approximately 0.3 to avoid braking on near-straight sections.
- **Intermediate release speeds:** trying thresholds of 20–30 km/h instead of 40 km/h to find a tighter optimum.

---

## Bob Prompts and Answers

### Prompt 1

> Ask mode. Do not change any files.
> Open snakeoil3_v2.py. Quote with line numbers: (1) the line containing target_speed, (2) the line starting R['brake'] = clip(abs(R['steer']), (3) any line containing R['brake'] = 0, (4) the line that sets R['steer'] from S['angle'].
> For each one say whether it exists, yes or no. Do not guess and do not invent numbers.

### Answer 1

Here are the exact quoted lines, with their line numbers, and whether each exists:

**(1) The line containing `target_speed`**

> **Line 533:** `    target_speed=300`

**Exists: YES**

**(2) The line starting `R['brake'] = clip(abs(R['steer'])`**

> **Line 551:** `    R['brake'] = clip(abs(R['steer']) * 0.8, 0, 1)`

**Exists: YES**

**(3) Any line containing `R['brake'] = 0`**

> **Line 552:** `    if S['speedX'] < 15: R['brake'] = 0`

**Exists: YES**

**(4) The line that sets `R['steer']` from `S['angle']`**

> **Line 536:** `    R['steer']= S['angle']*15 / PI`

**Exists: YES**

---

### Prompt 2

> Agent mode. Edit ONLY snakeoil3_v2.py. Do not touch snakeoil3_v1.py or snakeoil3_v2_clean.py. Do not create new files.
> Evidence: in my last lap log, whenever the wheel was turned hard at about 36 to 42 km/h, the brake was 0.9 to 1.0 and the car stalled (stopped at about 309 m, 360 m and 420 m).
> My file has one added line that releases the brake only below 15 km/h: if S['speedX'] < 15: R['brake'] = 0
> Make exactly ONE change: change 15 to 40 in that line only.
> Change nothing else: not target_speed, not the 0.8, not the telemetry, not the indentation.
> Show me the line before and after, with its line number. Do not run anything.

### Answer 2

**Line 552 — before and after:**

| | Code |
|---|---|
| **Before** | `    if S['speedX'] < 15: R['brake'] = 0` |
| **After** | `    if S['speedX'] < 40: R['brake'] = 0` |

Only the threshold value changed from `15` to `40`. Everything else — the `0.8` factor, `target_speed`, indentation, and all other lines — is untouched.
