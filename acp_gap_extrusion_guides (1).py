# =====================================================================
#  ACP (Pre) -- localized extrusion guides for flush seat gaps
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER acp_oss_plies_solids.py.
#
#  Each seat gap has a support passing through it. The gap walls extrude
#  along the tilted seat normal, so they meet the horizontal support along
#  one line (wedge void). This adds one extrusion guide per gap that
#  re-points that gap's edges toward its support (flattened horizontal),
#  so the walls lie flush. Pointing each gap at its own support auto-mirrors
#  L/R and avoids the sliver artifacts a single shared direction produces.
#
#  This version:
#    - REPLACE_EXISTING: deletes+recreates guides so re-runs are clean.
#    - Always ends by RAISING a summary, so the result is visible even when
#      ACP's print console is not (a silent "t=0.00s" finish means nothing
#      was created -- the summary now tells you exactly why).
# =====================================================================

# ---------------- CONFIG ----------------
SEAT_SET       = "Seat"
SEAT_ROSETTE   = "Seat"
EDGE_SETS      = ["EdgeSet1", "EdgeSet2", "EdgeSet3", "EdgeSet4"]

DIRECTION_MODE = "support"        # "support" | "seat_normal" | "fixed"
GAP_SUPPORT = {
    "EdgeSet1": "LTopVertSupp",
    "EdgeSet2": "LBottomVertSupp",
    "EdgeSet3": "RTopVertSupp",
    "EdgeSet4": "RBottomVertSupp",
}

UP_AXIS        = (0.0, 0.0, 1.0)
GUIDE_FLIP     = False
FIXED_HORIZONTAL = None

GUIDE_RADIUS   = 5.0
GUIDE_DEPTH    = 1.0

DO_UPDATE        = True
REPLACE_EXISTING = True            # delete + recreate guides that already exist

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
    es = get_item(model.element_sets, esname)
    if es is None:
        return None
    try:
        model.select_elements(selection="selC", op="new", attached_to=[es])
        return _avg(_triples(model.mesh_query(name="coordinates",
                                              position="centroid", selection="selC")))
    except Exception:
        return None

SEAT_CENTROID = set_centroid(SEAT_SET)

def horizontal_for(esname):
    if isinstance(FIXED_HORIZONTAL, dict) and esname in FIXED_HORIZONTAL:
        return _unit(tuple(FIXED_HORIZONTAL[esname])), "fixed(per-gap)"
    if DIRECTION_MODE == "support":
        sup = GAP_SUPPORT.get(esname)
        if not sup:
            return None, "no support mapped for %s" % esname
        if get_item(model.element_sets, sup) is None:
            return None, "support '%s' is not an element set (only a solid model?)" % sup
        sc = set_centroid(sup)
        if sc is None or SEAT_CENTROID is None:
            return None, "missing centroid (support='%s', seat='%s')" % (sup, SEAT_SET)
        toward = (sc[0] - SEAT_CENTROID[0], sc[1] - SEAT_CENTROID[1], sc[2] - SEAT_CENTROID[2])
        return flatten_to_horizontal(toward, UP_AXIS), "toward %s" % sup
    if DIRECTION_MODE == "fixed":
        if FIXED_HORIZONTAL is None:
            return None, "fixed mode but FIXED_HORIZONTAL not set"
        return _unit(tuple(FIXED_HORIZONTAL)), "fixed"
    n_seat = rosette_normal(get_item(model.rosettes, SEAT_ROSETTE))
    return flatten_to_horizontal(n_seat, UP_AXIS), "flattened seat normal"

def guide_exists(gname):
    try:
        return seat_sm.extrusion_guides[gname] is not None
    except Exception:
        return False

def delete_guide(gname):
    try:
        g = seat_sm.extrusion_guides[gname]
    except Exception:
        return False
    for attempt in (lambda: g.delete(),
                    lambda: seat_sm.remove_extrusion_guide(g),
                    lambda: seat_sm.remove_extrusion_guide(gname)):
        try:
            attempt()
            return True
        except Exception:
            pass
    try:
        del seat_sm.extrusion_guides[gname]
        return True
    except Exception:
        return False

# ---------------- locate the seat solid model ----------------
seat_sm = get_item(model.solid_models, SEAT_SET)
if seat_sm is None:
    raise RuntimeError("Seat solid model '%s' not found. Available: [%s]"
                       % (SEAT_SET, ", ".join(model.solid_models.keys())))

# ---------------- one guide per gap ----------------
made = 0
notes = []
for esname in EDGE_SETS:
    es = get_item(model.edge_sets, esname)
    if es is None:
        notes.append("%s: edge set NOT FOUND" % esname)
        continue

    horiz, src = horizontal_for(esname)
    if horiz is None:
        notes.append("%s: no direction (%s)" % (esname, src))
        continue
    if GUIDE_FLIP:
        horiz = (-horiz[0], -horiz[1], -horiz[2])

    gname = "%s_flush" % esname
    if guide_exists(gname):
        if REPLACE_EXISTING:
            ok = delete_guide(gname)
            if not ok:
                notes.append("%s: exists and could NOT delete (delete it in the tree)" % gname)
                continue
        else:
            notes.append("%s: already exists (REPLACE_EXISTING is off)" % gname)
            continue

    try:
        seat_sm.create_extrusion_guide(name=gname, edge_set=es,
                                       direction=horiz,
                                       radius=GUIDE_RADIUS, depth=GUIDE_DEPTH)
        made += 1
        notes.append("%s: OK dir=(%.3f,%.3f,%.3f) [%s]" % (gname, horiz[0], horiz[1], horiz[2], src))
    except Exception as ex:
        notes.append("%s: create FAILED: %s" % (esname, ex))

# ---------------- update ----------------
updated = False
if DO_UPDATE and made:
    try:
        model.update()
        updated = True
    except Exception as ex:
        notes.append("model.update() raised: %s" % ex)

# ---------------- ALWAYS-VISIBLE SUMMARY (raised so it shows in a dialog) ----------------
head = ("DONE (not an error): created %d guide(s), updated=%s. Section-cut to verify."
        % (made, updated)) if made else \
       ("NOTHING CREATED (made=0). Reasons below. "
        "edge_sets present: [%s]" % ", ".join(model.edge_sets.keys()))
raise RuntimeError(head + "  ||  " + "  ||  ".join(notes))
