"""Land use change model of Mozambique
Judith Verstegen, 2011-01-27

"""

from pcraster import *
from pcraster.framework import *
import Parameters

#######################################

class LandUseType:
  def __init__(self, typeNr, environment, relatedTypeList, suitFactorList, \
               weightList, variableDict, noise, nullMask, yieldFrac, \
               forestYieldFrac, windowLengthRealization):
    """Create LandUseType object that represents a class on the land use map.

    Takes ten arguments:
    typeNr -- class nr of the land use type on the land use map
    environment -- global land use map that will evolve
    relatedTypeList -- list with land use type next to which growth is preferred
    suitFactorList -- list of suitability factors the type takes into account
    weightList -- list of relative weights for those factors
    variableDict -- dictionary in which inputs for factors are found
    noise -- very small random noise to ensure cells can't get same suitability
    nullMask -- map with value 0 for study area and No Data outside
    yieldFrac -- fraction of maximum yield a cell can deliver
    forestYieldFrac -- fraction of maximum forest biomass a cell can deliver
    
    """
    
    self.typeNr = typeNr
    self.environment = environment
    self.relatedTypeList = relatedTypeList
    self.suitFactorList = suitFactorList
    self.weightList = weightList
    self.variableDict = variableDict
    self.nullMask = nullMask

    self.noise = noise
    self.toMeters = Parameters.getConversionUnit()
    self.stochDistance = Parameters.getStochDistance()
    self.stochWindow = Parameters.getStochWindow()
    self.windowLengthRealization = windowLengthRealization
    if self.typeNr == Parameters.getForestNr():
      self.forest = True
      self.yieldFrac = forestYieldFrac
    else:
      self.forest = False
      self.yieldFrac = yieldFrac

  def setEnvironment(self, environment):
    """Update the environment (land use map)."""
    self.environment = environment

  def createInitialMask(self, globalMapNoGo, privateMapsNoGo):
    """Combine the global no-go map with areas unsuitable for this land use."""
    self.mask = globalMapNoGo
    if privateMapsNoGo is not None:
      self.mask = pcror(self.mask, privateMapsNoGo)
##        report(self.mask, 'privMask')

  def normalizeMap(self, aMap):
    """Return a normalized version of the input map."""
    mapMax = mapmaximum(aMap)
    mapMin = mapminimum(aMap)
    diff = float(mapMax - mapMin)
    if diff < 0.000001:
      normalizedMap = (aMap - mapMin) / 0.000001
    else:
      normalizedMap = (aMap - mapMin) / diff
    return normalizedMap
  
  ## 1
  def getNeighborSuitability(self):
    """Return suitability map based on nr of neighors with a related type."""
    booleanSelf = pcreq(self.environment, self.typeNr)
    for aType in self.relatedTypeList:
      booleanMap = pcreq(self.environment, aType)
      booleanSelf = pcror(booleanSelf, booleanMap)
    scalarSelf = scalar(booleanSelf)
    ## Count nr of neighbors with 'true' in a window with length from parameters
    ## and assign this value to the centre cell
    variableList = self.variableDict.get(1)
    windowLength = variableList[0]
    if self.stochWindow == 1:
      windowLength += (celllength()/3) * self.windowLengthRealization
##      print('windowLength is', float(windowLength))
    nrNeighborsSameLU = windowtotal(scalarSelf, windowLength) - scalarSelf
    ## The nr of neighbors are turned into suitability values between 0 and 1
    maxNr = ((windowLength / celllength())**2) - 1
    neighborSuitability = nrNeighborsSameLU / maxNr
##    report(neighborSuitability, 'neighborSuitability')
    return neighborSuitability

  ## 2
  def getDistanceRoadSuitability(self, spreadMapRoads):
    """Return suitability map based on distance to roads."""
    variableList = self.variableDict.get(2)
    direction = variableList[0]
    maxDist = variableList[1]
    if self.stochDistance == 1:
      maxDist = 2*celllength() + mapuniform() * (2*maxDist - 2*celllength())
      print('max dist roads is', int(maxDist))
    friction = variableList[2]
    relationType = variableList[3]

    ## Influence up to some maximum distance
    cutOffMap = ifthen(spreadMapRoads < maxDist, spreadMapRoads * direction)
    normalizedMap = self.normalizeMap(cutOffMap)
    ## Implement linear (0), exponential (1) or inv. proportional (2) relation
    if relationType == 0:
      relationMap = normalizedMap
    elif relationType == 1:
      exponentialMap = exp(direction * normalizedMap)
      relationMap = self.normalizeMap(exponentialMap)
    elif relationType == 2:
      invPropMap = (-1) / (normalizedMap + 0.1)
      relationMap = self.normalizeMap(invPropMap)
      
    roadSuitability = cover(relationMap, self.nullMask)
##    report(roadSuitability, 'roadSuit' + str(self.typeNr))
    return roadSuitability

  ## 3
  def getDistanceWaterSuitability(self, spreadMapWater):
    """Return suitability map based on distance to water."""
    variableList = self.variableDict.get(3)
    direction = variableList[0]
    maxDist = variableList[1]
    if self.stochDistance == 1:
      maxDist = 2*celllength() + mapuniform() * (2*maxDist - 2*celllength())
      print('max dist water is', int(maxDist))
    friction = variableList[2]
    relationType = variableList[3]

    ## Influence up to some maximum distance
    cutOffMap = ifthen(spreadMapWater < maxDist, spreadMapWater * direction)
    normalizedMap = self.normalizeMap(cutOffMap)
    ## Implement linear (0), exponential (1) or inv. proportional (2) relation
    if relationType == 0:
      relationMap = normalizedMap
    elif relationType == 1:
      exponentialMap = exp(direction * normalizedMap)
      relationMap = self.normalizeMap(exponentialMap)
    elif relationType == 2:
      invPropMap = (-1) / (normalizedMap + 0.1)
      relationMap = self.normalizeMap(invPropMap)
      
    waterSuitability = cover(relationMap, self.nullMask)
##    report(waterSuitability, 'waterSuit' + str(self.typeNr))
    return waterSuitability

  ## 4
  def getDistanceCitySuitability(self, spreadMapCities):
    """Return suitability map based on distance to large cities."""
    variableList = self.variableDict.get(4)
    direction = variableList[0]
    maxDist = variableList[1]
    if self.stochDistance == 1:
      maxDist = 2*celllength() + mapuniform() * (2*maxDist - 2*celllength())
      print('max dist cities is', int(maxDist))
    friction = variableList[2]
    relationType = variableList[3]

    ## Influence up to some maximum distance
    cutOffMap = ifthen(spreadMapCities < maxDist, spreadMapCities * direction)
    normalizedMap = self.normalizeMap(cutOffMap)
    ## Implement linear (0), exponential (1) or inv. proportional (2) relation
    if relationType == 0:
      relationMap = normalizedMap
    elif relationType == 1:
      exponentialMap = exp(direction * normalizedMap)
      relationMap = self.normalizeMap(exponentialMap)
    elif relationType == 2:
      invPropMap = (-1) / (normalizedMap + 0.1)
      relationMap = self.normalizeMap(invPropMap)
      
    citySuitability = cover(relationMap, self.nullMask)
##    report(citySuitability, 'citySuit' + str(self.typeNr))
    return citySuitability

  ## 5
  def getYieldSuitability(self):
    """Return suitability map based on yield for crops or cattle."""
##    self.yieldFrac = self.normalizeMap(yieldFrac)
    variableList = self.variableDict.get(5)
    friction = variableList[0]
    yieldRelation = exp(friction * self.yieldFrac)
    yieldSuitability = self.normalizeMap(yieldRelation)
##    report(yieldSuitability, 'yieldSuit')
    return yieldSuitability

  ## 6
  def getPopulationSuitability(self, populationDensityMap):
    """Return suitability map based on population density."""
    variableList = self.variableDict.get(6)
    direction = variableList[0]
    populationSuitability = direction * populationDensityMap
    populationSuitability = self.normalizeMap(populationSuitability)
##    report(populationSuitability, 'popSuit' + str(self.typeNr))
    return populationSuitability

  ## 7
  def getCattleSuitability(self, cattleDensityMap):
    """Return suitability map based on cattle density."""
    variableList = self.variableDict.get(7)
    direction = variableList[0]
    cattleSuitability = direction * cattleDensityMap
    cattleSuitability = self.normalizeMap(cattleDensityMap)
    return cattleSuitability

  ## 8
  def getEdgeSuitability(self):
    """Return suitability map based on distance to a forest edge."""
    notSelf = pcrne(self.environment, self.typeNr)
    ## Relation always inversely prop, so initial dist 1 to prevent div 0
    distEdge = spread(notSelf, 1, 1)
    edgeSuitability = self.normalizeMap(-1/distEdge)
##    report(edgeSuitability, 'edgeSuit')
    return edgeSuitability

  ## 9
  def getCurrentLandUseSuitability(self):
    """Return suitability map based on current land use type."""
    variableDict = self.variableDict.get(9) 
    current = self.nullMask
    for aKey in variableDict.keys():
      current = ifthenelse(pcreq(self.environment, aKey), \
                           variableDict.get(aKey), current)
    currentLandUseSuitbaility = self.normalizeMap(current)
    return currentLandUseSuitbaility
  
  def createInitialSuitabilityMap(self, distRoads, distWater, distCities, \
                                  densPopulation, densCattle):
    """Return the initial suitability map, i.e. for static factors.

    Given six maps:
    distRoads -- distances to roads
    distWater -- distances to open water
    distCities -- distances to cities
    yieldFrac -- fraction of maximum yield that can be reached in a cell
    densPopulation -- population density (people per cell)
    densCattle -- cattle density (animals per cell)
    
    Uses a lists and two dictionaries created at construction of the object:
    factors -- the names (nrs) of the suitability factors (methods) needed
    parameters -- the input parameters for those factors
    weights -- the weights that belong to those factors (how they're combined).

    """

    self.weightInitialSuitabilityMap = 0
    self.initialSuitabilityMap = spatial(scalar(0))
    i = 0
    ## For every number in the suitability factor list
    ## that belongs to a STATIC factor
    ## the corresponding function is called providing the necessary parameters
    ## and the partial suitability map is added to the total
    ## taking into account its relative importance (weight)
    for aFactor in self.suitFactorList:
      if aFactor == 2:
        self.initialSuitabilityMap += self.weightList[i] * \
                                 self.getDistanceRoadSuitability(distRoads)
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor == 3:
        self.initialSuitabilityMap += self.weightList[i] * \
                                 self.getDistanceWaterSuitability(distWater)
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor == 4:
        self.initialSuitabilityMap += self.weightList[i] * \
                                 self.getDistanceCitySuitability(distCities)
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor == 5:
        self.initialSuitabilityMap += self.weightList[i] * \
                                      self.getYieldSuitability()
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor == 6:
        self.initialSuitabilityMap += self.weightList[i] * \
                                 self.getPopulationSuitability(densPopulation)
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor == 7:
        self.initialSuitabilityMap += self.weightList[i] * \
                                 self.getCattleSuitability(densCattle)
        self.weightInitialSuitabilityMap += self.weightList[i]
      elif aFactor in (1, 8, 9):
        ## Dynamic factors are captured in the total suitability map
        pass
      else:
        print('ERROR: unknown suitability factor for landuse', self.typeNr)
      i += 1
    print('weight of initial factors of', self.typeNr, \
          'is', self.weightInitialSuitabilityMap)
    self.initialSuitabilityMap += self.noise
##    report(self.initialSuitabilityMap, 'iniSuit' + str(self.typeNr))

  def getTotalSuitabilityMap(self):
    """Return the total suitability map for the land use type.

    Uses a lists and two dictionaries:
    factors -- the names (nrs) of the suitability factors (methods) needed
    parameters -- the input parameters for those factors
    weights -- the weights that belong to those factors (how they're combined).

    """

    suitabilityMap = spatial(scalar(0))
    i = 0
    ## For every number in the suitability factor list
    ## that belongs to a DYNAMIC factor
    ## the corresponding function is called providing the necessary parameters
    ## and the partial suitability map is added to the total
    ## taking into account its relative importance (weight)
    for aFactor in self.suitFactorList:
      if aFactor == 1:
        suitabilityMap += self.weightList[i] * self.getNeighborSuitability()
      elif aFactor == 8:
        suitabilityMap += self.weightList[i] * self.getEdgeSuitability()
      elif aFactor == 9:
        suitabilityMap += self.weightList[i] * \
                          self.getCurrentLandUseSuitability()
      elif aFactor in (2, 3, 4, 5, 6, 7):
        ## Static factors already captured in the initial suitability map
        pass
      else:
        print('ERROR: unknown suitability factor for landuse', self.typeNr)
      i += 1
    suitabilityMap += self.weightInitialSuitabilityMap * \
                      self.initialSuitabilityMap
    self.totalSuitabilityMap = ifthen(pcrnot(self.mask), suitabilityMap)
    self.totalSuitabilityMap = self.normalizeMap(self.totalSuitabilityMap)
    return self.totalSuitabilityMap

  def setMaxYield(self, maxYield):
    """Set the maximum yield in this time step using the input from the tss."""
    convertedMaxYield = (maxYield / self.toMeters) * cellarea()
    ownMaxYield = ifthen(self.environment == self.typeNr, convertedMaxYield)
    ## maximum yield PER CELL
    self.maxYield = float(mapmaximum(ownMaxYield))
    self.yieldMap = self.yieldFrac * self.maxYield
    
  def updateYield(self, env):
    """Calculate total yield generated by cells occupied by this land use."""
    ## Current cells taken by this land use type
    self.currentYield = ifthen(env == self.typeNr, self.yieldMap)
##    report(self.currentYield, 'currentYield' + str(self.typeNr))
    self.totalYield = float(maptotal(self.currentYield))

  def allocate(self, demand, tempEnvironment, immutables):
    """ Assess total yield, compare with demand and add or remove difference."""
    self.setEnvironment(tempEnvironment)
    self.updateYield(tempEnvironment)
    ownDemand = ifthen(self.environment == self.typeNr, demand)
    self.demand = float(mapmaximum(ownDemand))
    print('\nland use type', self.typeNr)
    print('demand is:', self.demand)
    if self.forest:
      print('forest,', self.typeNr,'so remove')
      self.removeForest()
    else:
      print('total yield is:', self.totalYield)
      if self.totalYield > self.demand:
        print('remove')
        self.remove()
      elif self.totalYield < self.demand:
        print('add')
        self.add(immutables)
      else:
        print('do nothing')
    newImmutables = ifthenelse(self.environment == self.typeNr, boolean(1),\
                               immutables)
    return self.environment, newImmutables
    
  def add(self, immutables):
    """Add cells of this land use type until demand is fullfilled."""
    ## Remove cells from immutables (already changed)
    self.totalSuitabilityMap = ifthen(pcrnot(immutables), \
                                      self.totalSuitabilityMap)
    ## Remove cells already occupied by this land use
    self.totalSuitabilityMap = ifthen(self.environment != self.typeNr, \
                                      self.totalSuitabilityMap)
    ## Determine maximum suitability and allocate new cells there
    mapMax = mapmaximum(self.totalSuitabilityMap)
    print('start mapMax =', float(mapMax))
    ordered = order(self.totalSuitabilityMap)
    maxIndex = int(mapmaximum(ordered))
    diff = float(self.demand - self.totalYield)
    x = int(maxIndex - diff / self.maxYield)
    xPrev = maxIndex
    i = 0
    tempEnv = self.environment
    while diff > 0 and xPrev > x:
      print('cells to add', int(maxIndex - x))
      if x < 0:
        print('No space left for land use', self.typeNr)
        break
      else:
        ## The key: cells with maximum suitability are turned into THIS type
        tempEnvironment = ifthen(ordered > x, nominal(self.typeNr))
        tempEnv = cover(tempEnvironment, self.environment)

        ## Check the yield of the land use type now that more land is occupied
        self.updateYield(tempEnv)
        i += 1
        xPrev = x
        ## Number of cells to be allocated
        diff = float(self.demand - self.totalYield)
        x -= int(diff / self.maxYield)
    self.setEnvironment(tempEnv)
    print('iterations', i, 'end yield is', self.totalYield)


  def remove(self):
    """Remove cells of this land use type until demand is fullfilled."""
    ## Only cells already occupied by this land use can be removed
    self.totalSuitabilityMap = ifthen(self.environment == self.typeNr, \
                                      self.totalSuitabilityMap)
    ordered = order(self.totalSuitabilityMap)
    mapMin = mapminimum(self.totalSuitabilityMap)
    print('start mapMin =', float(mapMin))
    diff = float(self.totalYield - self.demand)
    x = int(diff / (self.maxYield * 0.8))
    xPrev = 0
    i = 0
    tempEnv = self.environment
    while diff > 0 and xPrev < x and i < 100:
      print('cells to remove', x)
      ## The key: cells with minimum suitability are turned into 'abandoned'
      tempEnvironment = ifthen(ordered < x, nominal(99))
      tempEnv = cover(tempEnvironment, self.environment)
      
      ## Check the yield of the land use type now that less land is occupied
      self.updateYield(tempEnv)
      i += 1
      xPrev = x
      diff = float(self.totalYield - self.demand)
      if math.fmod(i, 40) == 0:
        print('NOT getting there...')
        ## Number of cells to be allocated
        x = 2 * (x + int(diff / self.maxYield))      
      else:
        ## Number of cells to be allocated
        x += int(diff / self.maxYield)
    self.setEnvironment(tempEnv)
    print('iterations', i, 'end yield is', self.totalYield)
##    report(self.environment, 'newEnv' + str(self.typeNr))

  def removeForest(self):
    """Remove area of forest indicated in time series."""
    if self.demand < 0.01:
      print('nothing to remove')
    else:
      ## Only cells already occupied by this land use can be removed
      self.totalSuitabilityMap = ifthen(self.environment == self.typeNr, \
                                        self.totalSuitabilityMap)
      ordered = order(self.totalSuitabilityMap)
      mapMin = mapminimum(self.totalSuitabilityMap)
      removedBiomass = self.nullMask
      diff = 1
      tempEnv = self.environment
      print('start mapMin =', float(mapMin))
      x = int(self.demand / self.maxYield * 0.8)
      xPrev = 0
      i = 0
      while diff > 0 and xPrev < x and i < 100:
        print('cells to remove', x)
        ## The key: cells with minimum suitability are turned into 'abandoned'
        tempEnvironment = ifthen(ordered < x, nominal(98))
        tempEnv = cover(tempEnvironment, self.environment)
        removed = ifthen(tempEnvironment == 98, nominal(self.typeNr))
        ## Check the yield of the land use type now that less land is occupied
        self.updateYield(removed)
        i += 1
        xPrev = x
        diff = float(self.demand - self.totalYield)
        if math.fmod(i, 40) == 0:
          print('NOT getting there...')
          ## Number of cells to be allocated
          x = 2 * (x + int(diff / self.maxYield))      
        else:
          ## Number of cells to be allocated
          x += int(diff / self.maxYield)
      self.setEnvironment(tempEnv)
      print('iterations', i, 'removed biomass is', self.totalYield)

#######################################

class LandUse:
  def __init__(self, types, environment, nullMask):
    """Construct a land use object with a nr of types and an environment."""
    self.types = types
    self.nrOfTypes = len(types)
    print('\nnr of dynamic land use types is:', self.nrOfTypes)
    self.environment = environment
    ## List with the land use type OBJECTS
    self.landUseTypes = []
    ## Map with 0 in study area and No Data outside, used for cover() functions
    self.nullMask = nullMask
    self.toMeters = Parameters.getConversionUnit()
    self.yearsDeforestated = nullMask
    self.forest = Parameters.getForestNr()

  def setEnvironment(self, environment):
    """Update environment of the 'overall' class and separate land use types."""
    self.environment = environment
    for aType in self.landUseTypes:
      aType.setEnvironment(self.environment)

  def addRandomNoise(self, yieldFrac, forestYieldFrac, scYieldFrac, \
                     populationDensity, cattleDensity, dem, stochYield, \
                     stochPopulation, stochCattle, stochDem):
    """Add some random noise to maps as indicated in Parameters.py."""
    self.yieldFrac = yieldFrac
    self.forestYieldFrac = forestYieldFrac
    self.scYieldFrac = scYieldFrac
    self.populationDensity = populationDensity
    self.cattleDensity = cattleDensity
    self.dem = dem
    ## Add random noise when required by corresponding method in Parameters.py
    if stochYield[0] == 1:
      self.yieldFrac += stochYield[1] * normal(1) * self.yieldFrac
      self.forestYieldFrac += stochYield[1] * normal(1) * self.forestYieldFrac
      self.scYieldFrac += stochYield[1] * normal(1) * self.scYieldFrac
##      self.yieldFrac = self.yieldFrac / mapmaximum(self.yieldFrac)
      self.yieldFrac = max(self.yieldFrac, 0)
      self.yieldFrac = min(self.yieldFrac, 1)
      self.forestYieldFrac = max(self.forestYieldFrac, 0)
      self.forestYieldFrac = min(self.forestYieldFrac, 1)
      self.scYieldFrac = max(self.scYieldFrac, 0)
      self.scYieldFrac = min(self.scYieldFrac, 1)
    if stochPopulation[0] == 1:
      self.populationDensity += stochPopulation[1] * normal(1) * \
                                self.populationDensity
      self.populationDensity = max(self.populationDensity, 0)
    if stochCattle[0] == 1:
      self.cattleDensity += stochCattle[1] * normal(1) * self.cattleDensity
      self.cattleDensity = max(self.cattleDensity, 0)
    if stochDem[0] == 1:
      self.dem += stochDem[1] * normal(1)
    self.euYieldFrac = self.yieldFrac
    
  def createLandUseTypeObjects(self, relatedTypeDict, suitabilityDict, \
                               weightDict, variableSuperDict, noise):
    """Generate an object for every dynamic land use type.

    Make objects with:
    typeNr -- class nr in land use map
    environment -- global land use map
    relatedTypes -- list with land use types next to which growth is preferred
    suitFactors -- list with nrs of the needed suitability factors
    weights -- list with relative weights for those factors
    variables -- dictionary with inputs for those factors
    noise -- small random noise that determines order when same suitability

    """
    windowLengthRealization = float(mapnormal())
    
    for aType in self.types:
      ## Get the list that states witch types the current types relates to
      relatedTypeList = relatedTypeDict.get(aType)
      ## Get the right list of suitability factors out of the dictionary
      suitabilityList = suitabilityDict.get(aType)
      ## Get the weights and variables out of the weight dictionary
      weightList = weightDict.get(aType)
      variableDict = variableSuperDict.get(aType)
      ## Parameter list is notincluded yet
      self.landUseTypes.append(LandUseType(aType, self.environment, \
                                           relatedTypeList, suitabilityList, \
                                           weightList, variableDict, noise, \
                                           self.nullMask, self.yieldFrac,\
                                           self.forestYieldFrac, \
                                           windowLengthRealization))
      
  def determineNoGoAreas(self, noGoMap, noGoLanduseList, privateNoGoSlopeDict):
    """Create global no-go map, pass it to the types that add own no-go areas."""
    self.slopeMap = slope(self.dem)
    self.excluded = noGoMap
    privateNoGoAreas = None
    ## Check the list with immutable land uses
    if noGoLanduseList is not None:
      for aNumber in noGoLanduseList:
        booleanNoGo = pcreq(self.environment, aNumber)
        self.excluded = pcror(self.excluded, booleanNoGo)
##    report(self.excluded, 'excluded')
    i = 0
    for aType in self.types:
      ## Get land use type specific no-go areas based on slope from dictionary
      ## If not present the variable privateNoGoAreas is 'None'
      aSlope = privateNoGoSlopeDict.get(aType)
      if aSlope is not None:
        privateNoGoAreas = pcrgt(self.slopeMap, aSlope)
      self.landUseTypes[i].createInitialMask(self.excluded, privateNoGoAreas)
      i += 1

  def determineDistanceToRoads(self, booleanMapRoads):
    """Create map with distance to roads, given a boolean map with roads."""
    self.distRoads = spread(booleanMapRoads, 0, 1)
##    report(self.distRoads, 'distRoads')
    
  def determineDistanceToWater(self, booleanMapWater):
    """Create map with distance to water, given a boolean map with water."""
    self.distWater = spread(booleanMapWater, 0, 1)
##    report(self.distWater, 'distWater')

  def determineDistanceToLargeCities(self, booleanMapCities):
    """Create map with distance to cities, using a boolean map with cities."""
    self.distCities = spread(booleanMapCities, 0, 1)
##    report(self.distCities, 'distCities')
  
  def calculateStaticSuitabilityMaps(self):
    """Get the part of the suitability maps that remains the same."""
    for aType in self.landUseTypes:
      ## Check whether the type has static suitability factors
      ## Those have to be calculated only once (in initial)
      aType.createInitialSuitabilityMap(self.distRoads, self.distWater, \
                                        self.distCities, self.populationDensity, \
                                        self.cattleDensity)

  def calculateSuitabilityMaps(self):      
    """Get the total suitability maps (static plus dynamic part)."""
    suitMaps = []
    for aType in self.landUseTypes:
      suitabilityMap = aType.getTotalSuitabilityMap()
      suitMaps.append(suitabilityMap)

  def allocate(self, maxYield, demand):
    """Allocate as much of a land use type as indicated in the demand tss."""
    tempEnvironment = self.environment
    immutables = self.excluded
    for aType in self.landUseTypes:
      aType.setMaxYield(maxYield)
      tempEnvironment, immutables = aType.allocate(demand, tempEnvironment, \
                                                   immutables)
    self.setEnvironment(tempEnvironment)    

  def growForest(self):
    """Regrow forest at deforestated areas after 10 years."""
    ## Get all cells that are abandoned in the timestep
    deforestated = pcreq(self.environment, 98)
    ## Update map that counts the years a cell is deforestated
    increment = ifthen(deforestated, self.yearsDeforestated + 1)
    self.yearsDeforestated = cover(increment, self.yearsDeforestated)
    ## Regrow forest after 9 years of abandonement, so it's available
    ## again after 10 years
    regrown = ifthen(self.yearsDeforestated == 9, nominal(self.forest))
    reset = ifthen(regrown == nominal(self.forest), scalar(0))
    self.yearsDeforestated = cover(reset, self.yearsDeforestated)
    ## Update environment
    filledEnvironment = cover(regrown, self.environment)
    self.setEnvironment(filledEnvironment)
    
  def getEnvironment(self):
    """Return the current land use map."""
    return self.environment

  def getBiofuelPotential(self, noGoMap, food, slope, provinces):
    """Return Boolean map with area suitable for energy crops and its total."""
    noBiofuels = pcror(self.excluded, noGoMap)
    for aType in food:
      booleanMap = pcreq(self.environment, aType)
      noBiofuels = pcror(noBiofuels, booleanMap)
    slopeGt = pcrgt(self.slopeMap, slope)
##    report(slopeGt, 'slope' + str(slope))
    noBiofuels = pcror(noBiofuels, slopeGt)
    biofuelPotential = pcrnot(noBiofuels)
    scalarMap = cover(scalar(biofuelPotential), self.nullMask)
    perProvince = areaaverage(scalarMap, provinces)
    totalArea = maptotal(scalarMap)
    totalArea = totalArea / maptotal(self.nullMask + 1)
##    totalArea = self.reduceToOneCell(totalArea)
    return biofuelPotential, perProvince, totalArea

  def getPotentialBiofuelYield(self, biofuelPotential, crop, maxYield, \
                               provinces):
    """Return total possible yield for sugar cane or eucalyptus."""
    convertedMaxYield = (float(maxYield) / float(self.toMeters)) * cellarea()
    if crop == 'sc':
      yieldFracMap = self.scYieldFrac
    elif crop == 'eu':
      yieldFracMap = self.euYieldFrac
    else:
      print('ERROR: unknown crop asked in yield evaluation')
    currentYieldMap = ifthen(biofuelPotential, yieldFracMap * \
                             convertedMaxYield)
    currentYield = cover(currentYieldMap, self.nullMask)
    yieldPerProvince = areaaverage(currentYield, provinces)
    totalBiofuelYield = maptotal(currentYieldMap)
##    totalBiofuelYield = areaaverage(currentYield, nominal(self.nullMask + 1))
    totalBiofuelYield = totalBiofuelYield / maptotal(self.nullMask + 1)
##    totalBiofuelYield = self.reduceToOneCell(totalBiofuelYield)
    return currentYield, yieldPerProvince, totalBiofuelYield

  def reduceToOneCell(self, aMap):
    cloneMap = ifthen(aMap > 0, boolean(1))
    x=xcoordinate(cloneMap)
    y=ycoordinate(cloneMap)
    corner= pcrand(pcreq(x, mapminimum(x)),pcreq(y,mapminimum(y)))    
    oneCellMap=ifthen(corner, scalar(aMap))
##    report(corner,'test')
##    Value, Valid = cellvalue(oneCellMap, 1, 1)
##    print('\n',Value)
    return oneCellMap
  
######################################

class LandUseChangeModel(DynamicModel, MonteCarloModel):
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self)
    setclone('landuse.map')

  def premcloop(self):
    self.initialEnvironment = self.readmap('landuse')
    self.nullMask = self.readmap('nullMask')
    roads = self.readmap('roads')
    water = self.readmap('water')
    cities = self.readmap('cities')
    bioNoGo = self.readmap('bioNoGo')
    noGoMap = readmap('noGo')
    yieldFrac = self.readmap('yield')
    forestYieldFrac = self.readmap('biomass')
    scYieldFrac = self.readmap('scYield')
    population = self.readmap('popDensity')
    cattle = self.readmap('cattleDensity')
    self.dem = self.readmap('dem')
    self.provinces = self.readmap('provinces')

    self.roads = cover(roads, boolean(self.nullMask))
    self.water = cover(water, boolean(self.nullMask))
    self.cities = cover(cities, boolean(self.nullMask))
    self.bioNoGo = cover(bioNoGo, boolean(self.nullMask))
    self.noGoMap = cover(noGoMap, boolean(self.nullMask))
    self.yieldFrac = yieldFrac / mapmaximum(yieldFrac)
    self.forestYieldFrac = forestYieldFrac / mapmaximum(forestYieldFrac)
    self.scYieldFrac = scYieldFrac / mapmaximum(scYieldFrac)
    self.populationDensity = population / mapmaximum(population)
    self.cattleDensity = cattle / mapmaximum(cattle)

    ## Check which maps should get random noise
    self.stochYield = Parameters.getStochYield()
    self.stochPopulation = Parameters.getStochPopulationDensity()
    self.stochCattle = Parameters.getStochCattleDensity()
    self.stochDem = Parameters.getStochDem()

    ## List of landuse types in order of 'who gets to choose first'
    self.landUseList = Parameters.getLandUseList()
    self.food = Parameters.getFoodList()
    self.relatedTypeDict = Parameters.getRelatedTypeDict()

    ## Input values from Parameters file
    self.suitFactorDict = Parameters.getSuitFactorDict()
    self.weightDict = Parameters.getWeightDict()
    self.variableSuperDictionary = Parameters.getVariableSuperDict()
    self.noGoLanduseList = Parameters.getNoGoLanduseTypes()
    self.privateNoGoSlopeDict = Parameters.getPrivateNoGoSlopeDict()

    ## Uniform map of very small numbers, used to avoid equal suitabilities
    self.noise = uniform(1)/10000

  def initial(self):
    ## Create the 'overall' landuse class
    self.environment = self.initialEnvironment
    self.landUse = LandUse(self.landUseList, self.environment, self.nullMask)

    ## Add some random noise to maps for which this in indicated in Parameters
    self.landUse.addRandomNoise(self.yieldFrac, self.forestYieldFrac, \
                                self.scYieldFrac, self.populationDensity, \
                                self.cattleDensity, self.dem, \
                                self.stochYield, self.stochPopulation, \
                                self.stochCattle, self.stochDem)

    ## Create an object for every landuse type in the list
    self.landUse.createLandUseTypeObjects(self.relatedTypeDict, \
                                          self.suitFactorDict, \
                                          self.weightDict, \
                                          self.variableSuperDictionary, \
                                          self.noise)

    ## Static suitability factors
    self.landUse.determineNoGoAreas(self.noGoMap, self.noGoLanduseList, \
                                    self.privateNoGoSlopeDict)
    self.landUse.determineDistanceToRoads(self.roads)
    self.landUse.determineDistanceToWater(self.water)
    self.landUse.determineDistanceToLargeCities(self.cities)
    self.landUse.calculateStaticSuitabilityMaps()
          
    ## Draw random numbers between zero and one
    ## To determine yield and demand
    self.demandStoch = mapuniform()
    print('FRACTION DEMAND IS',round(float(self.demandStoch),2),'\n')
    self.maxYieldStoch = mapnormal() * self.stochYield[2]
    self.bioMaxYieldStoch = mapnormal() * self.stochYield[2]

  def dynamic(self):
    timeStep = self.currentTimeStep()
    print('\ntime step', timeStep)

    ## Get max yield and demand per land use type
    maxYield = timeinputscalar('maxYield.tss', self.environment)
    scMaxYield = timeinputscalar('bioMaxYield.tss', 2)
    euMaxYield = timeinputscalar('bioMaxYield.tss', 1)
    if self.stochYield[0] == 1:
      maxYield += self.maxYieldStoch * maxYield
      maxYield = max(0, maxYield)
      scMaxYield += self.bioMaxYieldStoch * scMaxYield
      scMaxYield = max(0, scMaxYield)
      euMaxYield += self.bioMaxYieldStoch * euMaxYield
      euMaxYield = max(0, euMaxYield)
##    print('eu is', float(euMaxYield), 'sc is', float(scMaxYield))
    
    demandUp = timeinputscalar('demandUp.tss', self.environment)
    demandLow = timeinputscalar('demandLow.tss', self.environment)
    demandDiff = (demandUp - demandLow)
    demand = demandDiff * self.demandStoch + demandLow
    
    ## Suibility maps are calculated
    self.landUse.calculateSuitabilityMaps()

    ## Allocate new land use using demands of current time step
    self.landUse.allocate(maxYield, demand)
    self.landUse.growForest()
    self.environment = self.landUse.getEnvironment()

    self.report(self.environment, 'landUse')
    os.system('legend --clone landuse.map -f \"legendLU.txt\" %s ' \
              %generateNameST('landUse', self.currentSampleNumber(),timeStep))


    ## Check which area is available for bioenergy crops
    ## and the total area per province and for the whole country
    sc, scPr, scTot = self.landUse.getBiofuelPotential(self.bioNoGo, \
                                   self.food, 0.09, self.provinces)
    eu, euPr, euTot = self.landUse.getBiofuelPotential(self.bioNoGo, \
                                   self.food, 1, self.provinces)
    scSc = scalar(sc)
    euSc = scalar(eu)

    ## sugar cane
    self.report(sc, 'sc')
    self.report(scSc, 'scSc')  
    self.report(scTot, 'scTo')
    self.report(scPr, 'scPr')

    ## eucalyptus
    self.report(eu, 'eu')
    self.report(euSc, 'euSc')
    self.report(euTot, 'euTo')
    self.report(euPr, 'euPr') 

    ## Calculate the potential yield per cell, per province and total
    scYield, syPr, syTot = self.landUse.getPotentialBiofuelYield(sc, 'sc', \
                                                  scMaxYield, self.provinces)
    euYield, eyPr, eyTot = self.landUse.getPotentialBiofuelYield(eu, 'eu', \
                                                  euMaxYield, self.provinces)    
    ## sugar cane
    self.report(scYield, 'sY')   
    self.report(syPr, 'sYPr')    
    self.report(syTot, 'sYTo')

    ## eucalyptus
    self.report(euYield, 'eY')
    self.report(eyPr, 'eYPr')
    self.report(eyTot, 'eYTo')
    
  def postmcloop(self):
    print('\nrunning postmcloop...')
    print('...making movie of land use for 1 sample...')
    command = "python movie_land_use.py"
    os.system(command)
    if int(self.nrSamples()) > 1:
      ## Stochastic variables for which mean, var and percentiles are needed
      print('...calculating statistics...')
      names = ['euSc', 'euTo', 'euPr', 'eY', 'eYPr', 'eYTo']
      sampleNumbers = self.sampleNumbers()
      timeSteps = self.timeSteps()
      percentiles = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
      mcaveragevariance(names, sampleNumbers, timeSteps)
      names = ['eY', 'eYPr', 'eYTo']
      #mcpercentiles(names, percentiles, sampleNumbers, timeSteps)
      print('...making movie of availability...')
      command = "python movie_availability.py"
      os.system(command)

    print('\n...done')

nrOfTimeSteps = Parameters.getNrTimesteps()
nrOfSamples = Parameters.getNrSamples()
myModel = LandUseChangeModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel, nrOfSamples)
mcModel.run()
