import sys, time
import win32com.client
import pythoncom
from win32com.client import VARIANT

print("📢 create_solidcylinder.py started", sys.argv)

if len(sys.argv) != 3:
    raise Exception("❌ Usage: python create_solidcylinder.py <diameter_mm> <height_mm>")

diameter = float(sys.argv[1]) / 1000
height = float(sys.argv[2]) / 1000

pythoncom.CoInitialize()
swApp = win32com.client.Dispatch("SldWorks.Application")
swApp.Visible = True
time.sleep(1)

# Create new part document using default template
template = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\Part.prtdot"
part = swApp.NewDocument(template, 0, 0, 0)
if not part:
    raise Exception("❌ Failed to create new part")

model = swApp.ActiveDoc
nullDispatch = VARIANT(pythoncom.VT_DISPATCH, None)

# ✅ Select Top Plane correctly
print("🛠 Selecting Top Plane with dispatch pointer")
if not model.Extension.SelectByID2("Top Plane","PLANE", 0, 0, 0, False, 0, nullDispatch, 0):
    raise Exception("❌ Top Plane selection failed")

# Start sketch and draw circle
model.SketchManager.InsertSketch(True)
model.SketchManager.CreateCircleByRadius(0, 0, 0, diameter/2)
model.SketchManager.InsertSketch(False)
time.sleep(0.3)

# ✅ Select sketch for extrusion
model.ClearSelection2(True)
if not model.Extension.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, False, 0, nullDispatch, 0):
    raise Exception("❌ Sketch selection failed")

# Extrude with FeatureExtrusion2
feat = model.FeatureManager.FeatureExtrusion2(
    True, False, False,
    0, 0,
    height, 0,
    False, False, False, False,
    0, 0,
    False, False, False, False,
    True, False, False, 0, 0, False
)
if not feat:
    raise Exception("❌ Extrusion failed")

print("✅ Solid cylinder created successfully")
