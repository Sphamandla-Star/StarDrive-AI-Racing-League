# CHANGELOG

All significant changes to the racing client.
Track: Corkscrew (approximately 3 608 m). Racer: Siphamandla Radebe.

---

## Baseline

**File:** snakeoil3_v1.py (never edited — reference copy, do not modify)
**Lap time:** 03:55.07 | **Damage:** 0 | **Top speed:** 69 km/h
**Screenshot:** V1_results.png

---

## Earlier Attempts (all on snakeoil3_v2.py, all before Experiment 1)

| Change tried | Outcome | Decision |
|---|---|---|
| Corner brake factor reduced from 0.8 to 0.6 | 0 laps completed, damage 174, top speed 64 km/h | Reverted |
| `target_speed` changed from 300 to 80 | Car stuck at approximately 121 m, damage 0 | Undone |
| Brake released below 15 km/h (`if S['speedX'] < 15: R['brake'] = 0`) | Approximately 05:24, damage 0, top speed 102 km/h | Kept as v2 starting point |

---

## Experiments

### Experiment 1 — 11 October 2026

**File:** snakeoil3_v2.py
**One change:** Line 552, threshold raised from 15 to 40.

```
Before: if S['speedX'] < 15: R['brake'] = 0
After:  if S['speedX'] < 40: R['brake'] = 0
```

**Why:** Lap-log data showed the corner brake (`abs(steer) * 0.8`) rising above 0.9 at 36–40 km/h while the wheel was turned hard, stalling the car at approximately 309 m, 361 m, and 420 m. Raising the threshold to 40 km/h releases the brake across that speed range in corners.

**Result:** 03:52.86, 1 lap, damage 0, top speed 88 km/h. 2.21 s faster than v1 baseline; approximately 91 s faster than previous v2.
**Decision:** KEEP. Save point: snakeoil3_v2_clean.py.

---

## Current State

| Item | Value |
|---|---|
| Best clean lap | 03:52.86 |
| File | snakeoil3_v2.py |
| Clean save point | snakeoil3_v2_clean.py |
| Damage | 0 |
| Top speed | 88 km/h |
| Screenshot | BETTER_V2_RESULTS.png |
