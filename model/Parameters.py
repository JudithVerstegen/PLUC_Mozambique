"""Land use change model, designed for Mozambique
Judith Verstegen, 2011-01-11

"""

def getNrTimesteps():
  """Return nr of time steps.

  e.g. 2005 to 2030 is 26 time steps."""

  timesteps = 26 
  return timesteps

def getNrSamples():
  """Return nr of Monte Carlo samples required.

  If Monte Carlo isn't required fill in 1; no statistics will be calculated."""

  samples = 2
  return samples

def getConversionUnit():
  """Return conversion unit for max yield unit to square meters.

  e.g. when max yield in ton/ha fill in 10000."""

  toMeters = 10000
  return toMeters

def getStochYield():
  """Return 1 when the yield map should have a random error, 0 otherwise.

  standardDeviationMap will be used on top of the yield fraction maps
  standardDeviationMaxYield will be used for the time series."""

  stochastic = 1
  standardDeviationMap = 0.2
  standardDeviationMaxYield = 0.1
  return [stochastic, standardDeviationMap, standardDeviationMaxYield]

def getStochPopulationDensity():
  """Return 1 when the population density map should have a random error + sd."""
  stochastic = 0
  standardDeviation = 0.1
  return [stochastic, standardDeviation]

def getStochCattleDensity():
  """Return 1 when the cattle density map should have a random error + sd."""
  stochastic = 0
  standardDeviation = 0.1
  return [stochastic, standardDeviation]

def getStochDem():
  """Return 1 when the dem should have a random error + sd."""
  stochastic = 0
  standardDeviation = 1
  return [stochastic, standardDeviation]

def getStochDistance():
  """Return 1 when the max distance should have a random error.

  When 1 the maximum distance for the suitability factors 2, 3 and 4
  varies uniformly between 1 celllength and 2 * max distance,
  e.g. with cellsize of 1 km2 and max distance 5000
  max distance varies between 1000 and 10000 m"""

  stochastic = 0
  return stochastic

def getStochWindow():
  """Return 1 when the window length in suit factor 1 should have add error."""
  stochastic = 0
  return stochastic

def getLandUseList():
  """Return list of landuse types in ORDER of 'who gets to choose first'."""
  landUseList = [1, 3, 2, 7, 4]
  return landUseList

def getFoodList():
  """Return list of land use types considered food (land not for biofuel)."""
  food = [1, 7, 3, 2, 4, 98]
  return food

def getForestNr():
  """Return class number of land use types considered forest.

  Abandoned land of this type will be called 'deforestation'
  and will grow back to forest after 10 years."""

  forest = 4
  return forest

def getRelatedTypeDict():
  """Return dictionary which type (key) is related to which others (items).

  e.g. relatedTypeDict[3] = [1, 2, 3, 7] means:
  land use type 3 is related to types 1, 2, 3 and 7.
  This is used in suitability factor 1 about neighbors
  of the same or a related type."""
  
  relatedTypeDict = {}
  relatedTypeDict[1] = [1, 2, 3]
  relatedTypeDict[2] = [1, 2, 3]
  relatedTypeDict[3] = [1, 2, 3, 7]
  relatedTypeDict[4] = [4]
  relatedTypeDict[7] = [3, 7]
  return relatedTypeDict

def getSuitFactorDict():
  """Return dictionary which type (key) has which suit factors (items).

  e.g. suitFactorDict[1] = [1, 2, 4, 5, 6, 9] means:
  land use type 1 uses suitability factors 1, 2, 4, 5, 6 and 9."""
  
  suitFactorDict = {}
  suitFactorDict[1] = [1, 2, 3, 4, 5, 6, 9]
  suitFactorDict[2] = [1, 2, 3, 4, 5, 6, 9]
  suitFactorDict[3] = [1, 2, 3, 4, 5, 6, 7, 9]
  suitFactorDict[7] = [1, 2, 3, 4, 5, 6, 7, 9]
  suitFactorDict[4] = [2, 4, 5, 6, 8]
  return suitFactorDict

def getWeightDict():
  """Return dictionary how a type (key) weights (items) its suit factors.

  e.g. weightDict[1] = [0.3, 0.1, 0.2, 0.1, 0.2, 0.1] means:
  land use type 1 has suitability factor - weight:
  1 - 0.3
  2 - 0.1
  4 - 0.2
  5 - 0.1
  6 - 0.2
  9 - 0.1

  Note that the number and order of weights has to correspond to the
  suitbility factors in the previous method."""
  
  weightDict = {}
  ## A list with weights in the same order as the suit factors above
  weightDict[1] = [0.2, 0.1, 0.1, 0.1, 0.2, 0.2, 0.1]
  weightDict[2] = [0.2, 0.1, 0.1, 0.1, 0.2, 0.2, 0.1]
  weightDict[3] = [0.2, 0.1, 0.1, 0.1, 0.15, 0.15, 0.1, 0.1]
  weightDict[7] = [0.3, 0.05, 0.15, 0.05, 0.1, 0.05, 0.2, 0.1]
  weightDict[4] = [0.25, 0.2, 0.05, 0.3, 0.2]
  return weightDict

def getVariableSuperDict():
  """Return nested dictionary for which type (key1) which factor (item1
  and key2) uses which parameters (items2; a list).

  e.g. variableDict1[2] = [-1, 10000, 1, 2] means:
  land use type 1 uses in suitability factor 2 the parameters:
  -1 for direction of the relation (decreasing)
  10000 for the maximum distance of influence
  1 for friction
  and relation type 'inversely proportional' (=2).

  An explanation of which parameters are required for which suitability
  factor is given in the manual of the model."""

  variableSuperDict = {}
  variableDict1 = {}
  variableDict1[1] = [3000]
  variableDict1[2] = [-1, 5000, 1, 2]
  variableDict1[3] = [-1, 10000, 1, 2]
  variableDict1[4] = [-1, 50000, 1, 2]
  variableDict1[5] = [1]
  variableDict1[6] = [1]
  variableDict1[9] = {2:0.8, 3:0.8, 4:0.2, 98:1, 99:1, 6:0.8, 7:0.8, 8:0.4}
  variableSuperDict[1] = variableDict1
  variableDict2 = {}
  variableDict2[1] = [3000]
  variableDict2[2] = [-1, 5000, 1, 2]
  variableDict2[3] = [-1, 10000, 1, 2]
  variableDict2[4] = [-1, 50000, 1, 2]
  variableDict2[5] = [1]
  variableDict2[6] = [1]
  variableDict2[9] = {1:0.8, 3:0.8, 4:0.2, 98:1, 99:1, 6:0.8, 7:0.6, 8:0.4}
  variableSuperDict[2] = variableDict2
  variableDict3 = {}
  variableDict3[1] = [3000]
  variableDict3[2] = [-1, 5000, 1, 2]
  variableDict3[3] = [-1, 10000, 1, 2]
  variableDict3[4] = [-1, 50000, 1, 2]
  variableDict3[5] = [1]
  variableDict3[6] = [1]
  variableDict3[7] = [1]
  variableDict3[9] = {1:0.8, 2:0.8, 4:0.2, 98:1, 99:1, 6:0.8, 7:0.8, 8:0.4}
  variableSuperDict[3] = variableDict3
  variableDict4 = {}
  variableDict4[2] = [1, 1000000, 1, 2]
  variableDict4[4] = [1, 5000000, 1, 2]
  variableDict4[5] = [1]
  variableDict4[6] = [-1]
  variableSuperDict[4] = variableDict4
  variableDict7 = {}
  variableDict7[1] = [3000]
  variableDict7[2] = [-1, 5000, 1, 2]
  variableDict7[3] = [-1, 10000, 1, 2]
  variableDict7[4] = [-1, 50000, 1, 2]
  variableDict7[5] = [1]
  variableDict7[6] = [1]
  variableDict7[7] = [1]
  variableDict7[9] = {1:0.8, 2:0.8, 3:0.8, 4:0.2, 98:1, 99:1, 6:0.8}
  variableSuperDict[7] = variableDict7
  return variableSuperDict

def getNoGoLanduseTypes():
  """Return a list of land use type numbers that cannot be changed

  At the moment this only works for static land uses
  The noGo map is calculated once at the beginning of the run."""

  noGoLanduse = [9, 10]
  return noGoLanduse

def getPrivateNoGoSlopeDict():
  """Return dictionary of a type's (key) slope contrains (items; mapname).

  e.g. privateNoGoDict[1] = 0.16 means:
  land use type 1 can not allocate on locations that are have a slope
  of more than 16%."""
  
  privateNoGoDict = {}
  privateNoGoDict[1] = 0.16
  privateNoGoDict[3] = 0.16
  return privateNoGoDict
