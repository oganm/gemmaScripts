'''
# Data Matrix Export Script:
# Generates Expression Data Matrix (Unfiltered) from Input
# Accepts either Experiment ID or Short Name
# Revision: 26 April 2017
'''
# ------------------------------ INITIALIZATION ------------------------------
# Module Imports
from __future__ import print_function
import argparse
import os
import sys
from ElapseTime import ElapseTime
from SpringSupport import SpringSupport

# CLI Generation and Parsing
cliParser = argparse.ArgumentParser()
cliParser.add_argument('-u', required = False, default = None, help = 'Gemma username')
cliParser.add_argument('-p', required = False, default = None, help = 'Gemma password')
cliParser.add_argument('-i', required = True, default = None, help = 'File path for requested experiments')
cliParser.add_argument('-n', required = False, default = False, action = 'store_true', help = 'Short name flag')
cliOpts = cliParser.parse_args()

# Declaring Global Flags and Paths
valUser = None
valPassword = None
outputFolder = 'Output/'
globalTimer = ElapseTime()

if (cliOpts.u != None and cliOpts.p != None):
	valUser = cliOpts.u
	valPassword = cliOpts.p

# Start Spring Session and Service Declarations
sx = SpringSupport(valUser, valPassword)
edfService = sx.getBean('expressionDataFileService')
experimentService = sx.getBean('expressionExperimentService')
print('')

# ------------------------------ MAIN ------------------------------
print('Generating Data Matrices...')
tempExpHolder = []
experimentHolder = []
failHolder = []
with open(cliOpts.i, mode = 'rt') as inputFile:
	for everyLine in inputFile:
		tempExpHolder.append(everyLine.strip('\n'))

# Filter Non-existent Experiments
if cliOpts.n:
	for eeName in tempExpHolder:
		experiment = experimentService.findByShortName(eeName)
		if (experiment != None):
			experimentHolder.append(experiment)
		else:
			failHolder.append('{0} - Not Found'.format(eeName))
else:
	for eeID in tempExpHolder:
		experiment = experimentService.load(long(eeID))
		if (experiment != None):
			experimentHolder.append(experiment)
		else:
			failHolder.append('{0} - Not Found'.format(eeID))

# Create Data Matrices
successCount = 0
for eeIndex, experiment in enumerate(experimentHolder, start = 1):
	print('\rCurrently: {0}/{1}: {2}'.format(eeIndex, len(experimentHolder), experiment.shortName), end = '')
	sys.stdout.flush()
	
	tempPath = '{0}{1}.txt'.format(outputFolder, experiment.shortName)
	if (os.path.lexists(tempPath)):
		os.remove(tempPath)
	
	try:
		outFile = edfService.writeDataFile(experiment, False, tempPath, False)
		successCount += 1
	except:
		if cliOpts.n:
			failHolder.append('{0} - Data Missing'.format(experiment.shortName))
		else:
			failHolder.append('{0} - Data Missing'.format(experiment.id))
print('\r' + ' ' * 75 + '\r')

# Print Final Status
print('Successfully processed {0} requests.'.format(successCount))
if len(failHolder) > 0:
	print('The following datasets could not be proceesed:')
	for everyEntry in failHolder:
		print(str(everyEntry))

# ------------------------------ FINALIZATION ------------------------------
# Time Reporter
globalTimer.getElapse()

# End Spring Session
sx.shutdown()