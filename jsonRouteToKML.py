import json
import sys

# take a json string of the route, and use it to print out a kml file depicting a line of that route
def jsonRouteToKML(jsonStr):
  j = json.loads(jsonStr)

  print '<?xml version="1.0" encoding="UTF-8"?>'
  print '<kml xmlns="http://www.opengis.net/kml/2.2">'
  print '  <Document>'
  print "    <name>Route ID " + str(j[u'id']) + "</name>"
  print '    <description>Route as collected from PedalPDX Android App.</description>'
  print '    <Style id="line">'
  print '      <LineStyle>'
  print '        <color>7fff0000</color>'
  print '        <width>4</width>'
  print '      </LineStyle>'
  print '      <PolyStyle>'
  print '        <color>7f00ff00</color>'
  print '      </PolyStyle>'
  print '    </Style>'
  print '    <Placemark>'
  print '      <name>Route ID ' + str(j[u'id']) + '</name>'
  print '      <description>Route as collected from PedalPDX Android App.</description>'
  print '      <styleUrl>#line</styleUrl>'
  print '      <LineString>'
  print '        <extrude>1</extrude>'
  print '        <tessellate>1</tessellate>'
  print '        <altitudeMode>absolute</altitudeMode>'
  print '        <coordinates>'
  for points in j[u'points']:
    print '          ' + str(points[u'longitude']) + "," + str(points[u'latitude']) + ',0'
  print '        </coordinates>'
  print '      </LineString>'
  print '    </Placemark>'
  print '  </Document>'
  print '</kml>'

f = open(sys.argv[1], 'r')
jsonStr = f.read()
jsonRouteToKML(jsonStr)
