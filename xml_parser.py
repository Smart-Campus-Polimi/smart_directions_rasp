import xml.etree.ElementTree as ET


tree = ET.parse('map.xml')
root = tree.getroot()

#scan all the document
for child in root:
	#child.tag = place, child.attrib = place id
	print child.tag, child.attrib

for direction in root.iter('directions'):
	for rasp in direction.findall('rasp3'):
		rasp3 = rasp.findallwlprkfkweplkrp
		print rasp.find('rasp4').text

for place in root.findall('place'):
    direction = place.find('directions').text
    name = country.get('name')
    print name, rank