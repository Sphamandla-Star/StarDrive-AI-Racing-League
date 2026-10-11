"""
find_corners.py
Reads lap_data.csv (written by snakeoil3_v2.py) and reports:
  1. Corner zones  – straight-ahead sensor < 40 m
  2. Straight zones – straight-ahead sensor > 150 m
  3. Damage events  – rows where cumulative damage increased
Rows before the standing start (speedX <= 1 m/s for the first N rows)
are skipped automatically.
"""

import csv
import sys

CSV_FILE = 'lap_data.csv'
CORNER_THRESH  = 40.0   # m  – wall is close ahead → cornering
STRAIGHT_THRESH = 150.0  # m  – clear road ahead   → straight
MOTION_THRESH  = 1.0    # m/s – below this = car hasn't launched yet


def load_rows(path):
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'distFromStart': float(r['distFromStart']),
                'speedX':        float(r['speedX']),
                'trackPos':      float(r['trackPos']),
                'angle':         float(r['angle']),
                'steer':         float(r['steer']),
                'accel':         float(r['accel']),
                'brake':         float(r['brake']),
                'gear':          float(r['gear']),
                'track_straight': float(r['track_straight']),
                'damage':        float(r['damage']),
            })
    return rows


def skip_standing_start(rows):
    """Drop leading rows where the car has never moved yet."""
    for i, r in enumerate(rows):
        if r['speedX'] > MOTION_THRESH:
            return rows[i:]
    return []  # never moved at all


def find_zones(rows, sensor_lo, sensor_hi):
    """
    Return a list of zone dicts for rows where
    sensor_lo <= track_straight <= sensor_hi.
    Each zone: { start_dist, end_dist, min_speed, min_edge_dist, rows }
    """
    zones = []
    in_zone = False
    zone_rows = []

    for r in rows:
        ts = r['track_straight']
        inside = sensor_lo <= ts <= sensor_hi
        if inside:
            if not in_zone:
                in_zone = True
                zone_rows = []
            zone_rows.append(r)
        else:
            if in_zone:
                zones.append(zone_rows)
                zone_rows = []
            in_zone = False
    if in_zone and zone_rows:
        zones.append(zone_rows)

    result = []
    for zr in zones:
        min_speed = min(r['speedX'] for r in zr)
        # edge distance: |trackPos| 1.0 = edge; convert to fraction of half-width
        # smaller |trackPos| = closer to centre; larger = closer to edge
        max_edge_closeness = max(abs(r['trackPos']) for r in zr)
        result.append({
            'start_dist':      zr[0]['distFromStart'],
            'end_dist':        zr[-1]['distFromStart'],
            'min_speed':       min_speed,
            'max_edge_abs':    max_edge_closeness,  # 1.0 = at the wall
            'n_rows':          len(zr),
        })
    return result


def find_damage_events(rows):
    events = []
    prev_dmg = rows[0]['damage'] if rows else 0.0
    for i, r in enumerate(rows[1:], start=1):
        if r['damage'] > prev_dmg:
            events.append({
                'row':         i,
                'distFromStart': r['distFromStart'],
                'speedX':      r['speedX'],
                'trackPos':    r['trackPos'],
                'delta':       r['damage'] - prev_dmg,
                'total':       r['damage'],
            })
        prev_dmg = r['damage']
    return events


def print_section(title):
    print()
    print('=' * 60)
    print(title)
    print('=' * 60)


def main():
    try:
        all_rows = load_rows(CSV_FILE)
    except FileNotFoundError:
        print(f"ERROR: {CSV_FILE} not found. Run snakeoil3_v2.py first.")
        sys.exit(1)

    if not all_rows:
        print("ERROR: CSV is empty.")
        sys.exit(1)

    rows = skip_standing_start(all_rows)
    skipped = len(all_rows) - len(rows)

    print(f"Loaded {len(all_rows)} rows total.")
    print(f"Skipped {skipped} standing-start rows (speedX <= {MOTION_THRESH} m/s).")
    print(f"Analysing {len(rows)} in-motion rows.")

    if not rows:
        print()
        print("*** The car never moved. ***")
        print("All rows have speedX <= %.4f m/s." % MOTION_THRESH)
        print()
        print("Likely causes:")
        print("  1. TORCS server is not running or is paused.")
        print("  2. The race has not been started (still on grid).")
        print("  3. accel is being sent but the socket loop exits before")
        print("     the car actually gets a green light.")
        print()
        print("The telemetry captured the pre-race wait period only.")
        print("No corners, straights, or damage events to report.")
        return

    # ── 1. Corner zones ──────────────────────────────────────────
    print_section("1. CORNER ZONES  (track_straight < 40 m)")
    corners = find_zones(rows, 0.0, CORNER_THRESH)
    if not corners:
        print("  None found.")
    else:
        for i, z in enumerate(corners, 1):
            print(f"  Corner {i:>3}: dist {z['start_dist']:>8.1f} m → {z['end_dist']:>8.1f} m"
                  f"  |  min speed {z['min_speed']:>7.2f} m/s"
                  f"  |  max |trackPos| {z['max_edge_abs']:.3f}"
                  f"  |  {z['n_rows']} steps")

    # ── 2. Straight zones ─────────────────────────────────────────
    print_section("2. STRAIGHT ZONES  (track_straight > 150 m)")
    straights = find_zones(rows, STRAIGHT_THRESH, float('inf'))
    if not straights:
        print("  None found.")
    else:
        for i, z in enumerate(straights, 1):
            print(f"  Straight {i:>3}: dist {z['start_dist']:>8.1f} m → {z['end_dist']:>8.1f} m"
                  f"  |  min speed {z['min_speed']:>7.2f} m/s"
                  f"  |  {z['n_rows']} steps")

    # ── 3. Damage events ──────────────────────────────────────────
    print_section("3. DAMAGE EVENTS  (damage increased)")
    events = find_damage_events(rows)
    if not events:
        print("  No damage recorded.")
    else:
        for e in events:
            print(f"  row {e['row']:>6}  dist {e['distFromStart']:>8.1f} m"
                  f"  |  speed {e['speedX']:>7.2f} m/s"
                  f"  |  trackPos {e['trackPos']:>+.3f}"
                  f"  |  +{e['delta']:.1f} dmg (total {e['total']:.1f})")

    print()
    print(f"Done. ({len(corners)} corner zone(s), "
          f"{len(straights)} straight zone(s), "
          f"{len(events)} damage event(s))")


if __name__ == '__main__':
    main()
