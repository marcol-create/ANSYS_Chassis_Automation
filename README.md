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

## What the Script Does

The script automatically:

- ✅ Assigns a **1 mm thickness** to every geometry
- ✅ Creates **Named Selections** for every body
- ✅ Creates **Named Selections** for every grouped face imported from the STEP file

This eliminates the repetitive manual setup required before composite layup and structural analysis.
