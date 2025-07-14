import win32com.client, pythoncom
import sys
from win32com.client import VARIANT


pythoncom.CoInitialize()

# Get dimensions from command-line (mm to meters)
length = float(sys.argv[1]) / 1000
width = float(sys.argv[2]) / 1000
height = float(sys.argv[3]) / 1000

# Start SolidWorks
swApp = win32com.client.Dispatch("SldWorks.Application")
swApp.Visible = True

# Template path (update if needed)
template = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\Part.prtdot"

# Open new part with dummy vars for errors/warnings
errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

part = swApp.OpenDoc6(template, 1, 0, "", errors, warnings)

if part is None:
    raise Exception("Failed to create new part.")

# Select Top Plane
callout = VARIANT(pythoncom.VT_DISPATCH, None)
selected = part.Extension.SelectByID2("Top Plane", "PLANE", 0, 0, 0, False, 0, callout, 0)
if not selected:
    raise Exception("Failed to select Top Plane.")

# Start sketch
part.SketchManager.InsertSketch(True)

# Draw rectangle
part.SketchManager.CreateCenterRectangle(0, 0, 0, length/2, width/2, 0)

# Exit sketch
part.ClearSelection2(True)
part.SketchManager.InsertSketch(True)

# Extrude feature
feat = part.FeatureManager.FeatureExtrusion2(
    True, False, False, 0, 0,
    height, 0,
    False, False, False, False,
    0, 0, False, False,
    False, False, True, True, True, 0, 0, False
)

if feat is None:
    raise Exception("Extrusion failed.")

print("✅ Solid block created successfully.")
