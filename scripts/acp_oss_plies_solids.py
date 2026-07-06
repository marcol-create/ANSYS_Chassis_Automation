# =====================================================================
#  ACP (Pre) -- SCRIPT 2 of 2 : OSS + modeling groups/plies + solid models
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER script 1 and AFTER you have
#  finalized the rosettes (each OSS locks in its rosette at creation).
#
#  4. OSS      : one per element set, scoped to the set, reference
#                direction = same-named rosette
#  5. Modeling : one modeling group per set, each with one ply
#                (OSS = same-named set, ply material = "Full Panel")
#  6. Solids   : one solid model per set, that set in extrusion element sets
# =====================================================================

# ---------------- CONFIG ----------------
STACKUP_NAME = "Full Panel"
SKIP_SETS = ["All_Elements"]
DEFAULT_ORIENT_DIR = (0.0, 0.0, 1.0)   # OSS lay-up direction (adjust later)
PLY_ANGLE = 0.0
EX_TYPE = "analysis_ply_wise"          # solid model extrusion method
MONOLITHIC_SETS = set()                # e.g. {"Back Roof"} to use monolithic instead

# How each OSS orientation direction is chosen:
#   "rosette"    -> use the rosette's own normal (per-surface, as you set it)
#   "radial_out" -> point outward from the chassis center
#   "radial_in"  -> point inward toward the chassis center
#   "mesh"       -> use the face's average element normal
#   "fixed"      -> use DEFAULT_ORIENT_DIR for all
ORIENT_MODE = "rosette"
# Negate the chosen direction. Your rosette points along the offset and the
# extrusion is inward (opposite), so flip is on. Turn off if it extrudes wrong.
ORIENT_FLIP = True
# Chassis reference point for the radial modes. None = whole-mesh centroid.
ORIENT_CENTER = None

# ---------------- MODEL ----------------
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model
md    = model.material_data


# ---------------- HELPERS ----------------
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


def set_center(es):
    try:
        model.select_elements(selection="sel0", op="new", attached_to=[es])
        coords = model.mesh_query(name="coordinates", position="centroid",
                                  selection="sel0")
        return _avg(coords)
    except Exception:
        return None


def set_normal(es):
    """Average, normalized element normal of a set -> unit (x,y,z), or None."""
    try:
        import math
        model.select_elements(selection="sel1", op="new", attached_to=[es])
        norms = model.mesh_query(name="normals", position="centroid",
                                 selection="sel1")
        avg = _avg(norms)
        if avg is None:
            return None
        mag = math.sqrt(avg[0] ** 2 + avg[1] ** 2 + avg[2] ** 2)
        if mag < 1e-9:
            return None
        return (avg[0] / mag, avg[1] / mag, avg[2] / mag)
    except Exception:
        return None


def get_item(collection, name):
    try:
        return collection[name]
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


def rosette_normal(ros):
    """Normal (3rd axis) of a rosette, so the OSS orientation follows the
    rosette the user set. Tries a direct normal attr, else crosses the two
    in-plane direction vectors. Returns unit (x,y,z) or None."""
    if ros is None:
        return None
    # (a) a direct normal / 3rd-direction attribute
    for a in ["normal", "dir3", "dir_3", "direction_3", "z_direction", "n"]:
        try:
            u = _unit(tuple(getattr(ros, a)))
            if u:
                return u
        except Exception:
            pass
    # (b) cross product of the two in-plane directions
    for a1, a2 in [("dir1", "dir2"), ("dir_1", "dir_2"),
                   ("direction_1", "direction_2"), ("x_direction", "y_direction")]:
        try:
            d1 = tuple(getattr(ros, a1))
            d2 = tuple(getattr(ros, a2))
            u = _unit(_cross(d1, d2))
            if u:
                return u
        except Exception:
            pass
    return None


def target_sets():
    return [n for n in model.element_sets.keys() if n not in SKIP_SETS]


# ---------------- look up the stackup made in script 1 ----------------
full = get_item(md.stackups, STACKUP_NAME)
if full is None:
    raise KeyError("Stackup '%s' not found -- run script 1 first. Available: [%s]"
                   % (STACKUP_NAME, ", ".join("'%s'" % s for s in md.stackups.keys())))


# ---------------- chassis center (for radial orientation) ----------------
if ORIENT_CENTER is not None:
    GLOBAL_CENTER = tuple(ORIENT_CENTER)
else:
    try:
        GLOBAL_CENTER = _avg(model.mesh_query(name="coordinates",
                                              position="centroid", selection="all"))
    except Exception:
        GLOBAL_CENTER = None
if GLOBAL_CENTER is None:
    GLOBAL_CENTER = (0.0, 0.0, 0.0)
print("Chassis center: (%.2f, %.2f, %.2f)" % GLOBAL_CENTER)


def orient_direction(es, ros, center):
    """Pick the OSS orientation direction per ORIENT_MODE -> (vec, source)."""
    if ORIENT_MODE in ("radial_out", "radial_in"):
        rv = _unit((center[0] - GLOBAL_CENTER[0],
                    center[1] - GLOBAL_CENTER[1],
                    center[2] - GLOBAL_CENTER[2]))
        if rv:
            if ORIENT_MODE == "radial_in":
                rv = (-rv[0], -rv[1], -rv[2])
            return rv, ORIENT_MODE
    elif ORIENT_MODE == "rosette":
        v = rosette_normal(ros)
        if v:
            return v, "rosette"
    elif ORIENT_MODE == "mesh":
        v = set_normal(es)
        if v:
            return v, "mesh"
    return DEFAULT_ORIENT_DIR, "fixed"


# ---- one-time: show the first rosette's attributes (to verify [rosette] reads) ----
for _n in model.rosettes.keys():
    if _n not in SKIP_SETS and _n.lower() != "global coordinate system":
        print("Rosette '%s' attrs: %s"
              % (_n, ", ".join(a for a in dir(model.rosettes[_n]) if not a.startswith("_"))))
        break

# =====================================================================
# 4. ORIENTED SELECTION SETS
# =====================================================================
for name in target_sets():
    es  = model.element_sets[name]
    ros = get_item(model.rosettes, name)
    origin = set_center(es) or (0.0, 0.0, 0.0)
    orient_dir, src = orient_direction(es, ros, origin)
    if ORIENT_FLIP:
        orient_dir = (-orient_dir[0], -orient_dir[1], -orient_dir[2])

    kwargs = dict(name=name, orientation_point=origin,
                  orientation_direction=orient_dir, element_sets=[es])
    if ros is not None:
        kwargs["rosettes"] = [ros]
    try:
        model.create_oriented_selection_set(**kwargs)
    except Exception:
        oss = model.create_oriented_selection_set(name=name)
        try: oss.orientation_point = origin
        except Exception: pass
        try: oss.orientation_direction = orient_dir
        except Exception: pass
        try: oss.add_element_set(es)
        except Exception as ex: print("  add_element_set failed '%s': %s" % (name, ex))
        if ros is not None:
            try: oss.add_rosette(ros)
            except Exception as ex: print("  add_rosette failed '%s': %s" % (name, ex))
    tag = "" if ros is not None else "  (NO rosette)"
    print("OSS '%s'  orient_dir=(%.2f, %.2f, %.2f) [%s]%s"
          % (name, orient_dir[0], orient_dir[1], orient_dir[2], src, tag))

# =====================================================================
# 5. MODELING GROUPS + PLIES
# =====================================================================
for name in target_sets():
    oss = get_item(model.oriented_selection_sets, name)
    if oss is None:
        print("  SKIP modeling group '%s' (no OSS found)" % name)
        continue
    mg = model.create_modeling_group(name=name)
    mg.create_modeling_ply(name="%s Ply" % name,
                           ply_material=full,
                           ply_angle=PLY_ANGLE,
                           oriented_selection_sets=(oss,))
    print("Modeling group + ply: '%s'" % name)

# =====================================================================
# 6. SOLID MODELS
# =====================================================================
for name in target_sets():
    es = model.element_sets[name]
    ex = "monolithic" if name in MONOLITHIC_SETS else EX_TYPE
    try:
        model.create_solid_model(name=name, element_sets=[es], ex_type=ex)
    except Exception:
        sm = model.create_solid_model(name=name)
        try: sm.ex_type = ex
        except Exception as e1: print("  set ex_type failed '%s': %s" % (name, e1))
        try: sm.add_element_set(es)
        except Exception as e2: print("  add_element_set failed '%s': %s" % (name, e2))
    print("Solid model '%s'  (ex_type = %s)" % (name, ex))

model.update()
print("Done -- SCRIPT 2 complete (OSS, plies, solid models).")
