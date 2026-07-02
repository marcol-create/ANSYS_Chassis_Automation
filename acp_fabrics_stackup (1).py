# =====================================================================
#  ACP (Pre) -- fabrics + "Full Panel" stackup   (compolyx API)
# =====================================================================
#  Runs INSIDE ACP:
#    - from Workbench:  setup.RunScript(ScriptPath="...this file...")
#    - or manually:     File > Run Script  in the ACP editor
#  Requires the materials to already be imported (Engineering Data).
#
#  Instead of hard-coded names, it AUTO-DETECTS the honeycomb and the
#  carbon-fiber material from whatever is in the model, by keyword.
#
#  Builds:
#    HC  fabric  = <honeycomb material>, thickness 12.192
#    CF  fabric  = <carbon-fiber material>, thickness 0.127
#    "Full Panel" stackup = CF/0, CF/90, HC/0, CF/0, CF/90
# =====================================================================

# ---- CONFIG ----
# The material whose name contains one of these (case-insensitive, first
# key that matches wins) is used. Reorder / add terms to suit your names.
HC_KEYS = ["honeycomb", "al_hc", "hc", "alum"]
CF_KEYS = ["carbon", "cf", "fiber", "fibre"]

HC_THICKNESS = 12.192     # model length unit (mm if the model is mm-based)
CF_THICKNESS = 0.127
STACKUP_NAME = "Full Panel"

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()

model = db.active_model
md    = model.material_data


def find_material(keys, label):
    """First material whose name contains any keyword (case-insensitive)."""
    for k in keys:
        kl = k.lower()
        for name in md.materials.keys():
            if kl in name.lower():
                print("%s material -> '%s'" % (label, name))
                return md.materials[name]
    avail = ", ".join("'%s'" % n for n in md.materials.keys())
    raise KeyError("No %s material found (tried %s). Available: [%s]"
                   % (label, keys, avail))


# ---- fabrics ----
hc_mat = find_material(HC_KEYS, "Honeycomb")
cf_mat = find_material(CF_KEYS, "Carbon fiber")

hc = md.create_fabric(name="HC", material=hc_mat, thickness=HC_THICKNESS)
cf = md.create_fabric(name="CF", material=cf_mat, thickness=CF_THICKNESS)
print("Fabrics created: HC (%g), CF (%g)" % (hc.thickness, cf.thickness))

# ---- stackup: CF/0, CF/90, HC/0, CF/0, CF/90 ----
full = md.create_stackup(name=STACKUP_NAME)
for fab, ang in [(cf, 0.0), (cf, 90.0), (hc, 0.0), (cf, 0.0), (cf, 90.0)]:
    full.add_fabric(fab, ang)
print("Stackup '%s' created (%d fabrics)." % (STACKUP_NAME, len(full.fabrics)))

model.update()
print("Done.")
