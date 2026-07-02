# ANSYS GUI Automation Scripts

Python scripts that automate the setup of composite and bumper analyses for the **Stanford Solar Car – Sunstruck chassis** within **ANSYS Workbench**.

---

## Setup

### 1. Prepare Geometry

Create the required STEP files.

### Option A — ACP Only

Required geometry:

- 📦 Chassis panels

Run:

```text
just_acp.py
```

When prompted, select the **chassis panels STEP file**.

The script will automatically:

- ✅ Create an **ACP (Pre)** system
- ✅ Import the Carbon Fiber and Aluminum Honeycomb material data
- ✅ Import the chassis geometry
- ✅ Open the ACP model in **ANSYS Mechanical**
- ✅ Assign a **1 mm thickness** to every chassis panel
- ✅ Create **Named Selections** for every body
- ✅ Create **Named Selections** for every grouped face imported from the STEP file
- ✅ Save the completed Workbench project

---

### Option B — ACP + Bumpers

Required geometry:

- 📦 Chassis panels
- 🚗 Front bumper
- 🚗 Side bumper

Run:

```text
bumpers_include.py
```

When prompted, select the files in the following order:

1. Chassis panels STEP file
2. Front bumper STEP file
3. Side bumper STEP file

The script will automatically:

#### ACP Setup

- ✅ Create an **ACP (Pre)** system
- ✅ Import the Carbon Fiber and Aluminum Honeycomb material data
- ✅ Import the chassis geometry
- ✅ Open the ACP model in **ANSYS Mechanical**
- ✅ Assign a **1 mm thickness** to every chassis panel
- ✅ Create **Named Selections** for every body
- ✅ Create **Named Selections** for every grouped face imported from the STEP file

#### Bumper Setup

- ✅ Create **Front Bumper** and **Side Bumper** Mechanical systems
- ✅ Import both bumper geometries
- ✅ Assign a **1 mm thickness** to all surface bodies
- ✅ Apply a **3 mm global mesh**
- ✅ Generate the mesh
- ✅ Create **Static Structural** analyses
- ✅ Create **Structural Optimization** analyses
- ✅ Link all required systems automatically

Finally, the script saves the completed Workbench project.

---

## Which Script Should I Use?

| If you want to... | Run |
|-------------------|-----|
| Set up only the composite chassis model in ACP | `just_acp.py` |
| Set up the complete chassis + bumper workflow (including Static Structural and Structural Optimization analyses) | `bumpers_include.py` |
