# =====================================================================
#  ACP (Pre) -- one rosette per element set, at the set's own centroid
# =====================================================================
#  Runs INSIDE ACP (File > Run Script, or from Workbench via RunScript).
#  Run AFTER the mesh + element sets exist.
#
#  For every element set it creates a rosette of the same name, placed
#  at the average of THAT set's element centroids (scoped via a temporary
#  selection). Axis directions stay at defaults (X/Y) for manual entry.
# =====================================================================

# Element sets to skip (e.g. the whole-model set).
SKIP_SETS = ["All_Elements"]

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model


def _avg(arr):
    """Average a sequence of (x,y,z) coords -> (x,y,z)."""
    flat = list(arr)
    if not flat:
        return None
    if hasattr(flat[0], "__len__"):                 # [(x,y,z), ...]
        n = len(flat)
        return (sum(p[0] for p in flat) / n,
                sum(p[1] for p in flat) / n,
                sum(p[2] for p in flat) / n)
    xs, ys, zs = flat[0::3], flat[1::3], flat[2::3]  # flat [x,y,z,x,y,z,...]
    n = len(xs)
    return (sum(xs) / n, sum(ys) / n, sum(zs) / n)


def set_center(es):
    """Centroid of one element set: select its elements, then average
    their centroid coordinates. Returns None if it can't be read."""
    try:
        # scope a temporary selection to just this element set...
        model.select_elements(selection="sel0", op="new", attached_to=[es])
        # ...and read the element-centroid coordinates of that selection
        coords = model.mesh_query(name="coordinates", position="centroid",
                                  selection="sel0")
        return _avg(coords)
    except Exception as ex:
        print("  (centroid unavailable: %s)" % ex)
        return None


# ---- create one rosette per element set ----
made = 0
for name in list(model.element_sets.keys()):
    if name in SKIP_SETS:
        continue
    es = model.element_sets[name]
    origin = set_center(es)
    if origin is None:
        origin = (0.0, 0.0, 0.0)
        note = "  (placed at origin)"
    else:
        note = ""
    model.create_rosette(name, origin=origin,
                         dir1=(1.0, 0.0, 0.0), dir2=(0.0, 1.0, 0.0),
                         rosette_type="PARALLEL")
    made += 1
    print("Rosette '%s' at (%.3f, %.3f, %.3f)%s"
          % (name, origin[0], origin[1], origin[2], note))

model.update()
print("Done -- %d rosettes created." % made)
