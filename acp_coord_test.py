# =====================================================================
#  ACP TEST -- find the right mesh_query call for element coordinates
# =====================================================================
#  Run in ACP via  File > Run Script.  It writes the result to a text
#  file in your home folder:  acp_coord_test.txt  (path printed below).
#  Open that file and send me its contents.
# =====================================================================
import os

try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

# pick a real element set: prefer "Floor", else the first one
keys = list(model.element_sets.keys())
name = "Floor" if "Floor" in keys else keys[0]
es = model.element_sets[name]

lines = ["Element set tested: '%s'" % name,
         "Total element sets: %d" % len(keys),
         "Names: %s" % ", ".join(keys),
         ""]

for qname in ["coordinates", "centroids", "coordinate", "coord"]:
    try:
        data = model.mesh_query(name=qname, position="centroid",
                                selection="all", entities=[es])
        arr = data[0] if (len(data) and hasattr(data[0], "__len__")) else data
        flat = list(arr)
        first = flat[0] if flat else None
        lines.append("name='%s'  -> OK   count=%d   first=%s"
                     % (qname, len(flat), repr(first)))
    except Exception as ex:
        lines.append("name='%s'  -> ERROR: %s" % (qname, ex))

out_path = os.path.join(os.path.expanduser("~"), "acp_coord_test.txt")
f = open(out_path, "w")
f.write("\n".join(lines))
f.close()

# also surface the path (and raise so it's visible if there is a log/dialog)
print("Wrote: %s" % out_path)
raise Exception("COORD TEST DONE -> open this file: %s" % out_path)
