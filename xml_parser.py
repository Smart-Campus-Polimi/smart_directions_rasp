import xml.etree.ElementTree as ET


def find_name(pl_id):
	for parent in root:
		if (parent.attrib['placeid'] == pl_id):
			for office in parent.findall('name'):
				return office.text

def find_direction(pl_id, rasp_id):
	for parent in root:
		if (parent.attrib['placeid'] == pl_id):
			for direction in parent.findall('directions'):
				for rasp in direction:
					if (rasp.attrib['id'] == rasp_id):
						print "eccolo"


tree = ET.parse('map.xml')
root = tree.getroot()

#scan all the document
for parent in root:
	#parent.tag = place, parent.attrib = place id
	print parent.tag, parent.attrib
	for child in parent:
		print child.text



print "-------"
for place in root.iter('place'):
	for rasp in place.findall('name'):
		print rasp.text
	#	rasp3 = rasp.findall()
	#	print rasp.find('rasp4').text
print "@@@@@"

find_direction("3449", "A")

find_name("3449")
#for place in root.findall('place'):
#    direction = place.find('directions').text
#    name = place.get('name')
#    print name

