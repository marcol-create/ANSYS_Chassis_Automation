# =====================================================================
#  WORKBENCH SETUP -- JUST ACP
# =====================================================================
#  Run from the Workbench Project window (empty project is fine):
#     File > Scripting > Run Script File...  -> pick THIS file
#
#  Builds an ACP-only project ready for composite layup:
#    1. Creates an ACP (Pre) system titled "Panels"
#    2. Imports material data (files named *Al_HC* / *CF_Limits*)
#    3. Prompts for the chassis STEP file and attaches it to Geometry
#    4. Opens Mechanical and, on the chassis:
#         - sets 1 mm thickness on every (surface) body
#         - creates one Named Selection per body (all faces, prefix stripped)
#    5. Saves
#
#  (No bumpers, no Static Structural, no Structural Optimization.)
# =====================================================================

import os

# ---------------- CONFIG ----------------
MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]
MATERIAL_EXTS = (".xml", ".engd", ".eng")
SEARCH_ROOTS = [os.path.expanduser("~")]
CHASSIS_LABEL = "Chassis panels"
CHASSIS_FALLBACK = ""                            # optional hard path if the dialog misbehaves

# How to open Mechanical: "" (visible, most reliable) / "Interactive" / "Hidden"
EDIT_MODE = "Interactive"

SKIP_DIRS = set([
    "appdata", "$recycle.bin", "windows", "program files", "program files (x86)",
    "programdata", "node_modules", ".git", "$windows.~ws", "system volume information",
    "application data", "local settings", "my documents", "cookies",
    "nethood", "printhood", "recent", "sendto", "start menu", "templates",
])

# ---------------- Mechanical-side script (thickness + named selections) ----------------
CHASSIS_CMD = '''
THICKNESS = Quantity("1 [mm]")
NAME_DELIMITER = "|"

def clean_name(raw):
    if NAME_DELIMITER and NAME_DELIMITER in raw:
        return raw.rsplit(NAME_DELIMITER, 1)[-1].strip()
    return raw.strip()

model  = ExtAPI.DataModel.Project.Model
bodies = model.GetChildren(DataModelObjectCategory.Body, True)
with Transaction():
    for body in bodies:
        try:
            body.Thickness = THICKNESS
        except Exception:
            pass
with Transaction():
    for body in bodies:
        face_ids = [face.Id for face in body.GetGeoBody().Faces]
        if not face_ids:
            continue
        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        sel.Ids = face_ids
        ns = model.AddNamedSelection()
        ns.Location = sel
        ns.Name = clean_name(body.Name)
'''


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

        t = Thread(ThreadStart(_show))
        t.SetApartmentState(ApartmentState.STA)
        t.Start()
        t.Join()
        return holder["path"]
    except Exception as ex:
        print("  (file dialog unavailable: %s)" % ex)
        return None


def open_model(model):
    if EDIT_MODE == "Interactive":
        model.Edit(Interactive=False)
    elif EDIT_MODE == "Hidden":
        model.Edit(Hidden=True)
    else:
        model.Edit()


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
have_geometry = False
try:
    path = pick_step_file(CHASSIS_LABEL) or CHASSIS_FALLBACK
    if path:
        geom = sysA.GetContainer(ComponentName="Geometry")
        geom.SetFile(FilePath=path.replace("\\", "/"))
        have_geometry = True
        print("Chassis geometry set: %s" % path)
    else:
        print("No chassis file chosen - geometry left empty; skipping Mechanical setup.")
except Exception as ex:
    print("Geometry import error: %s" % ex)

# =====================================================================
# 4. Mechanical setup on the chassis: thickness + named selections
# =====================================================================
if have_geometry:
    try:
        comp = sysA.GetComponent(Name="Model")
        comp.Refresh()
        model = sysA.GetContainer(ComponentName="Model")
        open_model(model)
        model.SendCommand(Language="Python", Command=CHASSIS_CMD)
        model.Exit()
        print("Mechanical setup done: thickness + named selections.")
    except Exception as ex:
        print("Mechanical setup error: %s" % ex)

# =====================================================================
# 5. Save
# =====================================================================
try:
    Save(Overwrite=True)
    print("Project saved.")
except Exception as ex:
    print("Not saved (save manually): %s" % ex)

print("Done -- ACP project ready for composite layup.")
