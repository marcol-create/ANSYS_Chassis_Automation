# =====================================================================
#  ACP (Pre) -- FULL SETUP  (fabrics, stackup, rosettes, OSS, plies)
# =====================================================================
#  Run INSIDE ACP:  File > Run Script  (or from Workbench via RunScript).
#  Run AFTER the mesh + element sets + materials exist.
#
#  1. Fabrics  : HC (honeycomb, 12.192), CF (carbon fiber, 0.127)
#  2. Stackup  : "Full Panel" = CF/0, CF/90, HC/0, CF/0, CF/90
#  3. Rosettes : one per element set, at the set centroid
#  4. OSS      : one per element set, scoped to the set, reference
#                direction = same-named rosette
#  5. Modeling : one modeling group per element set, each with one ply
#                (OSS = same-named set, ply material = "Full Panel")
# =====================================================================

# ---------------- CONFIG ----------------
HC_KEYS = ["honeycomb", "al_hc", "hc", "alum"]     # honeycomb material match
CF_KEYS = ["carbon", "cf", "fiber", "fibre"]       # carbon-fiber material match
HC_THICKNESS = 12.192
CF_THICKNESS = 0.127
STACKUP_NAME = "Full Panel"

SKIP_SETS = ["All_Elements"]                       # sets to ignore everywhere
DEFAULT_ORIENT_DIR = (0.0, 0.0, 1.0)               # OSS lay-up direction (adjust later)
PLY_ANGLE = 0.0

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


def set_center(es):
    try:
        model.select_elements(selection="sel0", op="new", attached_to=[es])
        coords = model.mesh_query(name="coordinates", position="centroid",
                                  selection="sel0")
        return _avg(coords)
    except Exception:
        return None


def get_item(collection, name):
    try:
        return collection[name]
    except Exception:
        return None


def target_sets():
    return [n for n in model.element_sets.keys() if n not in SKIP_SETS]


# =====================================================================
# 1. FABRICS
# =====================================================================
hc = md.create_fabric(name="HC",
                      material=find_material(HC_KEYS, "Honeycomb"),
                      thickness=HC_THICKNESS)
cf = md.create_fabric(name="CF",
                      material=find_material(CF_KEYS, "Carbon fiber"),
                      thickness=CF_THICKNESS)
print("Fabrics created: HC (%g), CF (%g)" % (hc.thickness, cf.thickness))

# =====================================================================
# 2. STACKUP  "Full Panel"  =  CF/0, CF/90, HC/0, CF/0, CF/90
# =====================================================================
full = md.create_stackup(name=STACKUP_NAME)
for fab, ang in [(cf, 0.0), (cf, 90.0), (hc, 0.0), (cf, 0.0), (cf, 90.0)]:
    full.add_fabric(fab, ang)
print("Stackup '%s' created (%d fabrics)." % (STACKUP_NAME, len(full.fabrics)))

# =====================================================================
# 3. ROSETTES  (one per element set, at the set centroid)
# =====================================================================
for name in target_sets():
    es = model.element_sets[name]
    origin = set_center(es) or (0.0, 0.0, 0.0)
    model.create_rosette(name, origin=origin,
                         dir1=(1.0, 0.0, 0.0), dir2=(0.0, 1.0, 0.0),
                         rosette_type="PARALLEL")
    print("Rosette '%s' at (%.3f, %.3f, %.3f)" % (name, origin[0], origin[1], origin[2]))

# =====================================================================
# 4. ORIENTED SELECTION SETS (one per set, referencing same-named rosette)
# =====================================================================
for name in target_sets():
    es  = model.element_sets[name]
    ros = get_item(model.rosettes, name)
    origin = set_center(es) or (0.0, 0.0, 0.0)

    kwargs = dict(name=name, orientation_point=origin,
                  orientation_direction=DEFAULT_ORIENT_DIR, element_sets=[es])
    if ros is not None:
        kwargs["rosettes"] = [ros]
    try:
        model.create_oriented_selection_set(**kwargs)
    except Exception:
        oss = model.create_oriented_selection_set(name=name)
        try: oss.orientation_point = origin
        except Exception: pass
        try: oss.orientation_direction = DEFAULT_ORIENT_DIR
        except Exception: pass
        try: oss.add_element_set(es)
        except Exception as ex: print("  add_element_set failed '%s': %s" % (name, ex))
        if ros is not None:
            try: oss.add_rosette(ros)
            except Exception as ex: print("  add_rosette failed '%s': %s" % (name, ex))
    tag = "" if ros is not None else "  (NO rosette)"
    print("OSS '%s'%s" % (name, tag))

# =====================================================================
# 5. MODELING GROUPS + PLIES  (one group/ply per set, material = Full Panel)
# =====================================================================
for name in target_sets():
    oss = get_item(model.oriented_selection_sets, name)
    if oss is None:
        print("  SKIP modeling group '%s' (no OSS found)" % name)
        continue
    mg = model.create_modeling_group(name=name)
    mg.create_modeling_ply(name="%s Ply" % name,
                           ply_material=full,          # the "Full Panel" stackup
                           ply_angle=PLY_ANGLE,
                           oriented_selection_sets=(oss,))
    print("Modeling group + ply: '%s'" % name)

model.update()
print("Done -- full ACP setup complete.")
