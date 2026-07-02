# ANSYS GUI Automation (Semi) Scripts

Python scripts that automate the setup of composite and bumper analyses for the **Stanford Solar Car – Sunstruck chassis** within **ANSYS Workbench**.

---

## Setup

### 1. Prepare Geometry

Create three separate STEP files:

- 📦 Chassis panels
- 🚗 Front bumper
- 🚗 Side bumper

---

### 2. Run the Automation Script

In **ANSYS Workbench**, navigate to:

```text
File → Scripting → Run Script File
```

Select:

```text
workbench_setup.py
```

When prompted, select the following files in order:

1. Chassis panels STEP file
2. Front bumper STEP file
3. Side bumper STEP file

---

## What the Script Does

The script automatically:

### Workbench Setup

- ✅ Creates an **ACP (Pre)** system
- ✅ Creates two **Mechanical** systems (Front Bumper and Side Bumper)
- ✅ Orders all systems appropriately
- ✅ Imports the **Carbon Fiber** and **Aluminum Honeycomb** material data
- ✅ Imports each selected geometry into its corresponding system

### Chassis (ACP) Preparation

- ✅ Opens the ACP model in **ANSYS Mechanical**
- ✅ Assigns a **1 mm thickness** to every chassis panel
- ✅ Creates **Named Selections** for every body
- ✅ Creates **Named Selections** for every grouped face imported from the STEP file

### Bumper Preparation

For both the **Front Bumper** and **Side Bumper** Mechanical models, the script:

- ✅ Assigns a **1 mm thickness** to all surface bodies
- ✅ Applies a **3 mm global mesh**
- ✅ Generates the mesh

Finally, the script saves the completed Workbench project.

---

After the script finishes, the project is fully prepared for composite layup in ACP and structural analysis of the bumper models, eliminating nearly all repetitive setup steps. Next steps to work on, update ACP model, try to work on automating meshing for ACP part. 
