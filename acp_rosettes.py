# =====================================================================
#  ACP (Pre) -- one rosette per element set, at the set's centroid
# =====================================================================
#  Runs INSIDE ACP (File > Run Script, or from Workbench via RunScript).
#  Run AFTER the mesh + element sets exist.
#
#  For every element set it creates a rosette of the same name, placed
#  at the average of that set's element centroids. Axis directions are
#  left at defaults (X/Y) for you to set manually later.
# =====================================================================

# Element sets to skip (e.g. the whole-model set).
SKIP_SETS = ["All_Elements"]

# mesh_query names to try for element-centroid coordinates (first that works wins).
COORD_NAMES = ["coordinates", "centroids", "coordinate"]

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model


def _avg(arr):
    """Average a sequence of coords -> (x,y,z). Handles list-of-(x,y,z)
    or a flat [x,y,z,x,y,z,...] layout."""
    flat = list(arr)
    if not flat:
        return None
    if hasattr(flat[0], "__len__"):                 # [(x,y,z), ...]
        n = len(flat)
        return (sum(p[0] for p in flat) / n,
                sum(p[1] for p in flat) / n,
                sum(p[2] for p in flat) / n)
    xs, ys, zs = flat[0::3], flat[1::3], flat[2::3]  # [x,y,z,x,y,z,...]
    n = len(xs)
    return (sum(xs) / n, sum(ys) / n, sum(zs) / n)


def set_center(es):
    """Centroid of an element set, or None if coords can't be read."""
    for qname in COORD_NAMES:
        try:
            data = model.mesh_query(name=qname, position="centroid",
                                    selection="all", entities=[es])
            # mesh_query with entities= returns one array per entity
            arr = data[0] if (len(data) and hasattr(data[0], "__len__")) else data
            c = _avg(arr)
            if c is not None:
                return c
        except Exception as ex:
            last = ex
    print("  (centroid unavailable: %s)" % last)
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
