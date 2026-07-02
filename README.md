# ANSYS Chassis Automation
Scripts written to run within Ansys GUI to automate tedious/repetitive parts of simulation setup. Tailored to Stanford Solar Car "Sunstruck" chassis.


First, create a step file for the panels, one for the front bumper, and one for the side bumper. 

Create an ACP block for the panel file, then create a mechanical model block for the front bumper, and a mechanical model block for the side bumper. 

In the ACP block, import your material data for alluminum honeycomb and carbon fiber. 
Then, in that same ACP block, upload your chassis step file, with just the panels. 

For one mechanical model geometry, upload the step file for the side bumper, and in the other, upload the step file for the front bumper. 

Then open the ACP model; this should take you to ANSYS Mechanical. 
In Mechanical, go to "Automation" and press "Run Macro". Upload the "mechanical_setup_gui.py" 
This will first give all geometries a thickness 1mm, and then cocomplete the step of creating a named selection for each geometry, including each face that was grouped in the .step file. 








