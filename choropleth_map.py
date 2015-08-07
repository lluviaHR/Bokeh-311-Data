import csv
import shapefile
import sys
import operator
from bokeh.plotting import *
from bokeh.objects import HoverTool
from collections import OrderedDict
from bokeh.plotting import figure
from pandas import *

def loadComplaints(complaintsFilename):
  # Reads all complaints and keeps zips which have complaints.
  with open(complaintsFilename) as f:
    csvReader = csv.reader(f)
    headers = csvReader.next()
    zipIndex = headers.index('Incident Zip')
    latColIndex = headers.index('Latitude')
    lngColIndex = headers.index('Longitude')
    agencyIndex = headers.index('Agency')

    lat = []
    lng = []

    agencyDict = {}
    colors = []
    complaintsPerZip = {}

    for row in csvReader:
      try:
        lat.append(float(row[latColIndex]))
        lng.append(float(row[lngColIndex]))
        agency = row[agencyIndex]
        zipCode = row[zipIndex]
        if not agency in agencyDict:
          agencyDict[agency] = len(agencyDict)


        if zipCode in complaintsPerZip:
          if agency in complaintsPerZip[zipCode]:
            complaintsPerZip[zipCode][agency]+=1
          else:
            complaintsPerZip[zipCode][agency]=1
        else:
          complaintsPerZip[zipCode]={}
          complaintsPerZip[zipCode][agency]=1

      except:
        pass

    return {'zip_complaints': complaintsPerZip}


def getZipBorough(zipBoroughFilename):
  # Reads all complaints and keeps zips which have complaints.
  with open(zipBoroughFilename) as f:
    csvReader = csv.reader(f)
    csvReader.next()

    return {row[0]: row[1] for row in csvReader}


def drawPlot(shapeFilename, mapPoints, zipBorough):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)

  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [], "Agency":[], 'zipcode':[],'Complaints':[]}

  # Qualitative 6-class Set1
  colors = {'NYPD' : 'blue',
            'DOT' : 'yellow',
            'DOB' : 'purple',
            'DOE' : 'green',
            'HPD' : 'indigo',
            'FDNY': 'black',
            'DEP': 'orange',
            "DSNY": 'pink',
            'DPR': 'red',
            "DOHMH":"magenta",
            "DOF": "Plum",
            "DCA":"navy",
            "TLC": '#00FF7F',
            "HRA": 'linen',
            "CHALL":'Ivory',
            '3-1-1':'Marron',
            'EDC': 'gray',
            'DHS': 'peru',
            'DFTA': 'sienna',
            'DOITT': 'lavender',
            'OEM' : "olive",
            'OPS' : 'Cyan',
            'OATH': 'Teal',
            'DOP': 'gray',
            'MOC':'turquoise',
            'CAU' : 'violet',
            "CCRB" :'Aqua',
            "MOVA" : 'Blueviolet',
            'COIB' : 'Azure',
            "DCLA" : 'Gainsboro'}

  record_index = 0

  for r in dat.iterRecords():
    currentZip = r[0]

    # Keeps only zip codes in NY area.
    if currentZip in zipBorough:
      zipCodes.append(currentZip)

      # Gets shape for this zip.
      shape = dat.shapeRecord(record_index).shape
      points = shape.points

      # Breaks into lists for lat/lng.
      lngs = [p[0] for p in points]
      lats = [p[1] for p in points]

      # Stores lat/lng for current zip shape.
      polygons['lng_list'].append(lngs)
      polygons['lat_list'].append(lats)


      # Calculate color, according to number of complaints
      if currentZip in mapPoints['zip_complaints']:
          # agency1=

        # Top complaint type
        sortedlist = sorted(mapPoints['zip_complaints'][currentZip].items(), key=operator.itemgetter(1), reverse=True)
        agency = sortedlist[0][0]

        # print agency

        if agency in colors:
          color = colors[agency]
        else:
          color = 'white'

      else:
        color = 'white'
      polygons['color_list'].append(color)
      polygons['zipcode'].append(currentZip)
      polygons["Agency"].append(agency)
      polygons['Complaints'].append(sortedlist[0][1])


    record_index += 1


  # Creates the Plot
  output_file("Problem1.html", title="Agency with more complaints per Zipcode")
  hold()

  TOOLS="pan,hover,wheel_zoom,box_zoom,reset,previewsave"

  # source hover
  source=ColumnDataSource(data=dict(zipcodes=polygons['zipcode'], agency=polygons["Agency"], \
                                    complaints= polygons['Complaints'],))

  # Creates the polygons.
  patches(polygons['lng_list'], polygons['lat_list'], source=source,\
          fill_color=polygons['color_list'], line_color="gray", \
          tools=TOOLS, plot_width=1100, plot_height=700, \
          title="Agency with more complaints per Zipcode")

  # legend
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = polygons['Agency'][i])

  #  Hover
  hover=curplot().select(dict(type=HoverTool))
  hover.tooltips= OrderedDict([("Zipcode","@zipcodes"),("Top Agency","@agency"),("No.Complaints", "@complaints"),])

  show()


if __name__ == '__main__':
  if len(sys.argv) != 4:
    print 'Usage:'
    print sys.argv[0] \
    + '<complaintsfilename> <zipboroughfilename> <shapefilename>'
    print '\ne.g.: ' + sys.argv[0] \
    + ' data/complaints.csv zip_borough.csv data/nyshape.shp'
  else:
    mapPoints = loadComplaints(sys.argv[1])
    zipBorough = getZipBorough(sys.argv[2])
    drawPlot(sys.argv[3], mapPoints, zipBorough)
