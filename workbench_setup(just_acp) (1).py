# =====================================================================
#  WORKBENCH SETUP -- JUST ACP
# =====================================================================
#  Run from the Workbench Project window (empty project is fine):
#     File > Scripting > Run Script File...  -> pick THIS file
#
#  Builds an ACP-only project ready for composite layup:
#    1. Creates an ACP (Pre) system titled "Panels"
#    2. Imports material data (files named *Al_HC* / *CF_Limits*) into
#       its Engineering Data
#    3. Prompts for the chassis STEP file and attaches it to Geometry
#    4. Refreshes the model so it's ready to mesh + lay up
#
#  (No bumpers, no Static Structural, no Structural Optimization.)
# =====================================================================

import os

# ---------------- CONFIG ----------------
MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]     # material files to import (name contains)
MATERIAL_EXTS = (".xml", ".engd", ".eng")
SEARCH_ROOTS = [os.path.expanduser("~")]        # where to look for material files
CHASSIS_LABEL = "Chassis panels"                # shown in the file picker
CHASSIS_FALLBACK = ""                           # optional hard path if the dialog misbehaves

SKIP_DIRS = set([
    "appdata", "$recycle.bin", "windows", "program files", "program files (x86)",
    "programdata", "node_modules", ".git", "$windows.~ws", "system volume information",
    "application data", "local settings", "my documents", "cookies",
    "nethood", "printhood", "recent", "sendto", "start menu", "templates",
])


# ---------------- HELPERS ----------------
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
    hits, seen, kl = [], set(), key.lower()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fn in filenames:
                low = fn.lower()
                if kl in low and low.endswith(MATERIAL_EXTS):
                    full = os.path.join(dirpath, fn).replace("\\", "/")
                    if full not in seen:
                        seen.add(full)
                        hits.append(full)
    try:
        hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except Exception:
        pass
    return hits


def pick_step_file(label):
    try:
        import clr
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import OpenFileDialog, DialogResult
        from System.Threading import Thread, ThreadStart, ApartmentState
        holder = {"path": None}

        def _show():
            dlg = OpenFileDialog()
            dlg.Title = "Select STEP file for: %s" % label
            dlg.Filter = "STEP files (*.step;*.stp)|*.step;*.stp|All files (*.*)|*.*"
            dlg.Multiselect = False
            dlg.RestoreDirectory = True
            if dlg.ShowDialog() == DialogResult.OK:
                holder["path"] = dlg.FileName

        t = Thread(ThreadStart(_show))       # WinForms dialog needs an STA thread
        t.SetApartmentState(ApartmentState.STA)
        t.Start()
        t.Join()
        return holder["path"]
    except Exception as ex:
        print("  (file dialog unavailable: %s)" % ex)
        return None


# =====================================================================
# 1. Create the ACP (Pre) system
# =====================================================================
sysA = get_template("ACP (Pre)").CreateSystem()
sysA.DisplayText = "Panels"
print("Created ACP (Pre) system: 'Panels'")

# =====================================================================
# 2. Import material data into Engineering Data
# =====================================================================
try:
    eng = sysA.GetContainer(ComponentName="Engineering Data")
    print("Searching for material files under: %s" % ", ".join(SEARCH_ROOTS))
    for key in MATERIAL_NAME_KEYS:
        files = find_material_files(SEARCH_ROOTS, key)
        if not files:
            print("  WARNING: no file matching '%s' found." % key)
            continue
        eng.Import(Source=files[0])
        print("  Imported ('%s'): %s" % (key, files[0]))
        for extra in files[1:]:
            print("     (also found, NOT imported): %s" % extra)
except Exception as ex:
    print("Material import skipped due to error: %s" % ex)

# =====================================================================
# 3. Import the chassis geometry (file picker)
# =====================================================================
try:
    path = pick_step_file(CHASSIS_LABEL) or CHASSIS_FALLBACK
    if path:
        geom = sysA.GetContainer(ComponentName="Geometry")
        geom.SetFile(FilePath=path.replace("\\", "/"))
        print("Chassis geometry set: %s" % path)
    else:
        print("No chassis file chosen - geometry left empty.")
except Exception as ex:
    print("Geometry import error: %s" % ex)

# =====================================================================
# 4. Refresh so the model is ready for meshing + layup
# =====================================================================
try:
    comp = sysA.GetComponent(Name="Model")
    comp.Refresh()
    print("Model refreshed.")
except Exception as ex:
    print("Refresh note: %s" % ex)

try:
    Save(Overwrite=True)
    print("Project saved.")
except Exception as ex:
    print("Not saved (save manually): %s" % ex)

print("Done -- ACP project ready for composite layup.")
