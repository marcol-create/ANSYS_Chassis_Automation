# ANSYS Chassis (Semi) Automation Scripts

Python scripts that automates repetitive parts of setup for composite and bumper analyses for **Sunstruck** chassis in **ANSYS Workbench** and **ACP**.

---

# Included Scripts

| Script | Purpose |
|---------|---------|
| `workbench_setup(just_acp).py` | Creates an ACP-only Workbench project, imports the chassis geometry and material data, and performs the Mechanical setup (thickness + named selections). |
| `workbench_setup(bumpers_included).py` | Creates the complete Workbench project with ACP, Front Bumper, and Side Bumper systems, imports all geometry, meshes the bumper models, and creates the Static Structural and Structural Optimization analyses. |
| `acp_materials_rosettes.py` | Creates the Carbon Fiber and Honeycomb fabrics, the **Full Panel** stackup, and one rosette for every element set. |
| `acp_oss_plies_solids.py` | Creates the oriented selection sets (OSSs), modeling groups, plies, and solid models from the finalized rosettes. |

---

# Quick Workflow

1. **Run a Workbench setup script**
   - Run either `workbench_setup(just_acp).py` or `workbench_setup(bumpers_included).py`.
   - The script creates the Workbench project, imports the geometry and material data, generates the required Named Selections, and (if using the bumper workflow) automatically meshes the bumper models and creates the Static Structural and Structural Optimization analyses.

2. **Generate the chassis mesh**
   - Open the ACP Mechanical model and create the chassis mesh using the element sizing and selective refinement appropriate for your analysis.

3. **Create the composite model**
   - Run `acp_materials_rosettes.py`.
   - The script creates the Carbon Fiber and Honeycomb fabrics, the **Full Panel** stackup, and one rosette for every element set.

4. **Finalize the rosette orientations**
   - **Manual step:** Review each rosette and adjust its direction and flip to match the desired fiber/offset direction for each panel.

5. **Generate the ACP model**
   - Run `acp_oss_plies_solids.py`.
   - The script creates the Oriented Selection Sets (OSSs), Modeling Groups, Full Panel plies, and Solid Models for every element set, automatically linking everything by name.

6. **Update ACP**
   - Update the ACP model, then return to Workbench to continue with your composite or structural analyses.
---

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

---

# 2. Mesh the Chassis

Open the **ACP Mechanical** model and generate the chassis mesh.

Choose the element sizing and any local mesh refinement appropriate for your analysis.

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

Before continuing, manually orient each rosette.

For every rosette, verify:

- Direction
- Flip
- Offset direction

Each surface may require a different orientation.

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

### OSS Orientation Options

<img width="607" height="1075" alt="image" src="https://github.com/user-attachments/assets/fccf9a34-4582-4a3e-9a8b-fa1b4c5328a8" />

### ACP Objects

<img width="520" height="736" alt="image" src="https://github.com/user-attachments/assets/4b692e55-4761-425c-a9fe-2e7063166209" />

### Final ACP Model

<img width="1128" height="723" alt="image" src="https://github.com/user-attachments/assets/fdecc10c-1c5f-4252-a346-9c8117733a1e" />

Update the ACP model, then return to Workbench to continue with your analysis.

---

# Notes

- Run each ACP script **once** on a clean ACP model.
- Generate the **chassis mesh manually** before running the ACP scripts.
- The **bumper meshes** are generated automatically by `workbench_setup(bumpers_included).py`.
- All ACP objects (element sets, rosettes, OSSs, modeling groups, plies, and solid models) are linked by matching names, so avoid renaming element sets after setup.
