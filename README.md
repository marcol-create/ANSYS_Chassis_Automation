# ANSYS GUI Automation (semi) Scripts

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

# Setup

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

## Panel Meshing

🔵 **Panel Meshing:** The chassis panel mesh is intentionally left to the user. Before running the ACP scripts, generate the chassis mesh using the element size/coarseness appropriate for your analysis.

---

## Important Notes

- Both `acp_full_setup.py` and `acp_solid_models.py` are designed to build the ACP model from scratch. Run each script **once** on a clean ACP model.
- The bumper meshes are generated automatically by `workbench_setup(bumpers_included).py`.
- The chassis panel mesh must be generated manually and should be chosen based on the desired analysis accuracy.
