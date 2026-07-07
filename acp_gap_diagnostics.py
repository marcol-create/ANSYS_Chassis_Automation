# =====================================================================
#  ACP (Pre) -- DIAGNOSTICS for the seat gap extrusion guides
# =====================================================================
#  Read-only. Creates nothing. Raises a summary dialog with:
#    - seat mesh scale (element count + bounding box)
#    - whether node-coordinate queries even work in this version
#    - per edge set: node count, extents, dominant direction, and the ANGLE
#      between that edge set and its intended guide direction. An angle near
#      0 or 180 deg means that gap has an edge running ALONG the sweep
#      direction -> it will degenerate into slivers no matter the radius.
# =====================================================================

SEAT_SET  = "Seat"
EDGE_SETS = ["EdgeSet1", "EdgeSet2", "EdgeSet3", "EdgeSet4"]
GUIDE_DIR = {   # the directions currently in use (for the angle comparison)
    "EdgeSet1": (0.980, -0.199, 0.0),
    "EdgeSet2": (0.971, -0.239, 0.0),
    "EdgeSet3": (0.980,  0.199, 0.0),
    "EdgeSet4": (0.971,  0.239, 0.0),
}

try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

import math

def _triples(arr):
    flat = list(arr)
    if not flat:
        return []
    if hasattr(flat[0], "__len__"):
        return [(p[0], p[1], p[2]) for p in flat]
    return [(flat[i], flat[i + 1], flat[i + 2]) for i in range(0, len(flat) - 2, 3)]

def _unit(v):
    m = math.sqrt(sum(c * c for c in v))
    return None if m < 1e-9 else tuple(c / m for c in v)

def get_item(coll, name):
    try:
        return coll[name]
    except Exception:
        return None

def node_coords_of(setname, kind):
    """Try to pull node coordinates for an element set or edge set. Returns
    (list_of_xyz, method_string)."""
    obj = get_item(model.element_sets if kind == "elem" else model.edge_sets, setname)
    if obj is None:
        return [], "set '%s' not found in %s" % (setname, kind)
    # try node selection
    for sel_call, q in (
        (lambda: model.select_nodes(selection="selD", op="new", attached_to=[obj]),
         lambda: model.mesh_query(name="coordinates", selection="selD")),
        (lambda: model.select_elements(selection="selD", op="new", attached_to=[obj]),
         lambda: model.mesh_query(name="coordinates", position="nodal", selection="selD")),
        (lambda: model.select_elements(selection="selD", op="new", attached_to=[obj]),
         lambda: model.mesh_query(name="coordinates", position="centroid", selection="selD")),
    ):
        try:
            sel_call()
            pts = _triples(q())
            if pts:
                return pts, "ok"
        except Exception as e:
            last = str(e)
    return [], "no coord query worked (last: %s)" % (last if 'last' in dir() else "n/a")

def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

def dominant_dir(pts):
    """Rough dominant direction: axis of largest extent between the two most
    separated points (cheap, no numpy)."""
    if len(pts) < 2:
        return None
    # farthest pair by sampling extremes along each axis
    import itertools
    cand = []
    for ax in range(3):
        lo = min(pts, key=lambda p: p[ax]); hi = max(pts, key=lambda p: p[ax])
        cand.append((lo, hi))
    best, bestd = None, -1
    for a, b in cand:
        d = sum((a[i] - b[i]) ** 2 for i in range(3))
        if d > bestd:
            bestd, best = d, (a, b)
    a, b = best
    return _unit((b[0] - a[0], b[1] - a[1], b[2] - a[2]))

notes = []

# --- seat scale ---
seat_es = get_item(model.element_sets, SEAT_SET)
seat_sm = get_item(model.solid_models, SEAT_SET)
n_elem = "?"
try:
    n_elem = len(list(seat_sm.elements)) if seat_sm is not None else "?"
except Exception:
    pass
pts, m = node_coords_of(SEAT_SET, "elem")
if pts:
    x0, x1, y0, y1, z0, z1 = bbox(pts)
    notes.append("SEAT: nodes=%d bbox X[%.0f..%.0f] Y[%.0f..%.0f] Z[%.0f..%.0f] (coord query: %s)"
                 % (len(pts), x0, x1, y0, y1, z0, z1, m))
else:
    notes.append("SEAT coord query FAILED: %s" % m)

# --- each edge set ---
for esn in EDGE_SETS:
    pts, m = node_coords_of(esn, "edge")
    if not pts:
        notes.append("%s: coord query FAILED (%s)" % (esn, m))
        continue
    x0, x1, y0, y1, z0, z1 = bbox(pts)
    dd = dominant_dir(pts)
    g = _unit(GUIDE_DIR.get(esn, (1, 0, 0)))
    ang = None
    if dd and g:
        dot = max(-1.0, min(1.0, sum(dd[i] * g[i] for i in range(3))))
        ang = math.degrees(math.acos(abs(dot)))   # 0 = parallel to guide (BAD)
    notes.append("%s: nodes=%d span(X%.0f,Y%.0f,Z%.0f) dom=(%.2f,%.2f,%.2f) "
                 "angle_to_guide=%s deg %s"
                 % (esn, len(pts), x1 - x0, y1 - y0, z1 - z0,
                    dd[0] if dd else 0, dd[1] if dd else 0, dd[2] if dd else 0,
                    ("%.0f" % ang) if ang is not None else "n/a",
                    "<-- near-parallel, will sliver" if (ang is not None and ang < 25) else ""))

raise RuntimeError("DIAGNOSTICS || seat_elem_count=%s || %s" % (n_elem, "  ||  ".join(notes)))
