'''
# BioMaterial Metadata Script:
# Generates Metadata for BioMaterials (Samples)
# Taxa Limited to Human and Mouse
# Revision: 24 May 2017
# Ogan Revision: 7 June 2017
'''
# ------------------------------ INITIALIZATION ------------------------------
# Module Imports
from __future__ import print_function
import argparse
import os
import sys
import re
# from MetaBiomHelpers import *
from ElapseTime import ElapseTime # non essential in Nat's directory
from SpringSupport import SpringSupport
from PrettyPrint import * # in Nat's directory
from ubic.gemma.core.datastructure.matrix import ExpressionDataWriterUtils
from ubic.gemma.model.genome.gene.phenotype.valueObject import CharacteristicValueObject

execfile('/home/omancarci/git repos/natScripts/MetaBiomHelpers.py')

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
globalTimer = ElapseTime()

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
edwUtils = ExpressionDataWriterUtils() # not sure what this is. General utilities I guess

print('')

# ------------------------------ MAIN ------------------------------

# File Operations
tempPath = outputFile + "_backup"
if os.path.lexists(tempPath):
	print('DELETE: Old Metadata backup')
	os.remove(tempPath)

tempPath = outputFile
renamePath = outputFile + '_backup'
if os.path.lexists(tempPath):
	print('BACKUP: Old Metadata')
	os.rename(tempPath, renamePath)


# generate the header for the output file
outFile = open(tempPath, mode = 'wt')
# write column names that'll be used
outFile.write('\t'.join(['bmID',
						 'bmName',
						 'bmGSM',
						 'baseline', 
						 'factorType',
						 'factorCategories',
						 'factorCategoryUri',
						 'factorCategoryUriFull',
						 'factorUri',
						 'factorUriFull',
						 'factorCharacteristic',
						 'factorDescription',
						 'broadCategory',
						 'broadCategoryDescription', # sample info till here
						 'eeID', 
						 'eeName', 
						 'taxon',
						 'eeCategory',
						 'eeCategoryUri',
						 'eeCategoryUriFull',
						 'eeAnnot',
						 'eeUri',
						 'eeUriFull',
						 'technologyType',
						 'platformName',]) # experiment data till here
						+ '\n')
outFile.flush()

# get the experiments relevant to you filtered by taxon
print('Loading Experiments...')
experimentCol = []
for taxon in taxonCol:
	# create the taxon object to use for querrying
	taxonObj = taxonService.findByCommonName(taxon)
	# query by the taxon object
	experimentCol.extend(expressionExperimentService.findByTaxon(taxonObj))


# experiment = experimentCol[672]
# eeIndex = 672
startFrom = 0
# experiment = experimentCol[240]
# loop over experiments
for eeIndex, experiment in enumerate(experimentCol[startFrom:len(experimentCol)]):
	print('\rCurrently: {0}/{1}: ID: {2}'.format(eeIndex+startFrom, len(experimentCol), experiment.id), end = '')
	sys.stdout.flush()
	
	# loadValueObject returns a ExpressionExperimentValueObject
	eevo = expressionExperimentService.loadValueObject(experiment.id)
	

	# Sanity Check
	if eevo.troubled:
		continue
	
	arrayData = expressionExperimentService.getArrayDesignsUsed(experiment).toArray()
	technoTypes = map(lambda x: x.getTechnologyType(), arrayData)
	technoTypes = PPStripUnicode("|".join(map(lambda x: x.getValue(),technoTypes)))
	platformName = PPStripUnicode("|".join(map(lambda x: x.getShortName(), arrayData)))
	
	
	
	# here lies the annotation data for the experiment
	eeAnnot = expressionExperimentService.getAnnotations(experiment.id)
	
	eeAnnotCategory = PrettyPrint(map(lambda x: x.getClassName(),eeAnnot))
	eeAnnotCategoryUri = PrettyPrint(map(lambda x: x.getClassUri(),eeAnnot))
	eeAnnotCategoryBriefUri = map(lambda x: BriefUri(x),eeAnnotCategoryUri)
	
	eeAnnotCategory = '|'.join(eeAnnotCategory)
	eeAnnotCategoryUri = '|'.join(eeAnnotCategoryUri)
	eeAnnotCategoryBriefUri = '|'.join(eeAnnotCategoryBriefUri)
	
	experimentAnnotations = PrettyPrint(map(lambda x: x.termName,eeAnnot))
	experimentAnnotURI =  PrettyPrint(map(lambda x: x.termUri,eeAnnot))
	briefURI = map(lambda x: BriefUri(x),experimentAnnotURI)
	
	# merge annotation fields
	experimentAnnotations = '|'.join(experimentAnnotations)
	experimentAnnotURI = '|'.join(experimentAnnotURI)
	briefURI = '|'.join(briefURI)
	
	# this is general information about the experiment
	eeCol = [eevo.id,
			 eevo.shortName,
			 eevo.taxon,
			 eeAnnotCategory,
			 eeAnnotCategoryBriefUri,
			 eeAnnotCategoryUri,
			 experimentAnnotations,
			 briefURI,
			 experimentAnnotURI,
			 technoTypes,
			 platformName]
	
	# here we loop over individual bio materials
	bmCol = bioMaterialService.findByExperiment(experiment)
	# bm = bmCol[3]
	for i, bm in enumerate(bmCol):
		# print(i,end='')
		# print(i)
		fvCol = bm.factorValues
		
		factorDescriptions = "|".join(map(lambda x:PPStripUnicode(x.getDescriptiveString()),fvCol))
		broadCategory = "|".join(map(lambda x: PPStripUnicode(x.getExperimentalFactor().getName()), fvCol))
		broadCategoryDescription = "|".join(map(lambda x: PPStripUnicode(x.getExperimentalFactor().getDescription()), fvCol))
		
		
		
		# characteristics = map(lambda x:x.characteristics,fvCol)
		
		factorData = map(lambda x: FVResolve(x),fvCol)
		
		
		factorCategories = "|".join(map(lambda x: x['category'],factorData))
		factorCategoryUri =  "|".join(map(lambda x: x['categoryUri'],factorData))
		briefCategoryUri = "|".join(map(lambda x: x['briefCategoryUri'],factorData))
		
		factorCharacteristic = "|".join(map(lambda x: x['factorValue'],factorData))
		factorCharacteristicUri =  "|".join(map(lambda x: x['factorUri'],factorData))
		briefCharacteristicUri =  "|".join(map(lambda x: x['briefFactorUri'],factorData))
		
		# fvCol = filter(lambda x: x.getExperimentalFactor() != None, fvCol)
		
		# not sure if this variable works properly. add it to the end and see how it goes
		baseline = '|'.join(map(lambda x:str(x.getIsBaseline()), fvCol))
		
		factorType = '|'.join(map(lambda x:PPStripUnicode(x.getExperimentalFactor().getType().toString()), fvCol))	
			
		baCol = bm.bioAssaysUsedIn
		baAccession = filter(lambda x: x.accession != None, baCol)
		if len(baAccession) == 0:
			baAccession = 'NA'
		else:
			baAccession = '|'.join(map(lambda x: PPStripUnicode(x.accession.accession), baCol))
		
		tempCol = [bm.id,
				   edwUtils.constructBioAssayName(bm, baCol), 
				   baAccession,
				   baseline,
				   factorType,
				   factorCategories,
				   briefCategoryUri,
				   factorCategoryUri,
				   briefCharacteristicUri,
				   factorCharacteristicUri,
				   factorCharacteristic,
				   factorDescriptions,
				   broadCategory,
				   broadCategoryDescription]
		
		tempCol.extend(eeCol)
		
		# remove all tabs that may sneak into the columns
		tempCol = map(lambda x: PPStripUnicode(x).replace('\t',''), tempCol)
		
		outFile.write('\t'.join(PrettyPrint(tempCol)) + '\n')
		outFile.flush()
		
	
	
	# print('\r', ' ' * 50, '\r', end = '')

outFile.close()

# ------------------------------ FINALIZATION ------------------------------
# Time Reporter
globalTimer.getElapse()

# End Spring Session
sx.shutdown()
