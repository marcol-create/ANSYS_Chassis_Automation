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


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _unit(v):
    import math
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return None if m < 1e-9 else (v[0] / m, v[1] / m, v[2] / m)


def rosette_axes(es):
    """Compute (dir1, dir2) so the rosette normal (dir1 x dir2) is perpendicular
    to the surface and dir1 runs along the surface's LONG side.
    Returns (None, None) if it can't be determined (caller falls back)."""
    try:
        import math
        model.select_elements(selection="sel0", op="new", attached_to=[es])
        pts = _triples(model.mesh_query(name="coordinates", position="centroid",
                                        selection="sel0"))
        norms = _triples(model.mesh_query(name="normals", position="centroid",
                                          selection="sel0"))
        if len(pts) < 3 or not norms:
            return None, None

        # surface normal = averaged element normal
        N = _unit((sum(n[0] for n in norms),
                   sum(n[1] for n in norms),
                   sum(n[2] for n in norms)))
        if N is None:
            return None, None

        # centroid of the points
        m = len(pts)
        c = (sum(p[0] for p in pts) / m,
             sum(p[1] for p in pts) / m,
             sum(p[2] for p in pts) / m)

        # in-plane orthonormal basis (u, v) perpendicular to N
        seed = [0.0, 0.0, 0.0]
        seed[min(range(3), key=lambda i: abs(N[i]))] = 1.0   # axis least aligned with N
        u = _unit(_cross(N, tuple(seed)))
        if u is None:
            return None, None
        v = _cross(N, u)                                     # unit (N,u orthonormal)

        # project points into (a, b) and build the 2x2 covariance
        A, Saa, Sbb, Sab = [], 0.0, 0.0, 0.0
        for p in pts:
            d = (p[0] - c[0], p[1] - c[1], p[2] - c[2])
            a = d[0] * u[0] + d[1] * u[1] + d[2] * u[2]
            b = d[0] * v[0] + d[1] * v[1] + d[2] * v[2]
            A.append((a, b))
            Saa += a * a; Sbb += b * b; Sab += a * b

        # principal axis angle, then pick whichever of theta / theta+90 is longer
        theta = 0.5 * math.atan2(2.0 * Sab, Saa - Sbb)

        def extent(th):
            ca, sa = math.cos(th), math.sin(th)
            proj = [a * ca + b * sa for (a, b) in A]
            return max(proj) - min(proj)

        if extent(theta + math.pi / 2.0) > extent(theta):
            theta += math.pi / 2.0

        ca, sa = math.cos(theta), math.sin(theta)
        dir1 = _unit((ca * u[0] + sa * v[0],
                      ca * u[1] + sa * v[1],
                      ca * u[2] + sa * v[2]))
        if dir1 is None:
            return None, None
        dir2 = _cross(N, dir1)          # in-plane; dir1 x dir2 == N (perp to surface)
        return dir1, dir2
    except Exception:
        return None, None


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
