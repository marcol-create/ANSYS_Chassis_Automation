# =====================================================================
#  WORKBENCH PROJECT SCHEMATIC BUILDER  (.py / IronPython)
# =====================================================================
#  Run from the Workbench Project window:
#     File > Scripting > Run Script File...  -> pick this file
#
#  Builds five systems, positioned and titled:
#     A  ACP (Pre)                "Panels"        (top-left)
#     B  Static Structural        "Side Impact"   (right of A)
#     C  Structural Optimization  "Front Impact"  (below B)
#     D  Mechanical Model         "Side bumper"   (below A)
#     E  Mechanical Model         "Front Bumper"  (below D)
#
#  Position is a layout hint; Workbench snaps systems to its grid.
#  No data links are created -- each block is standalone (see note at end).
# =====================================================================

# --- Block A : ACP (Pre) -------------------------------------------
tmpl_acp = GetTemplate(TemplateName="ACP (Pre)")
sysA = tmpl_acp.CreateSystem()
sysA.DisplayText = "Panels"

# --- Block B : Static Structural, right of A -----------------------
tmpl_struct = GetTemplate(TemplateName="Static Structural")
sysB = tmpl_struct.CreateSystem(Position="Right", RelativeTo=sysA)
sysB.DisplayText = "Side Impact"

# --- Block C : Structural Optimization, below B --------------------
tmpl_opt = GetTemplate(TemplateName="Structural Optimization")
sysC = tmpl_opt.CreateSystem(Position="Below", RelativeTo=sysB)
sysC.DisplayText = "Front Impact"

# --- Block D : Mechanical Model, below A ---------------------------
tmpl_mm = GetTemplate(TemplateName="Mechanical Model")
sysD = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysA)
sysD.DisplayText = "Side bumper"

# --- Block E : Mechanical Model, below D ---------------------------
sysE = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysD)
sysE.DisplayText = "Front Bumper"

# --- Optional: save the project ------------------------------------
# Save(FilePath="C:/path/to/project.wbpj", Overwrite=True)

# --- Optional: link systems (example, not enabled) -----------------
# Share Engineering Data / Model from A into B, etc.:
# edA = sysA.GetComponent(Name="Engineering Data")
# edB = sysB.GetComponent(Name="Engineering Data")
# edA.TransferData(TargetComponent=edB)
