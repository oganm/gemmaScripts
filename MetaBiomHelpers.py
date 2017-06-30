import re

def StripUnicode(obj):
	if obj == None:
		return 'None'
	if isinstance(obj, unicode):
		return obj.encode('ascii', 'ignore')
	else:
		return str(obj)

# this function simplifies the full URL style ontology terms
# translated from Nat's groovy script
def BriefUri(uri):
	if (uri == None or uri == '' or uri == "None"):
		return 'None'
	if(uri =='null'):
		return 'null'
	
	tmpHash = uri.rfind('#')
	tmpSlash = uri.rfind('/')
	geneFlag = 'ncbi_gene' in uri
	if (tmpHash != -1):
		tmpString = uri[(tmpHash+1):len(uri)]
	elif (tmpSlash != -1):
		tmpString = uri[(tmpSlash+1):len(uri)]
	
	if (geneFlag):
		return 'GENE_' + tmpString
	else:
		return tmpString


# a vectorized version to make code shorter
def BriefUriVector(uriVector):
	return map(lambda x: BriefUri(x), uriVector)

def cleanAnnot(dirtyStr):
	if (dirtyStr == None):
		return 'None'
	
	tempString = re.sub(r'\t','',dirtyStr).strip()
	if (tempString == ''):
		return 'NA'
	return tempString


def FVResolve(fv):
	if (fv == None):
		return 'NA'
	
	charCol = fv.characteristics
	charCol = filter(lambda x: x != None, charCol)
    
	if (charCol != None and len(charCol) > 0):
		charCol = map(lambda x: CharacteristicValueObject(x),charCol)
		
		category = map(lambda x: StripUnicode(x.getCategory()),charCol)
		categoryUri = map(lambda x: StripUnicode(x.getCategoryUri()),charCol)
		briefCategoryUri = BriefUriVector(categoryUri)
		
		factorValue = map(lambda x: StripUnicode(x.getValue()),charCol)
		factorUri = map(lambda x: StripUnicode(x.getValueUri()),charCol)
		briefFactorUri = BriefUriVector(factorUri)
		
		def escapeSemiCol(aList):
			return map(lambda x:re.sub(';','_',x), aList)
		
		category = ';'.join(escapeSemiCol(category))
		categoryUri = ';'.join(escapeSemiCol(categoryUri))
		briefCategoryUri = ';'.join(escapeSemiCol(briefCategoryUri))
		factorValue = ';'.join(escapeSemiCol(factorValue))
		factorUri = ';'.join(escapeSemiCol(factorUri))
		briefFactorUri = ';'.join(escapeSemiCol(briefFactorUri))
		
		return {'category':category,
				'categoryUri':categoryUri,
				'briefCategoryUri':briefCategoryUri,
				'factorValue':factorValue,
				'factorUri':factorUri,
				'briefFactorUri':briefFactorUri}
	elif (fv.experimentalFactor != None):
		category = fv.experimentalFactor.getCategory()
		return {'category':category.getValue(),
				'categoryUri':category.getValueUri(),
				'briefCategoryUri':BriefUri(category.getValueUri()),
				'factorValue':cleanAnnot(fv.getValue()),
				'factorUri':'None',
				'briefFactorUri':'None'}
	elif (fv.measurement != None):
		return {'category':'None',
				'categoryUri':'None',
				'briefCategoryUri':'None',
				'factorValue':cleanAnnot(fv.measurement.value),
				'factorUri':'None',
				'briefFactorUri':'None'}
	elif (fv.value != None and fv.value ==""):
		return {'category':'None',
				'categoryUri':'None',
				'briefCategoryUri':'None',
				'factorValue':'None',
				'factorUri':'None',
				'briefFactorUri':'None'}

