# =====================================================================
#  ACP (Pre) -- one Oriented Selection Set per element set
# =====================================================================
#  Runs INSIDE ACP (File > Run Script). Run AFTER the rosettes exist
#  (acp_rosettes.py), since each OSS references the same-named rosette.
#
#  For every element set it creates an OSS that is:
#    - scoped to that element set,
#    - given its complementary rosette (same name) as reference direction,
#    - placed at the set centroid with a default lay-up direction (0,0,1).
#  You then adjust orientation direction / draping / flipping manually.
# =====================================================================

SKIP_SETS = ["All_Elements"]
DEFAULT_ORIENT_DIR = (0.0, 0.0, 1.0)   # lay-up growth direction; adjust per set later

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model


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


def get_rosette(name):
    try:
        return model.rosettes[name]
    except Exception:
        return None


# ---- create one OSS per element set ----
made = 0
for name in list(model.element_sets.keys()):
    if name in SKIP_SETS:
        continue
    es = model.element_sets[name]
    origin = set_center(es) or (0.0, 0.0, 0.0)
    ros = get_rosette(name)

    kwargs = dict(name=name,
                  orientation_point=origin,
                  orientation_direction=DEFAULT_ORIENT_DIR,
                  element_sets=[es])
    if ros is not None:
        kwargs["rosettes"] = [ros]

    try:
        model.create_oriented_selection_set(**kwargs)
    except Exception:
        # fallback: create bare, then attach via methods
        oss = model.create_oriented_selection_set(name=name)
        try:
            oss.orientation_point = origin
        except Exception:
            pass
        try:
            oss.orientation_direction = DEFAULT_ORIENT_DIR
        except Exception:
            pass
        try:
            oss.add_element_set(es)
        except Exception as ex:
            print("  add_element_set failed for '%s': %s" % (name, ex))
        if ros is not None:
            try:
                oss.add_rosette(ros)
            except Exception as ex:
                print("  add_rosette failed for '%s': %s" % (name, ex))

    made += 1
    tag = "" if ros is not None else "  (NO rosette found - reference direction unset)"
    print("OSS '%s' -> element set '%s'%s" % (name, name, tag))

model.update()
print("Done -- %d oriented selection sets created." % made)
