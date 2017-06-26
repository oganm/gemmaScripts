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

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# CLI Generation and Parsing
cliParser = argparse.ArgumentParser()
cliParser.add_argument('-u', required = False, default = None, help = 'Gemma username')
cliParser.add_argument('-p', required = False, default = None, help = 'Gemma password')
cliParser.add_argument('-o', required = False, default = 'Output/', help = 'Output directory')
cliParser.add_argument('-i', required = True, default = None, help = 'File path for requested experiments')
cliParser.add_argument('-n', required = False, default = False, action = 'store_true', help = 'Short name flag')
cliParser.add_argument('--ow', dest='overwrite', action='store_true')
cliParser.add_argument('--noow', dest='overwrite', action='store_false')
cliParser.set_defaults(overwrite=True)


cliOpts = cliParser.parse_args()

# Declaring Global Flags and Paths
valUser = None
valPassword = None
outputFolder = cliOpts.o + '/'
overwrite = cliOpts.overwrite
globalTimer = ElapseTime()

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

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



print(cliOpts.n)
if cliOpts.n:
	for eeName in tempExpHolder:
		tempPath = '{0}{1}.txt'.format(outputFolder, experiment.shortName)
		# check to see if the file exists
		if (os.path.lexists(tempPath) and not(overwrite)):
			continue
		
		experiment = experimentService.findByShortName(eeName)
		if (experiment != None):
			experimentHolder.append(experiment)
		else:
			failHolder.append('{0} - Not Found'.format(eeName))
else:
	for eeID in tempExpHolder:
		experiment = experimentService.load(long(eeID))
		# check to see if the file exists
		tempPath = '{0}{1}.txt'.format(outputFolder, experiment.shortName)
		if (os.path.lexists(tempPath) and not(overwrite)):
			continue
		
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
		if(overwrite):
			os.remove(tempPath)
		else:
			continue
	
	
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
