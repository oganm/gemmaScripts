from __future__ import print_function
import argparse
import os
import sys
import re
# from MetaBiomHelpers import *
from SpringSupport import SpringSupport
from ubic.gemma.core.datastructure.matrix import ExpressionDataWriterUtils
from ubic.gemma.model.genome.gene.phenotype.valueObject import CharacteristicValueObject

# CLI Generation and Parsing
cliParser = argparse.ArgumentParser()
cliParser.add_argument('-u', required = False, default = None, help = 'Gemma username')
cliParser.add_argument('-p', required = False, default = None, help = 'Gemma password')
cliParser.add_argument('-o', required = False, default = None, help = 'Output file')
cliOpts = cliParser.parse_args()

# Declaring Global Flags and Paths
valUser = None
valPassword = None
taxonCol = ['human', 'mouse']
outputFile = 'metaOutput.tsv'

if (cliOpts.u != None and cliOpts.p != None):
	valUser = cliOpts.u
	valPassword = cliOpts.p

if (cliOpts.o != None):
	outputFile = cliOpts.o

# Start Spring Session and Service Declarations
sx = SpringSupport(valUser, valPassword)
taxonService = sx.getBean('taxonService')
expressionExperimentService = sx.getBean('expressionExperimentService')
bioMaterialService = sx.getBean('bioMaterialService')


print('')

print('Loading Experiments...')
experimentCol = []
for taxon in taxonCol:
	# create the taxon object to use for querrying
	taxonObj = taxonService.findByCommonName(taxon)
	# query by the taxon object
	experimentCol.extend(expressionExperimentService.findByTaxon(taxonObj))


for eeIndex, experiment in enumerate(experimentCol[0:len(experimentCol)]):
	print('\rCurrently: {0}/{1}: ID: {2}'.format(eeIndex, len(experimentCol), experiment.id), end = '')
	sys.stdout.flush()
	bmCol = bioMaterialService.findByExperiment(experiment)
