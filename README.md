# ANSYS Chassis (Semi) Automation Scripts

Python scripts that automate the repetitive parts of setting up composite and bumper analyses for the **Sunstruck** chassis in **ANSYS Workbench** and **ACP**.

---

# Included Scripts

| Script | Purpose |
|---------|---------|
| `workbench_setup(just_acp).py` | Creates an ACP-only Workbench project. Prompts for the chassis geometry, finds and imports the material data from your computer, and does the Mechanical setup (thickness + named selections). |
| `workbench_setup(bumpers_included).py` | Creates the full Workbench project with ACP, Front Bumper, and Side Bumper systems. Imports all geometry, meshes the bumper models, and creates the Static Structural and Structural Optimization analyses. |
| `workbench_setup(with_rollcage).py` | Same as the bumpers project, plus a Rollcage Mechanical Model that imports the rollcage geometry and meshes it (MultiZone hex sweep, default steel — no composite material import). |
| `acp_materials_rosettes.py` | Creates the Carbon Fiber and Honeycomb fabrics, the **Full Panel** stackup, and one rosette per element set, centered automatically (orienting is still manual). |
| `acp_oss_plies_solids.py` | Creates the oriented selection sets (OSSs), modeling groups, plies, and solid models from the finalized rosettes. |

---

## Quick Workflow
Before starting in Ansys, prep the file in Fusion: surface-offset the faces by 0.00 mm, give the bumper parts their own files, and save as `.step`.
Also grab the material data if you don't have it yet (the files are in this repo too).

1. **Run a Workbench setup script (new Workbench file)**
   - Run `workbench_setup(just_acp).py`, `workbench_setup(bumpers_included).py`, or `workbench_setup(with_rollcage).py` through **Workbench → File → Scripting**.
   - The script creates the Workbench project, pulls in the material data from your computer, lets you pick the geometry file(s), generates the Named Selections, and — for the bumper and rollcage workflows — meshes the bumper/rollcage models and creates the Static Structural and Structural Optimization analyses.

2. **Generate the chassis mesh (Mechanical)**
   - Open the ACP Mechanical model and mesh the chassis at whatever coarseness fits your analysis.

3. **Create the composite model (ACP)**
   - Run `acp_materials_rosettes.py` in **ACP → File → Run Script**.
   - This creates the Carbon Fiber and Honeycomb fabrics, the **Full Panel** stackup, and one rosette per element set. The rosettes are centered but still need manual orienting.

4. **Finalize the rosette orientations**
   - **Manual step:** go through each rosette and set its direction and flip to match the fiber/offset direction you want for that panel.

5. **Generate the ACP model**
   - Run `acp_oss_plies_solids.py` in **ACP → File → Run Script**.
   - This creates the Oriented Selection Sets (OSSs), Modeling Groups, **Full Panel** plies, and Solid Models for every element set, linking everything by name.
   - Assign draping as needed.

6. **Update ACP**
   - Update the ACP model, then head back to Workbench to continue with the structural analyses.

---

# Summary of Manual Parts

- Meshing (Mechanical)
- Rosette orientation (ACP)
- Draping (ACP)

# More detailed steps
# 1. Workbench Setup

## Option A — ACP Only

### Required Geometry

- 📦 Chassis panels STEP file

In **ANSYS Workbench**:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(just_acp).py
```

Select the chassis STEP file when prompted.

The script creates:

- ✅ ACP (Pre) system
- ✅ Imports Carbon Fiber and Aluminum Honeycomb material data
- ✅ Imports the chassis geometry
- ✅ Opens ACP Mechanical
- ✅ Assigns a **1 mm** thickness to every surface body
- ✅ Creates a Named Selection for every body
- ✅ Saves the Workbench project

---

## Option B — ACP + Bumpers

### Required Geometry

- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file

In **ANSYS Workbench**:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(bumpers_included).py
```

Select the chassis, front bumper, and side bumper STEP files when prompted.

The script creates:

### ACP

- ✅ ACP (Pre) system
- ✅ Imports Carbon Fiber and Aluminum Honeycomb material data
- ✅ Imports the chassis geometry
- ✅ Opens ACP Mechanical
- ✅ Assigns a **1 mm** thickness to every surface body
- ✅ Creates a Named Selection for every body

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />



### Bumpers

- ✅ Front and Side Bumper Mechanical systems
- ✅ Imports bumper geometry
- ✅ Assigns **1 mm** thickness to all surface bodies
- ✅ Generates a **3 mm** global mesh
- ✅ Creates Static Structural analyses
- ✅ Creates Structural Optimization analyses
- ✅ Saves the Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/e8c1fed6-32fb-4de7-b3f2-82b00256fe39" />
<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/b690991e-21c5-437b-bdd1-010254c5b993" />

---

## Option C — ACP + Bumpers + Rollcage

Same as Option B, with an added Rollcage Mechanical Model.

### Required Geometry

- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file
- 🧰 Rollcage STEP file (solid, hollow tubes)

In **ANSYS Workbench**:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(with_rollcage).py
```

Select the chassis, front bumper, side bumper, and rollcage STEP files when prompted (in that order).

Everything from Option B, plus:

### Rollcage

- ✅ Rollcage Mechanical Model system
- ✅ Imports the rollcage geometry
- ✅ Keeps the default **Structural Steel** material (no composite material import for this block)
- ✅ Meshes with a **MultiZone hex sweep**, sized for the tube wall

> **Rollcage mesh note:** The tubes are hollow, so a plain coarse mesh doesn't resolve the wall. The script uses a MultiZone (hex sweep) mesh instead. Set `ROLLCAGE_SIZE` (top of the rollcage command in the script) to about **wall thickness ÷ 3** to get 2–3 elements across the wall. MultiZone sweeps the straight tube sections into hex and falls back to tets at the junctions. If you'd rather have a much lighter model, the tubes can instead be built as beams (line bodies with tube cross-sections) in SpaceClaim.

---

# 2. Mesh the Chassis

Open the **ACP Mechanical** model and generate the chassis mesh.

Pick the element sizing and any local refinement that fits your analysis.

<img width="2560" height="1540" alt="image" src="https://github.com/user-attachments/assets/cd505e9f-45f0-4a9a-a5b1-fe7f8f1bc9b8" />

---

# 3. ACP Materials, Stackup & Rosettes

In **ACP**:

```text
File → Run Script
```

Run:

```text
acp_materials_rosettes.py
```

The script creates:

- ✅ Carbon Fiber fabric
- ✅ Honeycomb fabric
- ✅ **Full Panel** stackup

```
Carbon Fiber (0°)
Carbon Fiber (90°)
Aluminum Honeycomb (0°)
Carbon Fiber (0°)
Carbon Fiber (90°)
```

- ✅ One centroid-based rosette for every element set

<img width="610" height="979" alt="image" src="https://github.com/user-attachments/assets/13564262-c9be-40b3-acc7-a719828bf01a" />

---

# 4. Finalize the Rosettes (Manual)

Before continuing, orient each rosette by hand.

For every rosette, check:

- Direction
- Flip
- Offset direction

Each surface may need a different orientation.

---

# 5. OSSs, Plies & Solid Models

In **ACP**:

```text
File → Run Script
```

Run:

```text
acp_oss_plies_solids.py
```

The script creates:

- ✅ One Oriented Selection Set (OSS) per element set
- ✅ One Modeling Group with a **Full Panel** ply per element set
- ✅ One Solid Model per element set
- ✅ **Analysis Ply Wise** extrusion
- ✅ Links all ACP objects by matching names

<table>
  <tr>
    <td align="center"><b>OSS Orientation Options</b></td>
    <td align="center"><b>ACP Objects</b></td>
  </tr>
  <tr>
    <td align="center"><img height="460" alt="OSS Orientation Options" src="https://github.com/user-attachments/assets/fccf9a34-4582-4a3e-9a8b-fa1b4c5328a8" /></td>
    <td align="center"><img height="460" alt="ACP Objects" src="https://github.com/user-attachments/assets/4b692e55-4761-425c-a9fe-2e7063166209" /></td>
  </tr>
</table>

### Final ACP Model



Update the ACP model, then return to Workbench to continue with your analysis.

---

# Notes

- Run each ACP script **once** on a clean ACP model.
- Mesh the **chassis manually** before running the ACP scripts.
- The **bumper meshes** are generated automatically by `workbench_setup(bumpers_included).py`.
- The **rollcage mesh** is generated automatically by `workbench_setup(with_rollcage).py` (MultiZone hex sweep); set `ROLLCAGE_SIZE` to roughly the tube wall thickness ÷ 3.
- All ACP objects (element sets, rosettes, OSSs, modeling groups, plies, and solid models) are linked by matching names, so avoid renaming element sets after setup.
