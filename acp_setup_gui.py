# =====================================================================
#  ACP (Pre) setup  --  LEGACY IN-GUI SCRIPT (compolyx API)
# =====================================================================
#  Run from inside the ACP editor:  File > Run Script...  (or paste
#  into the Shell panel).  It operates on the project that is CURRENTLY
#  OPEN, so the materials / oriented selection sets / element sets you
#  created earlier must already be in the tree.  Nothing is loaded or
#  saved -- the new objects just appear in your open model.
#
#  Builds:
#    1. Fabrics  "HC" (Aluminum Honeycomb, 12.192 mm) and "CF" (CF Fiber 2, 0.127 mm)
#    2. Stackup  "Full Panel" = [CF/0, CF/90, HC/0, CF/0, CF/90]
#    3. One modeling group + ply per part (ply material = "Full Panel" stackup,
#       OSS = the part's oriented selection set)
#    4. One solid model per part (ex_type = analysis_ply_wise, except Roof = monolithic)
# =====================================================================

# ---------------------------------------------------------------------
# CONFIG  --  edit to match your project
# ---------------------------------------------------------------------
MAT_HONEYCOMB = "Aluminum Honeycomb"
MAT_CF        = "CF Fiber 2"

HC_THICKNESS_MM = 12.192
CF_THICKNESS_MM = 0.127

STACKUP_NAME = "Full Panel"

# One entry per part. Each name must match the OSS name AND the element-set
# name already in the model. Add / rename freely.
PARTS = [
    "Floor",
    "Right Shock",
    "Left Shock",
    "Right Sup",
    "Roof",
    # "Left Sup", "Front", "Rear", ...   <-- add the rest here
]

# Parts whose solid model uses Monolithic extrusion (all others = Analysis Ply Wise).
MONOLITHIC_PARTS = {"Roof"}

# ---------------------------------------------------------------------
# GET THE OPEN MODEL
# ---------------------------------------------------------------------
try:
    db                      # already defined in the ACP shell
except NameError:
    import compolyx
    db = compolyx.DB()

model = db.active_model
md    = model.material_data

print("Model       : %s" % model.name)
print("Unit system : %s" % model.unit_system)

# Length conversion: thicknesses above are in mm; convert to the model's
# length unit. If the auto-detect is wrong, just set MM_TO_MODEL by hand.
_us = str(model.unit_system).lower()
_factors = {"si": 1e-3, "mks": 1e-3,      # length = m
            "mpa": 1.0, "umks": 1.0,      # length = mm
            "cgs": 0.1,                    # length = cm
            "bin": 1.0 / 25.4,             # length = in
            "bft": 1.0 / 304.8}            # length = ft
MM_TO_MODEL = next((f for k, f in _factors.items() if k in _us), 1e-3)
print("mm -> model factor: %g" % MM_TO_MODEL)


# ---------------------------------------------------------------------
# HELPERS  --  clear error (with available names) if something is missing
# ---------------------------------------------------------------------
def _require(collection, name, kind):
    try:
        return collection[name]
    except Exception:
        keys = ", ".join("'%s'" % k for k in collection.keys())
        raise KeyError("%s '%s' not found. Available: [%s]" % (kind, name, keys))


def get_material(name): return _require(md.materials, name, "Material")
def get_oss(name):      return _require(model.oriented_selection_sets, name, "Oriented selection set")

def get_region(name):
    """Solid-model region: prefer an element set, fall back to an OSS."""
    try:
        return model.element_sets[name]
    except Exception:
        return _require(model.oriented_selection_sets, name, "Element set / OSS")


# ---------------------------------------------------------------------
# 1. FABRICS
# ---------------------------------------------------------------------
hc_fabric = md.create_fabric(name="HC",
                             material=get_material(MAT_HONEYCOMB),
                             thickness=HC_THICKNESS_MM * MM_TO_MODEL)
cf_fabric = md.create_fabric(name="CF",
                             material=get_material(MAT_CF),
                             thickness=CF_THICKNESS_MM * MM_TO_MODEL)
print("Created fabrics: HC (%g), CF (%g)" % (hc_fabric.thickness, cf_fabric.thickness))

# ---------------------------------------------------------------------
# 2. STACKUP  "Full Panel"  =  CF/0, CF/90, HC/0, CF/0, CF/90
# ---------------------------------------------------------------------
full_panel = md.create_stackup(name=STACKUP_NAME)
for fab, ang in [(cf_fabric, 0.0),
                 (cf_fabric, 90.0),
                 (hc_fabric, 0.0),
                 (cf_fabric, 0.0),
                 (cf_fabric, 90.0)]:
    full_panel.add_fabric(fab, ang)
print("Created stackup: '%s' (%d fabrics)" % (STACKUP_NAME, len(full_panel.fabrics)))

# ---------------------------------------------------------------------
# 3. MODELING GROUPS + PLIES  (one per part)
# ---------------------------------------------------------------------
for part in PARTS:
    mpg = model.create_modeling_group(name=part)
    mpg.create_modeling_ply(name="%s Ply" % part,
                            ply_material=full_panel,            # the "Full Panel" stackup
                            ply_angle=0.0,
                            oriented_selection_sets=(get_oss(part),))
    print("Modeling group + ply: '%s'" % part)

# ---------------------------------------------------------------------
# 4. SOLID MODELS  (one per part)
# ---------------------------------------------------------------------
for part in PARTS:
    ex = "monolithic" if part in MONOLITHIC_PARTS else "analysis_ply_wise"
    model.create_solid_model(name=part,
                             element_sets=[get_region(part)],
                             ex_type=ex)
    print("Solid model: '%s'  (ex_type = %s)" % (part, ex))

# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
model.update()
print("Done -- model updated. Continue in the GUI.")

# Optional: save a checkpoint .acph5
# model.save(r"C:\path\to\checkpoint.acph5", cache_data=True)
