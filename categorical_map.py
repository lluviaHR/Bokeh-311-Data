import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import random
from bokeh.objects import HoverTool
from collections import OrderedDict
from math import floor

agencyDict = {}



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

    #agencyDict = {}
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


def drawPlot(shapeFilename, mapPoints, zipBorough, agency1, agency2):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)

  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  Agency1=agency1
  Agency2=agency2
  polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [], 'zip_code': [], 'bin_ratio':[]}



  # colors_palate = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DD1C77", "#980043" ']
  # bin_construction= ['0-0.5', '0.5-1.0', '1.0-1.5', '1.5-2', '2-inf']
  # bins = 0.5
 # ["#E5E5E5", "#E5CCD6",  "#E5B2C7","#E599B8",  "#E57FAA",  , "#E5537D", "#FF3366",  '#FF1952', '#FF006A']
   # colors_palate = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DD1C77", "#980043", ]
  colors_sp= ["#f7f4f9", "#e7e1ef", "#d4b9da", "#E5669B", "#E54C8C","#c994c7", "#df65b0" ,"#e7298a" ,"#ce1256" ,"#980043" ,"#67001f"]
  bin_construction= ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0', '1.0-1.2', '1.2-1.4', '1.4-1.6', '1.6-1.8','1.8-2.0', '2-inf']
  bins = 0.2



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


        color = str()
        bin_ratio = 1
        #ratio = float(1000)
        if agency1 in mapPoints['zip_complaints'][currentZip].keys() and agency2 in mapPoints['zip_complaints'][currentZip].keys():
          if mapPoints['zip_complaints'][currentZip][agency2] != 0:
            ratio = mapPoints['zip_complaints'][currentZip][agency1]/(mapPoints['zip_complaints'][currentZip][agency2]*1.0)
          elif mapPoints['zip_complaints'][currentZip][agency2] == 0:
            ratio = float('inf')
          else:
            color = 'white'
        if color != 'white':
          if ratio != 'inf':
            bin_ratio = int(floor(ratio//bins))
            if bin_ratio >= 10:
              bin_ratio = 10
          else:
            bin_ratio = 10
          color = colors_sp[bin_ratio]
      else:
        color = 'white'


      polygons['zip_code'].append(currentZip)
      polygons['color_list'].append(color)
      polygons['bin_ratio'].append(bin_construction[bin_ratio])


    record_index += 1

  output_file("Problem2.html", title="choropleth_map")
  hold()
  source = ColumnDataSource(data = dict(x = polygons['lat_list'], y =polygons['lng_list'], zip_code = polygons['zip_code'],ratio = polygons['bin_ratio']))
  TOOLS="pan,hover,wheel_zoom,box_zoom,reset,previewsave"

  # Creates the polygons.

  patches(polygons['lng_list'], polygons['lat_list'], \
        fill_color=polygons['color_list'], line_color="gray", \
        source = source,\
        tools=TOOLS, plot_width=900, plot_height=700, \
        title="Comparison of Complaints  Between Agencies per Zipcode")
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = agency1)
  for i in xrange(len(polygons['lat_list'])):
    scatter(2,2, color = polygons['color_list'][i], legend = agency2)
  # for i in xrange(len(polygons['lat_list'])):
  #   scatter(1,1, color = polygons['color_list'][i], legend = polygons["agency2"])
  hover = curplot().select(dict(type = HoverTool))
  hover.tooltips = OrderedDict([("Zip Code",'@zip_code'),("ratio","@ratio")])

  show()


if __name__ == '__main__':

  mapPoints = loadComplaints(sys.argv[1])
  zipBorough = getZipBorough(sys.argv[2])
  drawPlot(sys.argv[3], mapPoints, zipBorough, sys.argv[4], sys.argv[5])
