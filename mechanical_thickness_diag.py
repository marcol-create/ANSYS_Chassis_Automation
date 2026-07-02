# =====================================================================
#  MECHANICAL diagnostic -- why isn't thickness setting?
# =====================================================================
#  Run in Mechanical via Automation > Run Macro.
#  Pops a summary and writes mech_thickness_diag.txt to your home folder.
# =====================================================================
import os
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import MessageBox

model = ExtAPI.DataModel.Project.Model
bodies = model.GetChildren(DataModelObjectCategory.Body, True)

lines = ["Bodies found: %d" % len(bodies), ""]
set_ok, failed = 0, 0
first_err = ""

for body in bodies:
    line = "Body '%s': " % body.Name
    # current thickness (surface bodies have a settable Thickness)
    try:
        line += "curThickness=%s " % body.Thickness
    except Exception as ex:
        line += "NO Thickness property (%s) " % ex
    # attempt to set
    try:
        body.Thickness = Quantity("1 [mm]")
        line += "-> SET OK (now %s)" % body.Thickness
        set_ok += 1
    except Exception as ex:
        line += "-> SET FAILED: %s" % ex
        failed += 1
        if not first_err:
            first_err = str(ex)
    lines.append(line)

summary = ("Total bodies: %d\nThickness set OK: %d\nFailed/skipped: %d"
           % (len(bodies), set_ok, failed))
if first_err:
    summary += "\n\nFirst failure:\n%s" % first_err

try:
    out = os.path.join(os.path.expanduser("~"), "mech_thickness_diag.txt")
    f = open(out, "w"); f.write("\n".join(lines)); f.close()
    summary += "\n\nDetails written to:\n%s" % out
except Exception as ex:
    summary += "\n\n(could not write file: %s)" % ex

MessageBox.Show(summary)
