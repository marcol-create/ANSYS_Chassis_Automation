# =====================================================================
#  ACP TEST 2 -- find how to scope coordinates to ONE element set
# =====================================================================
#  Run in ACP via File > Run Script. Writes + opens acp_coord_test2.txt.
#  Send me the contents.
# =====================================================================
import os

try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

keys = list(model.element_sets.keys())
# pick a specific set that is NOT the whole-model set
name = None
for k in keys:
    if k.lower() != "all_elements":
        name = k
        break
es = model.element_sets[name]

L = ["Testing set: '%s'  (of %d sets)" % (name, len(keys)), ""]


def centroid_of(arr):
    flat = list(arr)
    if not flat:
        return None, 0
    if hasattr(flat[0], "__len__"):
        n = len(flat)
        return (sum(p[0] for p in flat) / n,
                sum(p[1] for p in flat) / n,
                sum(p[2] for p in flat) / n), n
    xs, ys, zs = flat[0::3], flat[1::3], flat[2::3]
    n = len(xs)
    return (sum(xs) / n, sum(ys) / n, sum(zs) / n), n


# whole-mesh count for comparison
try:
    d = model.mesh_query(name="coordinates", position="centroid", selection="all")
    _, n = centroid_of(d)
    L.append("WHOLE MESH count = %d   (approaches that match this did NOT scope)" % n)
except Exception as ex:
    L.append("whole mesh ERROR: %s" % ex)
L.append("")

# A) entities= with selection='all'  (current, suspected broken)
try:
    d = model.mesh_query(name="coordinates", position="centroid", selection="all", entities=[es])
    arr = d[0] if (len(d) and hasattr(d[0], "__len__")) else d
    c, n = centroid_of(arr)
    L.append("A) entities+all:        count=%d  centroid=%s" % (n, c))
except Exception as ex:
    L.append("A) entities+all:        ERROR %s" % ex)

# B) select_elements(attached_to=[es]) then query sel0
try:
    model.select_elements(selection="sel0", op="new", attached_to=[es])
    d = model.mesh_query(name="coordinates", position="centroid", selection="sel0")
    c, n = centroid_of(d)
    L.append("B) select attached_to:  count=%d  centroid=%s" % (n, c))
except Exception as ex:
    L.append("B) select attached_to:  ERROR %s" % ex)

# C) select_elements(element_sets=[es]) then query sel0
try:
    model.select_elements(selection="sel1", op="new", element_sets=[es])
    d = model.mesh_query(name="coordinates", position="centroid", selection="sel1")
    c, n = centroid_of(d)
    L.append("C) select element_sets: count=%d  centroid=%s" % (n, c))
except Exception as ex:
    L.append("C) select element_sets: ERROR %s" % ex)

# D) what does the element set object expose?
L.append("")
L.append("es attributes: %s" % ", ".join([a for a in dir(es) if not a.startswith("_")]))

out = os.path.join(os.path.expanduser("~"), "acp_coord_test2.txt")
open(out, "w").write("\n".join(str(x) for x in L))
try:
    os.startfile(out)
except Exception:
    pass
print("wrote %s" % out)
