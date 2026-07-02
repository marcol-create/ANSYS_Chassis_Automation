# =====================================================================
#  ACP (Pre) -- one Solid Model per element set
# =====================================================================
#  Run INSIDE ACP (File > Run Script), AFTER acp_full_setup.py, once the
#  rosettes and oriented selection sets are finalized.
#
#  For every element set it creates a Solid Model of the same name, with
#  that element set assigned in the extrusion Element Sets. Extrusion
#  method defaults to Analysis Ply Wise (override per set below).
# =====================================================================

SKIP_SETS = ["All_Elements"]          # sets to ignore
EX_TYPE   = "analysis_ply_wise"       # default extrusion method
MONOLITHIC_SETS = set()               # names that should use "monolithic" instead
                                      # e.g. MONOLITHIC_SETS = {"Back Roof"}

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model


# ---- one solid model per element set ----
made = 0
for name in list(model.element_sets.keys()):
    if name in SKIP_SETS:
        continue
    es = model.element_sets[name]
    ex = "monolithic" if name in MONOLITHIC_SETS else EX_TYPE

    try:
        model.create_solid_model(name=name, element_sets=[es], ex_type=ex)
    except Exception:
        # fallback: create bare, then set method + attach element set
        sm = model.create_solid_model(name=name)
        try:
            sm.ex_type = ex
        except Exception as e1:
            print("  set ex_type failed '%s': %s" % (name, e1))
        try:
            sm.add_element_set(es)
        except Exception as e2:
            print("  add_element_set failed '%s': %s" % (name, e2))

    made += 1
    print("Solid model '%s'  (ex_type = %s)" % (name, ex))

model.update()
print("Done -- %d solid models created." % made)
