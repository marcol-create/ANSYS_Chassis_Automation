# =====================================================================
#  WORKBENCH: import geometry (via file picker) + set up Mechanical
# =====================================================================
#  Run from the Workbench Project window, AFTER workbench_schematic.py:
#     File > Scripting > Run Script File...  -> pick THIS file
#
#  For each block it pops up a file picker so you choose THIS iteration's
#  STEP file, attaches it, opens Mechanical, runs the right setup, closes.
#
#    Chassis panels (ACP Pre): pick STEP -> 1 mm thickness on every body
#                              + one Named Selection per body (all faces,
#                              "Block Name|" prefix stripped)
#    Each bumper (Mechanical): pick STEP -> 1 mm thickness + 3 mm mesh + generate
#
#  Cancel a picker to leave that block's existing geometry untouched.
# =====================================================================

# (title-search term, kind, friendly label for the picker)
TASKS = [
    ("panels",       "chassis", "Chassis panels"),
    ("side bumper",  "bumper",  "Side bumper"),
    ("front bumper", "bumper",  "Front bumper"),
]

# Optional hard-coded fallbacks if the file dialog misbehaves in your
# install. Leave "" to just skip. e.g. "Chassis panels": "C:/geo/chassis.step"
FALLBACK_PATHS = {
    "Chassis panels": "",
    "Side bumper":    "",
    "Front bumper":   "",
}

# How to open Mechanical: "" (visible, most reliable) / "Interactive" / "Hidden"
EDIT_MODE = "Interactive"


# --- Mechanical-side scripts (run INSIDE Mechanical) ----------------
CHASSIS_CMD = '''
THICKNESS = Quantity("1 [mm]")
NAME_DELIMITER = "|"     # "Block Name| Top" -> "Top"; set "" to keep full name

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

BUMPER_CMD = '''
THICKNESS    = Quantity("1 [mm]")
ELEMENT_SIZE = Quantity("3 [mm]")
model  = ExtAPI.DataModel.Project.Model
bodies = model.GetChildren(DataModelObjectCategory.Body, True)
with Transaction():
    for body in bodies:
        try:
            body.Thickness = THICKNESS
        except Exception:
            pass
mesh = model.Mesh
mesh.ElementSize = ELEMENT_SIZE
mesh.UseAdaptiveSizing = False
mesh.GenerateMesh()
'''

CMD_BY_KIND = {"chassis": CHASSIS_CMD, "bumper": BUMPER_CMD}


# --- file picker (via .NET WinForms) --------------------------------
def pick_step_file(label):
    try:
        import clr
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import OpenFileDialog, DialogResult
        dlg = OpenFileDialog()
        dlg.Title = "Select STEP file for: %s" % label
        dlg.Filter = "STEP files (*.step;*.stp)|*.step;*.stp|All files (*.*)|*.*"
        dlg.Multiselect = False
        if dlg.ShowDialog() == DialogResult.OK:
            return dlg.FileName
        return None
    except Exception, ex:
        print("  (file dialog unavailable: %s)" % ex)
        return None


def choose_geometry(label):
    """Dialog first; fall back to a configured path; else None (skip)."""
    path = pick_step_file(label)
    if not path:
        path = FALLBACK_PATHS.get(label, "")
    return path if path else None


# --- helpers --------------------------------------------------------
def system_by_title(term):
    want = term.strip().lower()
    for s in GetAllSystems():
        try:
            if want in s.DisplayText.strip().lower():
                return s
        except Exception:
            pass
    return None


def open_model(model):
    if EDIT_MODE == "Interactive":
        model.Edit(Interactive=False)
    elif EDIT_MODE == "Hidden":
        model.Edit(Hidden=True)
    else:
        model.Edit()


# --- run ------------------------------------------------------------
for term, kind, label in TASKS:
    sysx = system_by_title(term)
    if sysx is None:
        print("SKIP - no block matching '%s'" % term)
        continue
    try:
        # 1) attach geometry chosen by the user (or skip if cancelled)
        path = choose_geometry(label)
        if path:
            geom = sysx.GetContainer(ComponentName="Geometry")
            geom.SetFile(FilePath=path.replace("\\", "/"))
            print("Geometry set for '%s': %s" % (sysx.DisplayText, path))
        else:
            print("No file chosen for '%s' - using existing geometry." % sysx.DisplayText)

        # 2) open Mechanical and run the setup
        comp = sysx.GetComponent(Name="Model")
        comp.Refresh()
        model = sysx.GetContainer(ComponentName="Model")
        open_model(model)
        model.SendCommand(Language="Python", Command=CMD_BY_KIND[kind])
        model.Exit()
        print("Done (%s): %s" % (kind, sysx.DisplayText))
    except Exception, ex:
        print("ERROR on '%s': %s" % (term, ex))

try:
    Save(Overwrite=True)
    print("Project saved.")
except Exception, ex:
    print("Not saved (save manually): %s" % ex)

print("All done.")
