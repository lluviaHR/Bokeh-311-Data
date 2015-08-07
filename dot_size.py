import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.objects import HoverTool

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

		complaintsPerZip = {}

		for row in csvReader:
			try:
				lat.append(float(row[latColIndex]))
				lng.append(float(row[lngColIndex]))
				zipCode = row[zipIndex]

				if zipCode in complaintsPerZip:
					complaintsPerZip[zipCode]+=1
				else:
					complaintsPerZip[zipCode]=1

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
	polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [], 'cirlat_list' : [] ,'cirlng_list' : [], 'radius_list' : []}

	hoverZip = list()
	hoverCompCount = list()
	hoverRadius = list()

	# Top complaint number total
	sortedlist = sorted(mapPoints['zip_complaints'].items(), key=operator.itemgetter(1), reverse=True)
	complaintsTotal = sortedlist[0][1]

	minRadius=0.00015
	maxRadius=0.015

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


			# Calculate circle radius, according to number of complaints
			if currentZip in mapPoints['zip_complaints']:
				compCount = mapPoints['zip_complaints'][currentZip]


				percentage = float(compCount)/float(complaintsTotal)

				relRadius = (maxRadius-minRadius)*percentage

				color = '#C0C0C0'
			else:
				color = '#magenta'
				compCount = 0
				relRadius = 0


			# we try to find the center of polygon
			lngmiddle = min(lngs)+((max(lngs)-min(lngs))/2)
			latmiddle = min(lats)+((max(lats)-min(lats))/2)

			hoverZip.append(currentZip)
			hoverCompCount.append(compCount)
			hoverRadius.append(relRadius*100)
			polygons['color_list'].append(color)

			polygons['cirlat_list'].append(latmiddle)
			polygons['cirlng_list'].append(lngmiddle)
			polygons['radius_list'].append(relRadius)

		record_index += 1

	source = ColumnDataSource(
		data=dict(
			hoverZip=hoverZip,
			hoverCompCount=hoverCompCount,
			hoverRadius=hoverRadius,
		)
	)

	# Creates the Plot
	output_file("Problem4.html", title="Proportional Number of Complaints Per Zipcode")

	TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave"

	patches(polygons['lng_list'], polygons['lat_list'], source=source, fill_color=polygons['color_list'], line_color="gray",\
            tools=TOOLS, plot_width=1100, plot_height=700, title="Proportional Number of Complaints Per Zipcode")
	hold()

	circle(polygons['cirlng_list'], polygons['cirlat_list'], radius=polygons['radius_list'],
		fill_color="#8B0000", fill_alpha=0.6, line_color=None)

	show()

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print 'Usage:'
		print sys.argv[0] \
		+ ' <complaintsfilename> <zipboroughfilename> <shapefilename>'
		print '\ne.g.: ' + sys.argv[0] \
		+ 'data/complaints.csv zip_borough.csv data/nyshape.shp'
	else:

		complaintsFile = sys.argv[1]
		zipBoroughsFile = sys.argv[2]
		shapeFile = sys.argv[3]

		mapPoints = loadComplaints(complaintsFile)
		zipBorough = getZipBorough(zipBoroughsFile)
		drawPlot(shapeFile, mapPoints, zipBorough)


