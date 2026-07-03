# ANSYS Chassis (semi) Automation Scripts

Python scripts that partly automate the setup of composite and bumper analyses for the **Stanford Solar Car – Sunstruck chassis** within **ANSYS Workbench**.

---

## Included Scripts

| Script | Purpose |
|---------|---------|
| `workbench_setup(just_acp).py` | Creates an ACP-only Workbench project: imports the chassis geometry and material data, then runs the chassis Mechanical setup (thickness + named selections). |
| `workbench_setup(bumpers_included).py` | Creates the complete Workbench project — ACP plus Front Bumper and Side Bumper systems and the Static Structural / Structural Optimization analyses — imports all geometry, and meshes the bumper models. |
| `acp_materials_rosettes.py` | **ACP script 1:** creates the fabrics, the *Full Panel* stackup, and a centroid-based rosette for every element set. |
| `acp_oss_plies_solids.py` | **ACP script 2:** creates the oriented selection sets (following each rosette), the modeling groups + plies, and the solid models for every element set. |

> **Why two ACP scripts?** Each OSS locks in its rosette orientation at the moment it is created. Editing a rosette *after* its OSS exists does not update the OSS. Splitting the ACP setup lets you finalize every rosette first (script 1), then build the OSSs, plies, and solid models from those final rosettes (script 2).

---

# Shorter Setup Summary

1. In **ANSYS Workbench**, run either `workbench_setup(just_acp).py` or `workbench_setup(bumpers_included).py`, depending on whether you want only the ACP setup or the full ACP + bumper setup. The script prompts you to select the required geometry (STEP) files.

2. Open the **ACP Mechanical** model and generate the chassis mesh. Apply the element sizing and any selective refinement appropriate for your analysis.

3. At this point the Mechanical setup is complete: imported materials, named selections, thickness, and mesh.

4. In **ACP**, run `acp_materials_rosettes.py` to create the fabrics, the *Full Panel* stackup, and a rosette (centered on each element set) for every element set.

5. **Manually adjust the rosettes** — set each rosette's direction/flip per surface so it points along the offset you want.

6. In **ACP**, run `acp_oss_plies_solids.py`. It creates an OSS for every element set (orientation taken from that set's rosette), a modeling group with one *Full Panel* ply, and a solid model for every element set. All objects are linked by name.

7. Update the ACP model, then return to Workbench to continue with your analysis.

---

# Detailed Setup Summary

## Option A — ACP Only

### Required Geometry
- 📦 Chassis panels STEP file

### Step 1 — Run the Workbench Setup Script

In **ANSYS Workbench**:

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
- ✅ Assigns a **1 mm thickness** to every chassis (surface) body
- ✅ Creates a **Named Selection** for every body (all faces of that body, grouped)
- ✅ Saves the completed Workbench project

---

## Option B — ACP + Bumpers

### Required Geometry
- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file

### Step 1 — Run the Workbench Setup Script

In **ANSYS Workbench**:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(bumpers_included).py
```

When prompted, select the STEP files for the chassis and each bumper.

The script automatically:

**ACP setup**
- ✅ Creates an **ACP (Pre)** system
- ✅ Imports the **Carbon Fiber** and **Aluminum Honeycomb** material data
- ✅ Imports the chassis geometry
- ✅ Opens ACP Mechanical, assigns **1 mm thickness**, and creates a **Named Selection** per body

**Bumper setup**
- ✅ Creates **Front Bumper** and **Side Bumper** Mechanical Model systems
- ✅ Imports both bumper geometries
- ✅ Assigns **1 mm thickness** to all surface bodies
- ✅ Applies a **3 mm global mesh** and generates the mesh
- ✅ Creates the **Static Structural** and **Structural Optimization** systems
- ✅ Saves the completed Workbench project

---

## Chassis Mesh

Before the ACP scripts, open the **ACP Mechanical** model and generate the chassis mesh manually, with the element sizing and selective refinement appropriate for your analysis.

After the Workbench setup and meshing, the ACP model contains:

- ✅ Imported materials
- ✅ Imported geometry
- ✅ Mesh
- ✅ Element Sets

Open the ACP model to continue.

---

# ACP Setup

## Step 2 — Materials, Stackup, and Rosettes

In **ACP**:

```text
File → Run Script
```

Run:

```text
acp_materials_rosettes.py
```

The script automatically:

- ✅ Detects the imported **Carbon Fiber** and **Aluminum Honeycomb** materials
- ✅ Creates the **Carbon Fiber (CF)** and **Honeycomb (HC)** fabrics
- ✅ Creates the **Full Panel** stackup:

```text
Carbon Fiber (0°)
Carbon Fiber (90°)
Aluminum Honeycomb (0°)
Carbon Fiber (0°)
Carbon Fiber (90°)
```

- ✅ Creates a centroid-based **Rosette** for every element set (named to match the set)

---

## Step 3 — Finalize the Rosettes (manual)

Because each OSS takes its orientation from its rosette, set the rosettes **before** running script 2. For every rosette:

- Set the axis directions / flip so the rosette points along the desired **offset direction** for that surface
- Confirm the direction is correct per surface (it is **not** always radially outward — it varies by panel)

---

## Step 4 — OSS, Modeling Groups/Plies, and Solid Models

After all rosettes are finalized, in **ACP**:

```text
File → Run Script
```

Run:

```text
acp_oss_plies_solids.py
```

The script automatically:

- ✅ Creates an **Oriented Selection Set (OSS)** for every element set, scoped to that set
- ✅ Sets each OSS orientation from its **rosette's normal** (flipped so extrusion is inward, opposite the offset)
- ✅ Links each OSS to its matching **Rosette** as the reference direction
- ✅ Creates a **Modeling Group** for every element set with one **Full Panel** ply
- ✅ Creates a **Solid Model** for every element set, scoped to the matching **Extrusion Element Set**, using **Analysis Ply Wise** extrusion

**OSS orientation options** (top of `acp_oss_plies_solids.py`):

| Setting | Effect |
|---------|--------|
| `ORIENT_MODE = "rosette"` | Orientation follows each rosette (default). Other modes: `"radial_out"`, `"radial_in"`, `"mesh"`, `"fixed"`. |
| `ORIENT_FLIP = True` | Negates the direction so the solid extrudes inward (opposite the rosette/offset). Set `False` if it extrudes the wrong way. |
| `EX_TYPE = "analysis_ply_wise"` | Solid-model extrusion method. `MONOLITHIC_SETS` can override specific sets to `monolithic`. |

Update the ACP model, then return to Workbench to continue with your analysis.

---

## Important Notes

- `acp_materials_rosettes.py` and `acp_oss_plies_solids.py` build the ACP model **from scratch**. Run each **once** on a clean ACP model; to redo a step, clear the objects it created first.
- The bumper meshes are generated automatically by `workbench_setup(bumpers_included).py`.
- The chassis panel mesh must be generated **manually** and should be chosen based on the desired analysis accuracy.
- All ACP objects (element sets, rosettes, OSSs, modeling groups, solid models) are linked **by name**, so consistent element-set names are important.
