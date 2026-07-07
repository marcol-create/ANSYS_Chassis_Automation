# =====================================================================
#  ACP (Pre) -- localized extrusion guides for flush seat gaps
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER acp_oss_plies_solids.py --
#  i.e. after the rosettes, OSSs, modeling groups and solid models exist
#  and have been updated once.
#
#  Each seat gap has a support passing through it. The gap walls extrude
#  along the tilted seat normal, so they meet the horizontal support along
#  one line, leaving a wedge void. This adds ONE extrusion guide per gap
#  that re-points only that gap's edges toward its support (horizontal), so
#  the walls lie flush.
#
#  DIRECTION (fixes the left/right sliver asymmetry):
#    A single world-space vector cannot be symmetric for mirror-symmetric
#    gaps -- it sweeps one side correctly and the mirror side the wrong way,
#    producing degenerate sliver/patch elements. So each gap gets its OWN
#    direction, pointing from the seat toward the support that passes through
#    that gap (support_centroid - seat_centroid, flattened horizontal). That
#    auto-mirrors, so left and right behave identically.
# =====================================================================

# ---------------- CONFIG ----------------
SEAT_SET       = "Seat"          # seat solid model / element set / rosette name
SEAT_ROSETTE   = "Seat"
EDGE_SETS      = ["EdgeSet1", "EdgeSet2", "EdgeSet3", "EdgeSet4"]

# How each gap's guide direction is chosen:
#   "support"     -> point toward the support passing through the gap  (RECOMMENDED,
#                    auto-mirrors L/R). Requires GAP_SUPPORT below.
#   "seat_normal" -> single flattened seat normal for all gaps  (the old behaviour;
#                    causes the L/R asymmetry on mirror-symmetric gaps).
#   "fixed"       -> use FIXED_HORIZONTAL for all gaps.
DIRECTION_MODE = "support"

# EDIT so each edge set maps to the support that goes through that gap:
GAP_SUPPORT = {
    "EdgeSet1": "LTopVertSupp",
    "EdgeSet2": "LBottomVertSupp",
    "EdgeSet3": "RTopVertSupp",
    "EdgeSet4": "RBottomVertSupp",
}

UP_AXIS        = (0.0, 0.0, 1.0)  # vertical axis; use (0,1,0) if Y is up
GUIDE_FLIP     = False            # global flip if EVERY gap points the wrong way
FIXED_HORIZONTAL = None           # (x,y,z), or a per-gap dict, for DIRECTION_MODE="fixed"

GUIDE_RADIUS   = 5.0              # tight sphere of influence -> keeps the tilt local
GUIDE_DEPTH    = 1.0

DO_UPDATE      = True
SKIP_IF_EXISTS = True

# ---------------- MODEL ----------------
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

# ---------------- HELPERS ----------------
import math

def _unit(v):
    if v is None:
        return None
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return None if m < 1e-9 else (v[0] / m, v[1] / m, v[2] / m)

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def _triples(arr):
    flat = list(arr)
    if not flat:
        return []
    if hasattr(flat[0], "__len__"):
        return [(p[0], p[1], p[2]) for p in flat]
    return [(flat[i], flat[i + 1], flat[i + 2]) for i in range(0, len(flat) - 2, 3)]

def _avg(pts):
    pts = list(pts)
    if not pts:
        return None
    n = len(pts)
    return (sum(p[0] for p in pts) / n,
            sum(p[1] for p in pts) / n,
            sum(p[2] for p in pts) / n)

def get_item(collection, name):
    try:
        return collection[name]
    except Exception:
        return None

def rosette_normal(ros):
    if ros is None:
        return None
    for a in ["normal", "dir3", "dir_3", "direction_3", "z_direction", "n"]:
        try:
            u = _unit(tuple(getattr(ros, a)))
            if u:
                return u
        except Exception:
            pass
    for a1, a2 in [("dir1", "dir2"), ("dir_1", "dir_2"),
                   ("direction_1", "direction_2"), ("x_direction", "y_direction")]:
        try:
            u = _unit(_cross(tuple(getattr(ros, a1)), tuple(getattr(ros, a2))))
            if u:
                return u
        except Exception:
            pass
    return None

def flatten_to_horizontal(v, up):
    up = _unit(up)
    if up is None or v is None:
        return None
    d = v[0] * up[0] + v[1] * up[1] + v[2] * up[2]
    return _unit((v[0] - d * up[0], v[1] - d * up[1], v[2] - d * up[2]))

def set_centroid(esname):
    """Average element centroid of an element set -> (x,y,z), or None."""
    es = get_item(model.element_sets, esname)
    if es is None:
        return None
    try:
        model.select_elements(selection="selC", op="new", attached_to=[es])
        return _avg(_triples(model.mesh_query(name="coordinates",
                                              position="centroid", selection="selC")))
    except Exception:
        return None

# seat centroid, computed once
SEAT_CENTROID = set_centroid(SEAT_SET)

def horizontal_for(esname):
    """Resolve this gap's horizontal guide direction -> (vec, source)."""
    if isinstance(FIXED_HORIZONTAL, dict) and esname in FIXED_HORIZONTAL:
        return _unit(tuple(FIXED_HORIZONTAL[esname])), "fixed(per-gap)"

    if DIRECTION_MODE == "support":
        sup = GAP_SUPPORT.get(esname)
        if not sup:
            return None, "no support mapped"
        sc = set_centroid(sup)
        if sc is None or SEAT_CENTROID is None:
            return None, "missing centroid (support='%s')" % sup
        toward = (sc[0] - SEAT_CENTROID[0],
                  sc[1] - SEAT_CENTROID[1],
                  sc[2] - SEAT_CENTROID[2])
        return flatten_to_horizontal(toward, UP_AXIS), "toward %s" % sup

    if DIRECTION_MODE == "fixed":
        if FIXED_HORIZONTAL is None:
            return None, "fixed mode but FIXED_HORIZONTAL not set"
        return _unit(tuple(FIXED_HORIZONTAL)), "fixed"

    # seat_normal (old behaviour)
    n_seat = rosette_normal(get_item(model.rosettes, SEAT_ROSETTE))
    return flatten_to_horizontal(n_seat, UP_AXIS), "flattened seat normal"

# ---------------- locate the seat solid model ----------------
seat_sm = get_item(model.solid_models, SEAT_SET)
if seat_sm is None:
    raise RuntimeError("Seat solid model '%s' not found. Available: [%s]"
                       % (SEAT_SET, ", ".join(model.solid_models.keys())))

# ---------------- one guide per gap ----------------
made, skipped = 0, 0
for esname in EDGE_SETS:
    es = get_item(model.edge_sets, esname)
    if es is None:
        print("  SKIP '%s' -- edge set not found. Available: [%s]"
              % (esname, ", ".join(model.edge_sets.keys())))
        continue

    horiz, src = horizontal_for(esname)
    if horiz is None:
        print("  SKIP '%s' -- could not resolve direction (%s)." % (esname, src))
        continue
    if GUIDE_FLIP:
        horiz = (-horiz[0], -horiz[1], -horiz[2])

    gname = "%s_flush" % esname
    if SKIP_IF_EXISTS:
        try:
            if seat_sm.extrusion_guides[gname] is not None:
                print("  '%s' already exists -- skipping (delete it to recreate)" % gname)
                skipped += 1
                continue
        except Exception:
            pass

    try:
        seat_sm.create_extrusion_guide(
            name=gname,
            edge_set=es,
            direction=horiz,
            radius=GUIDE_RADIUS,
            depth=GUIDE_DEPTH)
        made += 1
        print("  guide '%s'  dir=(%.4f, %.4f, %.4f) [%s]"
              % (gname, horiz[0], horiz[1], horiz[2], src))
    except Exception as ex:
        raise RuntimeError("create_extrusion_guide failed for '%s': %s" % (esname, ex))

print("Guides created: %d   skipped: %d   of %d." % (made, skipped, len(EDGE_SETS)))

# ---------------- update + shape check ----------------
if DO_UPDATE and made:
    try:
        model.update()
        print("Update complete. Section-cut each gap:")
        print("  - wedge closed, no slivers  -> done.")
        print("  - a gap's wedge got WIDER   -> that support mapping/side is reversed;")
        print("                                 check GAP_SUPPORT for that edge set.")
        print("  - slivers persist on a gap  -> lower GUIDE_RADIUS, or split that gap's")
        print("                                 third edge (the one along the direction)")
        print("                                 onto its own edge set + guide.")
    except Exception as ex:
        print("Update raised: %s" % ex)
else:
    print("Skipped update (no new guides, or DO_UPDATE off).")
