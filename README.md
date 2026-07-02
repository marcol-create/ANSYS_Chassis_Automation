# ANSYS Chassis (semi) Automation Scripts

Python scripts that partly automates the setup of composite and bumper analyses for the **Stanford Solar Car – Sunstruck chassis** within **ANSYS Workbench**.

---

## Included Scripts

| Script | Purpose |
|---------|---------|
| `workbench_setup(just_acp).py` | Creates an ACP Workbench project, imports the chassis geometry, imports material data, and prepares the model for composite layup. |
| `workbench_setup(bumpers_included).py` | Creates the complete Workbench project, including ACP, Front Bumper, and Side Bumper systems, imports all geometry, meshes the bumper models, and creates the Static Structural and Structural Optimization analyses. |
| `acp_full_setup.py` | Automatically creates the composite layup by generating fabrics, stackups, rosettes, oriented selection sets, modeling groups, and plies for every element set. |
| `acp_solid_models.py` | Generates ACP solid models for every element set using **Analysis Ply Wise** extrusion. |

---
# Much Shorter Setup Summary

- In **ANSYS Workbench**, run either `workbench_setup(just_acp).py` or `workbench_setup(bumpers_included).py`, depending on whether you want only the ACP setup or the full ACP + bumper setup. The script will prompt you to select the required geometry files.

- Open the **ACP Mechanical** model and generate the chassis mesh. Apply the element sizing and selective mesh refinement appropriate for your analysis.

- At this point, the ANSYS Mechanical setup is complete, including the imported materials, named selections, and mesh.

- In **ACP**, run `acp_full_setup.py`. This script creates the fabrics, stackup, rosettes (centered on each element set), oriented selection sets (OSSs), and modeling groups. All objects are automatically linked by name. The remaining manual work is to define the rosette directions, OSS orientations, draping directions, ply flipping, and any face-specific orientation settings.

- After all rosette and OSS orientations have been finalized, run `acp_solid_models.py`. This creates the solid models and links them to the correct extrusion element sets using **Analysis Ply Wise** extrusion.

- Update the ACP model, then return to Workbench to continue with your analysis.

# Detailed Setup Summary

## Option A — ACP Only

### Required Geometry

- 📦 Chassis panels STEP file

### Step 1 — Run the Workbench Setup Script

In **ANSYS Workbench**, navigate to:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(just_acp).py
```

When prompted, select the **chassis panels STEP file**.

The script automatically:

- ✅ Creates an **ACP (Pre)** system
- ✅ Imports the **Carbon Fiber** and **Aluminum Honeycomb** material data
- ✅ Imports the chassis geometry
- ✅ Opens ACP Mechanical
- ✅ Assigns a **1 mm thickness** to every chassis panel
- ✅ Creates **Named Selections** for every body
- ✅ Creates **Named Selections** for every grouped face imported from the STEP file
- ✅ Saves the completed Workbench project

 <img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/a87d7abc-8d2d-4584-ae0f-30466b344d52" />


---

## Option B — ACP + Bumpers

### Required Geometry

- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file

### Step 1 — Run the Workbench Setup Script

In **ANSYS Workbench**, navigate to:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(bumpers_included).py
```

When prompted, select the files in the following order:

1. Chassis panels STEP file
2. Front bumper STEP file
3. Side bumper STEP file

The script automatically:

### ACP Setup

- ✅ Creates an **ACP (Pre)** system
- ✅ Imports the **Carbon Fiber** and **Aluminum Honeycomb** material data
- ✅ Imports the chassis geometry
- ✅ Opens ACP Mechanical
- ✅ Assigns a **1 mm thickness** to every chassis panel
- ✅ Creates **Named Selections** for every body
- ✅ Creates **Named Selections** for every grouped face imported from the STEP file

### Bumper Setup

- ✅ Creates **Front Bumper** and **Side Bumper** Mechanical systems
- ✅ Imports both bumper geometries
- ✅ Assigns a **1 mm thickness** to all surface bodies
- ✅ Applies a **3 mm global mesh**
- ✅ Generates the mesh
- ✅ Creates **Static Structural** analyses
- ✅ Creates **Structural Optimization** analyses
- ✅ Links all required systems automatically
- ✅ Saves the completed Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/cfa23791-5ce3-4ab2-8485-27b22d2ccaec" />

<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/efa12b9e-672d-4de3-8c31-1b5c85f4bba8" />




---

---

## Chassis Mesh

Before proceeding to the ACP scripts, open the **ACP Mechanical** model and generate the chassis mesh manually with preferred mesh coarseness before continuing to the ACP setup scripts.

---

# ACP Setup

After the Workbench setup script has finished, the ACP model will contain:

- ✅ Imported materials
- ✅ Imported geometry
- ✅ Mesh
- ✅ Element Sets

Open the ACP model to continue.

---

## Step 2 — Build the Composite Layup

In **ACP**, navigate to:

```text
File → Run Script
```

Run:

```text
acp_full_setup.py
```

The script automatically:

- ✅ Detects the imported **Carbon Fiber** and **Aluminum Honeycomb** materials
- ✅ Creates the **Carbon Fiber** and **Honeycomb** fabrics
- ✅ Creates the **Full Panel** stackup:

```text
Carbon Fiber (0°)
Carbon Fiber (90°)
Aluminum Honeycomb (0°)
Carbon Fiber (0°)
Carbon Fiber (90°)
```

- ✅ Creates a centroid-based **Rosette** for every element set
- ✅ Creates an **Oriented Selection Set (OSS)** for every element set
- ✅ Links each OSS to its corresponding Rosette
- ✅ Creates a **Modeling Group** for every element set
- ✅ Assigns one **Full Panel** ply to each Modeling Group


<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/abc9b72f-aae5-4aea-8dd8-40fdcc13c599" />
<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/ee2066ea-8e73-4585-8f7d-65701656dd91" />



---

## Step 3 — Review Composite Orientations

Before generating solid models, manually review each:

- Rosette
- Oriented Selection Set (OSS)

Update any orientation-specific settings, including:

- Fiber / lay-up direction
- Rosette axis directions
- Ply flipping
- Draping direction
- Any face-specific orientation adjustments

---

## Step 4 — Generate ACP Solid Models

After all orientations have been finalized, in **ACP** navigate to:

```text
File → Run Script
```

Run:

```text
acp_solid_models.py
```

The script automatically:

- ✅ Creates one solid model for every element set
- ✅ Assigns each solid model to its corresponding **Extrusion Element Set**
- ✅ Configures **Analysis Ply Wise** extrusion for every solid model

---

## Important Notes

- Both `acp_full_setup.py` and `acp_solid_models.py` are designed to build the ACP model from scratch. Run each script **once** on a clean ACP model.
- The bumper meshes are generated automatically by `workbench_setup(bumpers_included).py`.
- The chassis panel mesh must be generated manually and should be chosen based on the desired analysis accuracy.
