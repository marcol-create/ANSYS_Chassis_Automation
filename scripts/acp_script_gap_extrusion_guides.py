# =====================================================================
#  ACP (Pre) -- SCRIPT 3 : localized extrusion guides for flush gaps
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER Script 2 -- i.e. after the
#  rosettes, OSSs, modeling groups and solid models already exist and
#  have been updated at least once.
#
#  PROBLEM
#    The seat wall sits at ~65 deg and (correctly) extrudes NORMAL to its
#    own face -- rosette driven. A horizontal support slab passes through
#    each of the 4 gaps (EdgeSet1..4, 3 edges each). Because the gap walls
#    extrude along the tilted seat normal, they only kiss the horizontal
#    support along one line -> the wedge void you see in the section cuts.
#
#  WHAT THIS DOES
#    Adds ONE extrusion guide per gap, scoped to that gap's edge set, that
#    re-points ONLY those edges along a HORIZONTAL direction. The seat body
#    keeps extruding normal everywhere; the 4 gap walls drop to horizontal
#    so they lie flush against the supports.
#
#    Angle is handled here. Gap POSITION / SIZE is handled separately in the
#    geometry (grow/shift the slot so it seats the support) -- as intended.
#
#  DIRECTION
#    "Horizontal" is a plane, so the wall only comes out horizontal if the
#    edges are swept along the horizontal direction that points ACROSS the
#    slot (the way the support travels). That is derived here by taking the
#    seat's own normal (from its rosette) and flattening the vertical
#    component. Override with FIXED_HORIZONTAL if your layout needs it.
# =====================================================================

# ---------------- CONFIG ----------------
SEAT_SET        = "Seat"          # element-set / solid-model name of the seat
SEAT_ROSETTE    = "Seat"          # rosette whose normal == seat face normal
EDGE_SETS       = ["EdgeSet1", "EdgeSet2", "EdgeSet3", "EdgeSet4"]

UP_AXIS         = (0.0, 0.0, 1.0) # vertical axis; use (0,1,0) if Y is your up-axis
GUIDE_FLIP      = False           # negate the horizontal dir if the wedge gets WORSE
FIXED_HORIZONTAL = None           # e.g. (1.0, 0.0, 0.0) to override the derived dir
                                  # (or a dict {"EdgeSet1": (..), ...} for per-gap dirs)

GUIDE_RADIUS    = 5.0             # tight sphere of influence (model units) -> stays local
GUIDE_DEPTH     = 1.0
# NOTE: this compolyx version infers the guide type from the arguments -- passing
# `direction` (with cad_geometry left at None) makes it a by-direction guide
# automatically. There is no extrusion_guide_type argument in this signature.

DO_UPDATE       = True            # run model.update() at the end
SKIP_IF_EXISTS  = True            # don't recreate a guide that is already there

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
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return None if m < 1e-9 else (v[0] / m, v[1] / m, v[2] / m)

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def get_item(collection, name):
    try:
        return collection[name]
    except Exception:
        return None

def rosette_normal(ros):
    """3rd axis (normal) of a rosette. Tries a direct normal attr, else dir1 x dir2.
    Mirrors the lookup used in Script 2 so it survives naming differences."""
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
    """Remove the vertical (up) component so the vector lies in the ground plane."""
    up = _unit(up)
    if up is None or v is None:
        return None
    d = v[0] * up[0] + v[1] * up[1] + v[2] * up[2]
    return _unit((v[0] - d * up[0], v[1] - d * up[1], v[2] - d * up[2]))

def horizontal_for(esname):
    """Resolve the horizontal guide direction for one edge set."""
    # per-gap override dict
    if isinstance(FIXED_HORIZONTAL, dict):
        if esname in FIXED_HORIZONTAL:
            return _unit(tuple(FIXED_HORIZONTAL[esname])), "fixed(per-gap)"
    # single global override
    elif FIXED_HORIZONTAL is not None:
        return _unit(tuple(FIXED_HORIZONTAL)), "fixed"
    # derived: flatten the seat normal
    n_seat = rosette_normal(get_item(model.rosettes, SEAT_ROSETTE))
    if n_seat is None:
        return None, "no-seat-normal"
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
        print("  SKIP '%s' -- could not resolve a horizontal direction (%s). "
              "Set FIXED_HORIZONTAL." % (esname, src))
        continue
    if GUIDE_FLIP:
        horiz = (-horiz[0], -horiz[1], -horiz[2])

    gname = "%s_flush" % esname

    # idempotency: skip if a guide of this name is already on the solid model
    if SKIP_IF_EXISTS:
        existing = None
        try:
            existing = seat_sm.extrusion_guides[gname]
        except Exception:
            existing = None
        if existing is not None:
            print("  '%s' already exists -- skipping (delete it to recreate)" % gname)
            skipped += 1
            continue

    try:
        seat_sm.create_extrusion_guide(
            name=gname,
            edge_set=es,
            direction=horiz,
            radius=GUIDE_RADIUS,
            depth=GUIDE_DEPTH)
        made += 1
        print("  guide '%s' on '%s'  dir=(%.4f, %.4f, %.4f) [%s]"
              % (gname, SEAT_SET, horiz[0], horiz[1], horiz[2], src))
    except Exception as ex:
        # Fail LOUD: in ACP's Run Script, print() goes to a console you may not
        # see, so a swallowed error looks like a silent no-op. Re-raise so the
        # real reason lands in a dialog.
        raise RuntimeError("create_extrusion_guide failed for '%s': %s" % (esname, ex))

print("Guides created: %d   skipped (existing): %d   of %d edge sets."
      % (made, skipped, len(EDGE_SETS)))

# ---------------- update + shape-check feedback ----------------
if DO_UPDATE and made:
    try:
        model.update()
        print("Update complete. Inspect a section cut through each gap:")
        print("  - wedge CLOSED, wall flat on support -> done.")
        print("  - wedge WIDER               -> set GUIDE_FLIP = True and re-run.")
        print("  - wall warped / distorted   -> lower GUIDE_RADIUS, or split the")
        print("                                 3-edge set so the edge running along")
        print("                                 the guide direction gets its own guide.")
    except Exception as ex:
        print("Update raised: %s" % ex)
else:
    print("Skipped update (no new guides, or DO_UPDATE off).")
