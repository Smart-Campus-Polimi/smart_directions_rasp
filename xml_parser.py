import xml.etree.ElementTree as ET

def find_name(root, pl_id):
	for parent in root:
		if (parent.attrib['placeid'] == pl_id):
			for office in parent.findall('name'):
				return office.text
		else:
			return None

def find_direction(root, pl_id, rasp_id):
	for place in root.findall('place'):
		if(int(place.attrib['placeid']) == pl_id):
			for direction in place.findall('directions'):
				for rasp in direction.findall('rasp'):
					if (rasp.attrib['id'] == rasp_id):
						return rasp.text
		else:
			return None

