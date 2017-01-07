# PLUC_Mozambique

This is the PCRaster Land Use Change model (PLUC) for Mozambique, created in PCRaster Python. Results of the model are published in Verstegen et al. 2012 and van der Hilst et al. 2012.



Manual for land use change model in PCRaster Python

Author: Judith Verstegen, January 27th 2011, edited on December 28th 2016


1. Introduction

A land use change model of Mozambique was created in PCRaster Python. The aim of the model is to evaluate where bio energy crops can be cultivated without endangering food production now and in the near future when population and thus food crop and pasture areas will increase. It is possible to run the model with different land use classifications, suitability factors, model parameters, and even for a different region when required. This manual specifies the software requirements, outlines the model scheme, explains how to manage input data and parameter settings, shows how to run the model, and lists model outputs.


2. Requirements

In order to run the model, installation of PCRaster Python is required. The installation guide and files can be found at http://pcraster.geo.uu.nl/getting-started/. The minimum requirement to use PCRaster Python is Python version 2.7 and Numpy version 1.8.


3. Model description

The main procedure of the model is the state transition function, the spatially explicit change in land use. This change is modelled in time steps of a year. It is driven by two factors: the demand of the population for food and wood, and the maximum potential yield of the land, defined by the country's technological state of the art in agriculture. The actual location of the expansion or contraction of the land use types is determined by suitability factors, like distance to cities and transport networks, current land use in the neighbourhood and location-specific yield due to characteristics of the soil. Areas not occupied by food production or reserved land use are available for bio energy crops.

The model is constructed with the use of two PCRaster Python frameworks: the dynamic modelling framework and the Monte Carlo framework. These frameworks together form the schedule of the model that determines the order of execution of the implemented methods. Two separate classes exist in the model file: LandUse and LandUseType. The first keeps track of the land use map and carries out 'global' tasks, valid for the whole land use system. Methods for the individual land use types are implemented in the second class. For every dynamic land use type in the land use map an instance of this class is created. An important task of the land use type instances is the generation of a suitability map that indicates the appropriateness of a certain location to allocate land of the type. It can be specified by the user which land use type should use which suitability factors with which parameter values, as will be explained in the next chapter.


4. Inputs

The model is distributed as a compressed file (zip file). When unpacked, one will see it consists out of input maps, input time series, one legend file, and two Python files. Below it is explained where to edit what when one wants to run the model with different inputs.

Maps
Maps carry all spatially explicit data. Maps have to be provided according to the PCRaster map format (extension .map). A description how to convert ascii files to PCRaster maps can be found at
http://www.carthago.nl/miracle/doc/AscGridtutorial.pdf. The current metadata of all maps is:

ncols 1166
nrows 1839
xllcorner 195374
yllcorner 7003459
cellsize 1000

NODATA_value -9999

Maps can be replaced by new maps as long as one keeps the extent, filename, data type (value scale) and measurement unit the same. It is also possible to change the study area (and thus extent), but all maps need to have the same extent. An overview of all input maps and their characteristics is given in Table 1. Note that the unit for cattle and population density states 'per area'. This means it does not matter whether this is per cell or per meter or something else, because the data is only used as a proxy and will be normalized anyway. If there is no need to exclude extra areas for bioenergy crops, then make the 'bioNoGo' input map empty (all No Data values) or copy the general 'noGo' map into it.

filename | contents | data type | unit |
------ | ------ | -------| ------| 
biomass.map | fraction of the maximum biomass a forest cell produces | scalar | -	| 
bioNoGo.map | all areas that cannot be used by bioenergy crops in addition to noGo.map (cannot be changed = true) | Boolean  | -
cattleDensity.map | nr of cows and goats per area unit | scalar | animals/area |
cities.map | whether or not a cell contains a city (city = true) | Boolean | - |               	
dem.map | Digital Elevation Model of the study area | scalar | meters |
landuse.map | land use classes; all dynamic land use types must exhibit at least one cell in the initial land use map | nominal | - |
noGo.map    | all areas that cannot be changed and do NOT have a specific class in the land use map (roads, water, nature areas, ....) (can’t be changed = true) | Boolean  | - |
nullMask.map | value 0 for cells included in the study area and No Data for cells outside the study area | scalar | - |
popDensity.map | nr of people per area unit | scalar | people/area |
roads.map | whether or not a main road is present in a cell (road = true) | Boolean | - |
scYield.map | fraction of the maximum yield a cell can reach for sugar cane | scalar | - |
water.map | whether or not a river or water body is present in a cell (water = true) | Boolean | - |
yield.map | fraction of the maximum yield a cell can reach for food crops and pasture | scalar | - |

