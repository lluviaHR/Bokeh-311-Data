import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.objects import HoverTool
from math import floor

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

		#print "complaintsPerZip: ", complaintsPerZip

	return {'zip_complaints': complaintsPerZip}


# In[9]:

def getZipBorough(zipBoroughFilename):
	# Reads all complaints and keeps zips which have complaints.
	with open(zipBoroughFilename) as f:
		csvReader = csv.reader(f)
		csvReader.next()

		return {row[0]: row[1] for row in csvReader}


# In[15]:

def drawPlot(shapeFilename, mapPoints, zipBorough, n):
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
	min_latitude = []
	max_latitude = []
	min_longitude = []
	max_longitude = []
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

			min_latitude.append(min(lats))
			max_latitude.append(max(lats))
			min_longitude.append(min(lngs))
			max_longitude.append(max(lngs))
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
		sortedlist = sorted(polygons['lat_list'], reverse = True)
	#sortedlist = sorted(polygons['lat_list'].items(), key=operator.itemgetter(1), reverse=True)
	max_lat = max(max_latitude)
	min_lat = min(min_latitude)
	min_lon = min(min_longitude)
	max_lon = max(max_longitude)
	#print max_lat, min_lat, max_lon, min_lon
	x_increment = (max_lat - min_lat)/float(n)
	y_increment = (max_lon - min_lon)/float(n)
	num_of_complaints = {}
	for i in polygons['lat_list']:
		#print polygons['lat_list'][i]
		for j in xrange(len(i)):
			#print i[j]
			x_box = int(floor((i[j]-min_lat)//x_increment))
			y_box = int(floor((polygons['lng_list'][polygons['lat_list'].index(i)][j]-min_lon)//y_increment))
			num_of_complaints.setdefault(x_box, {})
			count = num_of_complaints[x_box].setdefault(y_box, 0)
			num_of_complaints[x_box][y_box] = count + 1
	relative_Radius = []
	center_x = []
	center_y = []
	count_max = 0
	for i in num_of_complaints.keys():
		for j in num_of_complaints[i].keys():
			if num_of_complaints[i][j]>count_max:
				count_max = num_of_complaints[i][j]

	for i in num_of_complaints.keys():
		for j in num_of_complaints[i].keys():
			#print i,j, num_of_complaints[i][j]
			center_x.append(min_lat + x_increment*i + (x_increment/float(2)))
			center_y.append(min_lon + y_increment*j + (y_increment/float(2)))
			relative_Radius.append(num_of_complaints[i][j]/float(count_max)*(maxRadius-minRadius))

	source = ColumnDataSource(
		data=dict(
			hoverZip=hoverZip,
			hoverCompCount=hoverCompCount,
			hoverRadius=hoverRadius,
		)
	)

	# Creates the Plot
	output_file("Problem4.html", title="Complaints in n dimension")
	TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave"
	# Creates the polygons.
	patches(polygons['lng_list'], polygons['lat_list'], source=source, fill_color=polygons['color_list'], line_color="gray",\
            tools=TOOLS, plot_width=1100, plot_height=700, title="Complaints in n dimension")
	hold()

	circle(center_y, center_x, radius=relative_Radius,
		fill_color="#8B0000", fill_alpha=0.6, line_color=None)
	show()


if __name__ == '__main__':
	if len(sys.argv) != 5:
		print 'Usage:'
		print sys.argv[0] \
		+ ' <n> <complaintsfilename> <zipboroughfilename> <shapefilename>'
		print '\ne.g.: ' + sys.argv[0] \
		+ ' n data/complaints.csv zip_borough.csv data/nyshape.shp'
	else:

		complaintsFile = sys.argv[2]
		zipBoroughsFile = sys.argv[3]
		shapeFile = sys.argv[4]
		n = sys.argv[1]
		mapPoints = loadComplaints(complaintsFile)
		zipBorough = getZipBorough(zipBoroughsFile)
		drawPlot(shapeFile, mapPoints, zipBorough, n)


