# =====================================================================
#  MECHANICAL setup  --  IN-GUI SCRIPT (ACT / IronPython)
# =====================================================================
#  Run from inside Ansys Mechanical:
#     Ribbon > Automation > Scripting  ->  paste in the editor, click Run
#     (or paste into the Shell/console).
#  Operates on the model that is CURRENTLY OPEN.
#
#  Does two things:
#    1. Sets the thickness of every body to 1 mm (surface/shell bodies).
#    2. Creates one Named Selection per body, named the same as the body.
# =====================================================================

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
THICKNESS = Quantity("1 [mm]")   # change value/unit here if needed

# ---------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------
model = ExtAPI.DataModel.Project.Model

# All bodies in the model, including those inside multi-body parts.
bodies = model.GetChildren(DataModelObjectCategory.Body, True)
print("Found %d bodies." % len(bodies))

# ---------------------------------------------------------------------
# 1. THICKNESS = 1 mm on every (surface) body
# ---------------------------------------------------------------------
n_thick = 0
with Transaction():                      # batch tree edits -> much faster
    for body in bodies:
        try:
            body.Thickness = THICKNESS   # only valid for surface bodies
            n_thick += 1
        except Exception:
            # Solid bodies have no Thickness property -> skip them.
            print("  Skipped thickness (not a surface body): %s" % body.Name)
print("Set thickness on %d bodies." % n_thick)

# ---------------------------------------------------------------------
# 2. ONE NAMED SELECTION PER BODY  (same name as the body)
# ---------------------------------------------------------------------
n_ns = 0
with Transaction():
    for body in bodies:
        sel = ExtAPI.SelectionManager.CreateSelectionInfo(
            SelectionTypeEnum.GeometryEntities)
        sel.Ids = [body.GetGeoBody().Id]   # geometry id of this body

        ns = model.AddNamedSelection()
        ns.Location = sel
        ns.Name = body.Name
        n_ns += 1
        print("  Named selection: %s" % body.Name)

print("Created %d named selections. Done." % n_ns)
