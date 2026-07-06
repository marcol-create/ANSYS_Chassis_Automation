try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model
raise RuntimeError(
    "EDGE SETS: [%s]  ||  SOLID MODELS: [%s]  ||  ROSETTES: [%s]"
    % (", ".join(model.edge_sets.keys()),
       ", ".join(model.solid_models.keys()),
       ", ".join(model.rosettes.keys())))
