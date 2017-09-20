# ------------------------------ INITIALIZATION ------------------------------
# Module Imports
from __future__ import print_function
import argparse
import os
import sys
import re
import requests # requests package used is 2.5.3. see https://stackoverflow.com/a/29154908/3273060 for explanation
# from MetaBiomHelpers import *
from ElapseTime import ElapseTime # non essential in Nat's directory
from SpringSupport import SpringSupport
from PrettyPrint import * # in Nat's directory
from ubic.gemma.core.datastructure.matrix import ExpressionDataWriterUtils
from ubic.gemma.model.genome.gene.phenotype.valueObject import CharacteristicValueObject

helperURL = "https://raw.githubusercontent.com/oganm/gemmaScripts/master/MetaBiomHelpers.py" # run helpers from URL
exec(requests.get(helperURL).content)
# execfile('/home/omancarci/git repos/gemmaScripts/MetaBiomHelpers.py')

# CLI Generation and Parsing
cliParser = argparse.ArgumentParser()
cliParser.add_argument('-u', required = False, default = None, help = 'Gemma username')
cliParser.add_argument('-p', required = False, default = None, help = 'Gemma password')

cliOpts = cliParser.parse_args()

# Declaring Global Flags and Paths
valUser = None
valPassword = None
taxonCol = ['human', 'mouse']
globalTimer = ElapseTime()

if (cliOpts.u != None and cliOpts.p != None):
	valUser = cliOpts.u
	valPassword = cliOpts.p


# Start Spring Session and Service Declarations
sx = SpringSupport(valUser, valPassword)
taxonService = sx.getBean('taxonService')
expressionExperimentService = sx.getBean('expressionExperimentService')
bioMaterialService = sx.getBean('bioMaterialService')
edwUtils = ExpressionDataWriterUtils() # not sure what this is. General utilities I guess

print('')

# ------------------------------ MAIN ------------------------------

# get the experiments relevant to you filtered by taxon
print('Loading Experiments...')
experimentCol = []
for taxon in taxonCol:
	# create the taxon object to use for querrying
	taxonObj = taxonService.findByCommonName(taxon)
	# query by the taxon object
	experimentCol.extend(expressionExperimentService.findByTaxon(taxonObj))


# experiment = experimentCol[2824]
# eeIndex = 672
startFrom = 0


outFile = open('DEBUGFILE', mode = 'wt')

experimentCol
startFrom = 0

for eeIndex, experiment in enumerate(experimentCol[startFrom:len(experimentCol)]):
	'\rCurrently: {0}/{1}: ID: {2} GSE: {3}'.format(eeIndex+startFrom, len(experimentCol), experiment.id,experiment.getShortName()) + '\n'
	outFile.write('{0}/{1}: ID: {2} GSE: {3}'.format(eeIndex+startFrom, len(experimentCol), experiment.id,experiment.getShortName()) + '\n')
	outFile.flush()
	
outFile.close()
