# ANSYS GUI Semi-Automation Scripts

Python scripts that semi-automates the setup of composite and bumper analyses for the **Stanford Solar Car – Sunstruck chassis** within **ANSYS Workbench**.

---

## Setup

### 1. Prepare Geometry

Create three separate STEP files:

- 📦 Chassis panels
- 🚗 Front bumper
- 🚗 Side bumper

---

### 2. Run the Automation Script

First, downlowd all .py files from this repo. 

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



<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/f8c512ca-f5ba-4ece-8508-d0841f29193a" />

Finally, the script saves the Workbench project. The last thing that needs to be done manually in ANSYS Mechanical is to select the "panels only" mesh based on specific courseness. 
---
