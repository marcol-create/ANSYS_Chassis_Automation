# =====================================================================
#  WORKBENCH PROJECT SCHEMATIC BUILDER  v2   (IronPython)
# =====================================================================
#  Run from the Workbench Project window:
#     File > Scripting > Run Script File...  -> pick THIS file
#  (Delete older "workbench schematic" copies so you don't run a stale one.)
#
#  Builds five systems, positioned and titled, then searches your
#  computer for material files named *Al_HC* / *CF_Limits* and imports
#  them into block A's Engineering Data.
#
#  Watch the console for lines like "A created", "Imported (...)".
#  If you DON'T see those, you ran an old file.
# =====================================================================

import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
SEARCH_ROOTS = [os.path.expanduser("~")]        # your whole user profile
# Whole drive instead (slow):   SEARCH_ROOTS = ["C:\\"]
# Several places:               SEARCH_ROOTS = [os.path.expanduser("~"), "D:\\"]

MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]     # match anywhere in the name
MATERIAL_EXTS = (".xml", ".engd", ".eng")

SKIP_DIRS = set([
    "appdata", "$recycle.bin", "windows", "program files",
    "program files (x86)", "programdata", "node_modules", ".git",
    "$windows.~ws", "system volume information",
    # legacy Windows junctions inside the user profile (access-denied):
    "application data", "local settings", "my documents", "cookies",
    "nethood", "printhood", "recent", "sendto", "start menu", "templates",
])


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def get_template(name, solver=None):
    try:
        if solver:
            return GetTemplate(TemplateName=name, Solver=solver)
        return GetTemplate(TemplateName=name)
    except Exception:
        if solver:
            return GetTemplate(TemplateName="%s (%s)" % (name, solver))
        raise


def find_material_files(roots, key):
    hits, seen, key_low = [], set(), key.lower()
    for root in roots:
        if not os.path.isdir(root):
            print("WARNING: search root does not exist: %s" % root)
            continue
        # onerror swallows access-denied dirs so the walk never throws
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fname in filenames:
                low = fname.lower()
                if key_low in low and low.endswith(MATERIAL_EXTS):
                    full = os.path.join(dirpath, fname).replace("\\", "/")
                    if full not in seen:
                        seen.add(full)
                        hits.append(full)
    try:
        hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except Exception:
        pass
    return hits


# ---------------------------------------------------------------------
# Block A : ACP (Pre)  + material import
# ---------------------------------------------------------------------
sysA = get_template("ACP (Pre)").CreateSystem()
sysA.DisplayText = "Panels"
print("A created: Panels")

# The whole search/import is wrapped so a file-system hiccup can never
# stop the schematic from being built.
try:
    eng = sysA.GetContainer(ComponentName="Engineering Data")
    print("Searching under: %s" % ", ".join(SEARCH_ROOTS))
    for key in MATERIAL_NAME_KEYS:
        files = find_material_files(SEARCH_ROOTS, key)
        if not files:
            print("WARNING: no file matching '%s' found." % key)
            continue
        eng.Import(Source=files[0])
        print("Imported ('%s'): %s" % (key, files[0]))
        for extra in files[1:]:
            print("   (also found, NOT imported): %s" % extra)
except Exception, ex:                       # IronPython 2.x syntax
    print("Material import skipped due to error: %s" % ex)

# ---------------------------------------------------------------------
# Blocks B - E
# ---------------------------------------------------------------------
sysB = get_template("Static Structural", "ANSYS").CreateSystem(
    Position="Right", RelativeTo=sysA)
sysB.DisplayText = "Side Impact"
print("B created: Side Impact")

sysC = get_template("Structural Optimization", "ANSYS").CreateSystem(
    Position="Below", RelativeTo=sysB)
sysC.DisplayText = "Front Impact"
print("C created: Front Impact")

tmpl_mm = get_template("Mechanical Model")
sysD = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysA)
sysD.DisplayText = "Side bumper"
print("D created: Side bumper")

sysE = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysD)
sysE.DisplayText = "Front Bumper"
print("E created: Front Bumper")

print("Done.")
