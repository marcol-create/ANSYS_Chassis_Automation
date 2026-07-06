# =====================================================================
#  ACP (Pre) -- SCRIPT 1 of 2 : materials + stackup + rosettes
# =====================================================================
#  Run INSIDE ACP (File > Run Script), after mesh + element sets + materials.
#
#  1. Fabrics  : HC (honeycomb, 12.192), CF (carbon fiber, 0.127)
#  2. Stackup  : "Full Panel" = CF/0, CF/90, HC/0, CF/0, CF/90
#  3. Rosettes : one per element set, at the set centroid
#
#  >>> After this, adjust the rosettes manually. THEN run script 2
#      (acp_oss_plies_solids.py) to build OSS / plies / solid models.
# =====================================================================

# ---------------- CONFIG ----------------
HC_KEYS = ["honeycomb", "al_hc", "hc", "alum"]
CF_KEYS = ["carbon", "cf", "fiber", "fibre"]
HC_THICKNESS = 12.192
CF_THICKNESS = 0.127
STACKUP_NAME = "Full Panel"
SKIP_SETS = ["All_Elements"]

# ---------------- MODEL ----------------
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model
md    = model.material_data


# ---------------- HELPERS ----------------
def find_material(keys, label):
    for k in keys:
        kl = k.lower()
        for nm in md.materials.keys():
            if kl in nm.lower():
                print("%s material -> '%s'" % (label, nm))
                return md.materials[nm]
    avail = ", ".join("'%s'" % n for n in md.materials.keys())
    raise KeyError("No %s material found (tried %s). Available: [%s]"
                   % (label, keys, avail))


def _avg(arr):
    flat = list(arr)
    if not flat:
        return None
    if hasattr(flat[0], "__len__"):
        n = len(flat)
        return (sum(p[0] for p in flat) / n,
                sum(p[1] for p in flat) / n,
                sum(p[2] for p in flat) / n)
    xs, ys, zs = flat[0::3], flat[1::3], flat[2::3]
    n = len(xs)
    return (sum(xs) / n, sum(ys) / n, sum(zs) / n)


def _triples(arr):
    """Normalize a coordinate result to a list of (x, y, z) tuples."""
    flat = list(arr)
    if not flat:
        return []
    if hasattr(flat[0], "__len__"):
        return [(p[0], p[1], p[2]) for p in flat]
    return [(flat[i], flat[i + 1], flat[i + 2]) for i in range(0, len(flat) - 2, 3)]


# Snap the origin to the nearest element in the set so it always sits ON that
# face (not floating off a curved/L-shaped face or drifting onto a neighbor).
SNAP_TO_ELEMENT = True


def set_center(es):
    try:
        model.select_elements(selection="sel0", op="new", attached_to=[es])
        pts = _triples(model.mesh_query(name="coordinates", position="centroid",
                                        selection="sel0"))
        if not pts:
            return None
        n = len(pts)
        c = (sum(p[0] for p in pts) / n,
             sum(p[1] for p in pts) / n,
             sum(p[2] for p in pts) / n)
        if not SNAP_TO_ELEMENT:
            return c
        # nearest element centroid to the average -> guaranteed on this set
        best, bestd = None, None
        for p in pts:
            d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
            if bestd is None or d < bestd:
                bestd, best = d, p
        return best
    except Exception:
        return None


def target_sets():
    return [n for n in model.element_sets.keys() if n not in SKIP_SETS]


# ---------------- 1. FABRICS ----------------
hc = md.create_fabric(name="HC",
                      material=find_material(HC_KEYS, "Honeycomb"),
                      thickness=HC_THICKNESS)
cf = md.create_fabric(name="CF",
                      material=find_material(CF_KEYS, "Carbon fiber"),
                      thickness=CF_THICKNESS)
print("Fabrics created: HC (%g), CF (%g)" % (hc.thickness, cf.thickness))

# ---------------- 2. STACKUP ----------------
full = md.create_stackup(name=STACKUP_NAME)
for fab, ang in [(cf, 0.0), (cf, 90.0), (hc, 0.0), (cf, 0.0), (cf, 90.0)]:
    full.add_fabric(fab, ang)
print("Stackup '%s' created (%d fabrics)." % (STACKUP_NAME, len(full.fabrics)))

# ---------------- 3. ROSETTES ----------------
for name in target_sets():
    es = model.element_sets[name]
    origin = set_center(es) or (0.0, 0.0, 0.0)
    model.create_rosette(name, origin=origin,
                         dir1=(1.0, 0.0, 0.0), dir2=(0.0, 1.0, 0.0),
                         rosette_type="PARALLEL")
    print("Rosette '%s' at (%.3f, %.3f, %.3f)" % (name, origin[0], origin[1], origin[2]))

model.update()
print("Done -- SCRIPT 1 complete. Adjust rosettes, then run script 2.")
