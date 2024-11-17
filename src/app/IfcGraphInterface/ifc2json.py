import ifcopenshell
import json

# Load IFC file
ifc_file = ifcopenshell.open("example.ifc")

# Convert IFC elements to a list of dictionaries
ifc_data = [entity.get_info() for entity in ifc_file]

# Save as JSON
with open("output.json", "w") as json_file:
    json.dump(ifc_data, json_file)
