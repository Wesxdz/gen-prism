"""
Generates a rectangular prism from 6 rectangles of welded rods
"""
import FreeCADGui
import FreeCAD
from FreeCAD import Base, Vector, Units, Rotation
import Sketcher
import Part
from math import pi, sin, cos

DOC = FreeCAD.activeDocument()
DOC_NAME = "PowerPrism"

def clear_doc():
    """
    Clear the active document deleting all the objects
    """
    for obj in DOC.Objects:
        DOC.removeObject(obj.Name)

def setview():
    """Rearrange View"""
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Gui.activeDocument().activeView().viewAxometric()


if DOC is None:
    FreeCAD.newDocument(DOC_NAME)
    FreeCAD.setActiveDocument(DOC_NAME)
    DOC = FreeCAD.activeDocument()
else:
    clear_doc()

unit_measurement = "in"
rod_diameter = 0.5
width = 20
height = 25
depth = 26

dim = DOC.addObject("Spreadsheet::Sheet", "Dim")

dim.setBackground('A1:G25', (0.137255,0.160784,0.196078))

dim.set("A1", "Power Prism")
dim.setForeground('A1', (1.0, 0.0, 1.0))

dim.set('C1', 'External')
# Internal values are calculated by user determined external frame measurements
dim.set('D1', 'Internal')

dim.set("B2", "Width")
dim.set("C2", "=" + str(width) + unit_measurement)
dim.setAlias("C2", "width")

dim.set("B3", "Height")
dim.set("C3", "=" + str(height) + unit_measurement)
dim.setAlias("C3", "height")

dim.set("B4", "Depth")
dim.set("C4", "=" + str(depth) + unit_measurement)
dim.setAlias("C4", "depth")

dim.set("B5", "Rod Diameter")
dim.set("C5", "=" + str(rod_diameter) + unit_measurement)
dim.setAlias("C5", "rod_diameter")

dim.setStyle('C2:C5', 'bold', 'add')
dim.setForeground('C2:C5', (1.0, 1.0, 1.0))

dim.setForeground('B2', (0.996078,0.172549,0.027451))
dim.setForeground('B3', (0.000000,0.870588,0.964706))
dim.setForeground('B4', (0.458824,0.866667,0.023529))
dim.setForeground('B5', (0.850980,0.741176,0.176471))

DOC.recompute()

# Visual representation of internal bounds
bounds = DOC.addObject("PartDesign::Body", 'Bounds')
s = bounds.newObject("Sketcher::SketchObject", 'Sketch')
s.Support = DOC.getObject("XY_Plane"),[""]
s.MapMode='FlatFace'
geoList = [Part.LineSegment(Vector(0.0, 0.0), Vector(1.0, 0.0)), Part.LineSegment(Vector(1.0, 0.0), Vector(1.0, 1.0)), 
Part.LineSegment(Vector(1.0, 1.0), Vector(0.0, 1.0)), Part.LineSegment(Vector(0.0, 1.0), Vector(0.0, 0.0))]

conList = [Sketcher.Constraint('Coincident',0,2,1,1), Sketcher.Constraint('Coincident',1,2,2,1), 
Sketcher.Constraint('Coincident',2,2,3,1), Sketcher.Constraint('Coincident',3,2,0,1),
Sketcher.Constraint('Horizontal',0), Sketcher.Constraint('Horizontal',2),
Sketcher.Constraint('Vertical',1), Sketcher.Constraint('Vertical',3),
Sketcher.Constraint('Coincident', 0, 1, -1, 1),
Sketcher.Constraint('DistanceY',3,2,3,1,100.000000),
Sketcher.Constraint('DistanceX',0,1,0,2,100.000000),
]

s.addGeometry(geoList, False)
s.addConstraint(conList)

s.setExpression('Constraints[9]', u'Dim.depth')
s.setExpression('Constraints[10]', u'Dim.width')

p = bounds.newObject("PartDesign::Pad", "Pad")
p.Profile = s
p.setExpression("Length", u'Dim.height')

boundsGui = FreeCADGui.getDocument('PowerPrism').getObject('Bounds')
boundsGui.Transparency = 85
boundsGui.ShapeColor = (0.21,0.27,0.31)
boundsGui.DisplayMode=u"Shaded"
boundsGui.BoundingBox=True
FreeCADGui.updateGui()

# Each face is an https://wiki.freecadweb.org/Std_Part
face_names = ["Front", "Right", "Back", "Left", "Top", "Bottom"]
sides = ["North", "East", "South", "West"]
dw = u'Dim.width'
dh = u'Dim.height'
dd = u'Dim.depth'
drd = u'Dim.rod_diameter'
rects = [[dw, dh], [dd, dh], [dw, dh], [dd, dh], [dw, dd], [dw, dd]]
# Each rod is a https://wiki.freecadweb.org/PartDesign_Body

faces = []

for i in range(6):
    face = DOC.addObject("App::Part", face_names[i])
    faces.append(face)
    for j in range(4):
        body = face.newObject("PartDesign::Body", sides[j] + 'Side')
        if j == 0:
            body.setExpression('.Placement.Base.z', rects[i][1])
        if j == 1:
            body.setExpression('.Placement.Base.x', rects[i][0])
        if j % 2 == 0:
            body.Placement.Rotation = Rotation(Vector(0, 1, 0), 90)
        sketch = body.newObject("Sketcher::SketchObject", 'Sketch')
        sketch.Support = DOC.getObject("XY_Plane"),[""]
        sketch.MapMode='FlatFace'
        sketch.addGeometry(Part.Circle(Vector(0, 0, 0), Vector(0, 0, 1), 1), False)
        sketch.addConstraint(Sketcher.Constraint("Diameter", 0, 1.0))
        sketch.setExpression("Constraints[0]", u'Dim.rod_diameter')

        pad = body.newObject("PartDesign::Pad", "Pad")
        pad.Profile = sketch
        pad.setExpression("Length",rects[i][j % 2])

faces[1].setExpression('Placement.Base.x', dw)
faces[1].Placement.Rotation = Rotation(Vector(0, 0, 1), 90)

faces[2].setExpression('Placement.Base.y', dd)

faces[3].Placement.Rotation = Rotation(Vector(0, 0, 1), 90)

faces[4].Placement.Rotation = Rotation(Vector(1, 0, 0), -90)
faces[4].setExpression('Placement.Base.z', dh)

faces[5].Placement.Rotation = Rotation(Vector(1, 0, 0), -90)

DOC.recompute()
setview()