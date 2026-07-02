# ANSYS GUI Automation Scripts

Python scripts written to run inside the **ANSYS Mechanical GUI** to automate repetitive simulation setup tasks for the **Stanford Solar Car – Sunstruck chassis**.

---

## Setup

### 1. Prepare Geometry

Create three separate STEP files:

- 📦 Chassis panels
- 🚗 Front bumper
- 🚗 Side bumper

---

### 2. Create the Workbench Project

In **ANSYS Workbench**, navigate to:

```text
File → Scripting → Run Script File
```

Select:

```text
workbench_schematic.py
```

The script will automatically:

- ✅ Create an **ACP (Pre)** system
- ✅ Create two **Mechanical** systems
- ✅ Link the systems appropriately
- ✅ Import the **Carbon Fiber** and **Aluminum Honeycomb** material data

---

### 3. Configure Geometry

Import the geometry files:

- **ACP (Pre)** → Chassis panels STEP file
- **Mechanical Model 1** → Side bumper STEP file
- **Mechanical Model 2** → Front bumper STEP file

---

### 4. Automatically Mesh the Bumpers

Back in **ANSYS Workbench**, navigate to:

```text
File → Scripting → Run Script File
```

Select:

```text
workbench_mesh_bumpers.py
```

The script will automatically:

- ✅ Open both **Front Bumper** and **Side Bumper** Mechanical models
- ✅ Assign a **1 mm thickness** to all surface bodies
- ✅ Apply a **3 mm global mesh**
- ✅ Generate the mesh
- ✅ Close Mechanical after meshing
- ✅ Save the Workbench project

> **Note:** This script performs the complete bumper meshing workflow directly from the Workbench Project window, so you never need to open Mechanical manually for the bumper analyses.

---

## Running the Mechanical Automation Script

1. Open the **ACP** model (this launches **ANSYS Mechanical**).
2. In Mechanical, navigate to:

```text
Automation → Run Macro
```

3. Select:

```text
mechanical_setup_gui.py
```

---

## What the Mechanical Script Does

The script automatically:

- ✅ Assigns a **1 mm thickness** to every chassis panel
- ✅ Creates **Named Selections** for every body
- ✅ Creates **Named Selections** for every grouped face imported from the STEP file

This eliminates the repetitive manual setup required before composite layup and structural analysis.
