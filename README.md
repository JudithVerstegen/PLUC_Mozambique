# PLUC_Mozambique

This is the PCRaster Land Use Change model (PLUC) for Mozambique, created in [PCRaster](http://pcraster.geo.uu.nl/) Python. Results of the model are published in [Verstegen et al. 2012](https://doi.org/10.1016%2Fj.compenvurbsys.2011.08.003) and [van der Hilst et al. 2012](https://doi.org/10.1111/j.1757-1707.2011.01147.x).


Manual for land use change model in PCRaster Python

Author: Judith Verstegen, January 27th 2011, edited for [GitHub distribution](https://github.com/JudithVerstegen/PLUC_Mozambique) in December 2016


1. Introduction
---------------

A land use change model of Mozambique was created in PCRaster Python. The aim of the model is to evaluate where bio energy crops can be cultivated without endangering food production now and in the near future when population and thus food crop and pasture areas will increase. It is possible to run the model with different land use classifications, suitability factors, model parameters, and even for a different region when required. This manual specifies the software requirements, outlines the model scheme, explains how to manage input data and parameter settings, shows how to run the model, and lists model outputs.


2. Requirements
--------------

In order to run the model, installation of PCRaster Python is required. PLCU Mozambique has been updated to be compatible with PCRaster version `4.1.0`. The installation guide and files can be found at http://pcraster.geo.uu.nl/getting-started/. The minimum requirement to use PCRaster Python is [Python](https://www.numpy.org/) version `2.7` and [Numpy](http://www.numpy.org/) version `1.8`.


3. Model description
------------------

The main procedure of the model is the state transition function, the spatially explicit change in land use. This change is modelled in time steps of a year. It is driven by two factors: the demand of the population for food and wood, and the maximum potential yield of the land, defined by the country's technological state of the art in agriculture. The actual location of the expansion or contraction of the land use types is determined by suitability factors, like distance to cities and transport networks, current land use in the neighbourhood and location-specific yield due to characteristics of the soil. Areas not occupied by food production or reserved land use are available for bio energy crops.

The model is constructed with the use of two PCRaster Python frameworks: the dynamic modelling framework and the Monte Carlo framework. These frameworks together form the schedule of the model that determines the order of execution of the implemented methods. Two separate classes exist in the model file `LU_Moz.py`: `LandUse` and `LandUseType`. The first keeps track of the land use map and carries out 'global' tasks, valid for the whole land use system. Methods for the individual land use types are implemented in the second class. For every dynamic land use type in the land use map an instance of this class is created. An important task of the land use type instances is the generation of a suitability map that indicates the appropriateness of a certain location to allocate land of the type. It can be specified by the user which land use type should use which suitability factors with which parameter values, as will be explained in the next chapter.


4. Inputs
--------------

The model consists out of input maps, input time series, one legend file, and two Python files. Below it is explained where to edit what, when one wants to run the model with different inputs.

*Maps*

Maps carry all spatially explicit data. Maps have to be provided according to the PCRaster map format (extension `.map`). A description how to convert ascii files to PCRaster maps can be found under the `asc2map` command in the PCRaster documentation: http://pcraster.geo.uu.nl/support/documentation. We have used the map projection Moznet UTM Zone 36S ([EPSG:3036](https://epsg.io/3036)). The current PCRaster metadata of all maps is:

variable | value |
----- | ----- |
ncols | 1166 |
nrows | 1839 |
xllcorner | 195374 |
yllcorner | 7003459 |
cellsize | 1000 | 
NODATA_value | -9999 |

Maps can be replaced by new maps as long as one keeps the extent, filename, data type (value scale) and measurement unit the same. It is also possible to change the study area (and thus extent), but all maps need to have the same extent. An overview of all input maps and their characteristics is given in Table 1. Note that the unit for cattle and population density states 'per area'. This means it does not matter whether this is per cell or per meter or something else, because the data is only used as a proxy and will be normalized anyway. If there is no need to exclude extra areas for bioenergy crops, then make the 'bioNoGo' input map empty (all `No Data` values) or copy the general 'noGo' map into it.

Table 1: Characteristics of input maps

filename | contents | data type | unit |
------ | ------ | -------| ------| 
biomass.map | fraction of the maximum biomass a forest cell produces | scalar | -	| 
bioNoGo.map | all areas that cannot be used by bioenergy crops in addition to noGo.map (cannot be changed = true) | Boolean  | -
cattleDensity.map | nr of cows and goats per area unit | scalar | animals/area |
cities.map | whether or not a cell contains a city (city = true) | Boolean | - |               	
dem.map | Digital Elevation Model of the study area | scalar | meters |
landuse.map | land use classes; all dynamic land use types must exhibit at least one cell in the initial land use map | nominal | - |
noGo.map    | all areas that cannot be changed and do NOT have a specific class in the land use map (roads, water, nature areas, ....) (cannot be changed = true) | Boolean  | - |
nullMask.map | value `0` for cells included in the study area and `No Data` for cells outside the study area | scalar | - |
popDensity.map | nr of people per area unit | scalar | people/area |
roads.map | whether or not a main road is present in a cell (road = true) | Boolean | - |
scYield.map | fraction of the maximum yield a cell can reach for sugar cane | scalar | - |
water.map | whether or not a river or water body is present in a cell (water = true) | Boolean | - |
yield.map | fraction of the maximum yield a cell can reach for food crops and pasture | scalar | - |

*Time series*

Time series are structured in ascii files (extension `.tss`). They consist of a header and a body. The header specifies the type of information provided, the number of columns in the body and the contents of those columns. The header thus contains as many lines as the nr of land use classes + 3. The body, i.e. data frame, contains the time steps and values for every land use class belonging to these time steps. An example of the header and first two time steps of the demand is:

	demand per land use type 
	11 
	model time with t0 = 2005 crops (=1) (ton/year) 
	crops grass (=2) (ton/year) crops pasture (=3) (ton/year) forest (=4) (ton/year) 
	nothing (=5) 
	grass (=6) 
	pasture (=7) (ton/year) 
	shrubs (=8) 
	excluded (=9) 
	urban (=10) 
	1	1517230	0 	14294510	 46620500	 0	0	1017512	0	0 	0	
	2	1600709	61695	14810098	45454988	0	0	1026875	0	0	0	

Currently, four time series are used:

- the lower limit of the expected demand,
- the upper limit of the expected demand,
- the maximum yield of land use types in the land use map, and 
- the maximum yield of bioenergy crops.

The maximum yield is provided per area unit. Furthermore, it does not matter whether yield is in kg, kcal or something else per area unit, as long as the unit of the numerator is the same as the unit of the demand. Make sure to use sufficient precision in the calibrated demand and maximum yield of the first time step; it is experienced that omitting some decimals can have profound effects. The range between upper and lower limit of the demand originates from uncertainty in population growth, self-sufficiency ratio and/or diet of the population. The easiest way to dismiss this uncertainty in a model run is to give the two files `demandUp.tss` and `demandLow.tss` the same contents.

*Legend file*

A legend, given in the text file `legendLU.txt`, is used to attach to the output land use maps. An example of its outlook is given below.

	-0 landuse
	1 cropland
	2 cropland+grassland
	3 cropland+pasture
	4 forest
	5 abandoned
	6 grassland
	7 pasture
	8 shrubland
	9 excluded
	10 urban

The first line of the file indicates the contents (title) and every following line provides a class number and its corresponding class name. When a new input land use map is used, do not forget to change the legend file as well, so that the land use maps generated by the model will have the correct legend.

*Python files*

Two Python files are used. `LU_Moz.py` is the model itself and `Parameters.py` contains all static, non- spatial input variables and parameters, i.e. the ones not included in a map or time series. The latter Python file can be edited when different inputs are required, for example with [IDLE](https://docs.python.org/2/library/idle.html). The file is assumed to be self-explanatory for most variables and parameters.
 
The specification  of  the  suitability  factors  for  the  land  use  types  needs  some  further explanation. An overview of all implemented suitability factors and their parameters is given in Table 2. Make sure that all necessary parameters are specified for all suitability factors that a land use type implements.

Table 2: Implemented suitability factors and their parameters

nr | description | parameter 1 | parameter 2 | parameter 3 | parameter 4 |
---- | ---- | ---- | ---- | ---- | ---- | 
1 | nr of neighbours same class | window length<sup>1</sup> | - | - | - |
2 | distance to roads | direction<sup>2</sup> | max distance effect<sup>3</sup> | friction<sup>4</sup> | relation type<sup>5</sup> |
3 | distance to water | direction<sup>2</sup> | max distance effect<sup>3</sup> | friction<sup>4</sup> | relation type<sup>5</sup> |
4 | distance to cities | direction<sup>2</sup> | max distance effect<sup>3 | friction<sup>4</sup> | relation type<sup>5</sup> |
5 | yield | friction<sup>4</sup> | - | - | - | 
6 | population density | direction<sup>2</sup> | - | - | - | 
7 | cattle density | direction<sup>2</sup> | - | - | - |
8 | distance to forest edge | - | - | - | - |
9 | current land use | suitability current lu<sup>6</sup> | - | - | - |

Footnotes to Table 2:

1. window length (in m.) in which neighbours are counted; e.g. `3000` for `3x3` window when cell length is 1000 m.
1. direction of the distance function; `1` = positive; `-1` = negative
1. maximum distance of effect (in `m`) of the distance function; e.g. `100000` for effect up to 100 cells away when cell length is 1000 m.
1. friction in the distance function; used in `e ^ friction * distance` only for an exponential distance function; use `1` when unknown or when the relation is not exponential
1. type of distance function; `0` = linear; `1` = exponential; `2` = inversely proportional
1. Python dictionary with suitability of current land use for placing the new land use; e.g. `3 : 0.7` means that land use type `3` has a suitability of `0.7` for becoming the land use type that holds this suitability factor (types not specified will have no additional suitability due to factor `9`); especially useful to give abandoned areas a higher suitability


5. Running the model
--------------------

When all maps and time series are present and all static, non-spatial inputs are correctly specified the model can be run by double clicking on the file LU_Moz.py. A command window will be appear and be present until the run is finished. Running the model once (indicated by setting the variable 'samples' to 1 in the Parameter.py file) will take approximately five minutes on a standard pc (timed on a 2 GHz processor with 4 GB RAM). When a Monte Carlo batch run is done (the variable 'samples' is much larger then 1) completion can take several hours.

```bash
cd model/
python2 LU_Moz.py
```

6. Outputs
----------------

All outputs of the model are maps in the PCRaster map format (extension `.map`). They can be viewed with the software [Aguila](http://pcraster.geo.uu.nl/projects/developments/aguila/).

Two types of outputs are generated by the model. Outputs that are written to disk in each time step of each Monte Carlo sample (type 1) and outputs for each time step averaged over all samples (type 2). Consequently, when the model is run once, only outputs of type 1 are generated. An overview all outputs, their contents, output type, and data type is given in Table 3.

Outputs of type 1 can be visualized with a command like:
> aguila --scenarios='{1,2,3,4,5}' --timesteps=[1,26] --multi=1x5 filename

Outputs of type 2 can be visualized with a command like:
> aguila --timesteps=[1,26] filename

For a detailed description of visualization commands and options of the Graphical User Interface the user is referred to the Aguila manual that can be found in the PCRaster documentation for the required version: http://pcraster.geo.uu.nl/support/documentation.

Table 3: Overview of model outputs

filename | contents | output type | data type |
--- | --- | --- | --- |
eu | whether or not a cell is available for eucalyptus | 1 | Boolean |
euPr | available area per province for eucalyptus (km2) | 1 | scalar |
euSc | scalar of whether or not a cell is available for eucalyptus (used as input for output type 2, use eu output for visualization purposes) | 1 | scalar |
euTo | total available area for eucalyptus (km2) | 1 | scalar |
eY | potential bioenergy yield for eucalyptus | 1 | scalar |
eYPr | potential bioenergy yield per province for eucalyptus (non-spatial) | 1 | scalar |
eYTo | total potential bioenergy yield for eucalyptus (non-spatial) | 1 | scalar |
landUse | land use | 1 | nominal |
sc | whether or not a cell is available for sugar cane | 1 | Boolean |
scPr | available area for a province for sugar cane (km2) | 1 | scalar |
scSc | scalar of whether or not a cell is available for sugar cane (used as input for output type 2, use sc output for visualization purposes) | 1 | scalar |
scTo | total available area for sugar cane (km2) | 1 | scalar |
sY | potential bioenergy yield per km2 for sugar cane | 1 | scalar |
sYPr | potential bioenergy yield per km2 for a province for sugar cane | 1 | scalar |
sYTo | potential bioenergy yield per km2 for sugar cane for the whole country (non-spatial) | 1 | scalar |
euSc/scSc-ave<sup>7</sup> | probability that is cell is available for the bioenergy crop type | 2 | scalar |
euSc/scSc-err<sup>7</sup> | relative error (standard deviation / mean) of each cell for the availability of the bioenergy crop type | 2 | scalar |
euSc/scSc-var<sup>7</sup> | variance of each cell for the availability of the bioenergy crop type | 2 | scalar |

Footnote 7: These three outputs can in principle be generated for all scalar outputs of type 1.

Note that output will be overwritten when the model is run again, so make sure to copy all output somewhere else when it is needed again. 
## 8. Running the model with Docker

### About

[Docker is](https://www.docker.com/what-docker) a containerization solution to package applications and their dependencies. It is very well suited [for reproducible research](https://scholar.google.de/scholar?q=docker+%22reproducible+research%22&btnG=&hl=de&as_sdt=0%2C5), because it allows to capture and transfer a scientist's runtime environment (see [Boettiger et al.](https://doi.org/10.1145/2723872.2723882) and [Nüst et al.](http://doi.org/10.1045/january2017-nuest)).

A Docker _container_ is the running instance of a Docker _image_. A Docker _image_ can be build following the instructions in a [Dockerfile](https://docs.docker.com/engine/reference/builder/), which is like a manifest or recipe for the image. Ready-to-use images are published on [Docker Hub](https://hub.docker.com/help/) and [can be run](https://docs.docker.com/engine/reference/run/) on any machine that has a working Docker installation with a single command.

This repository contains a `Dockerfile` with the instructions to (i) install PCRaster and all requirements, (ii) copy all input files into the image, and (iii) run the analysis. You can either [run a pre-build image from Docker Hub](#run-from-docker-hub) or [build locally and run it](#build-image-locally-and-run-it).

### tl;dr

```bash
docker run -it --name pluc_moz nuest/pluc_mozambique
```

### Install Docker

Install [Docker Community Edition](https://www.docker.com/community-edition#/download).

### Run from Docker Hub

Execute the following commands to 

1. run the analysis in a Docker [image from Docker Hub](https://hub.docker.com/r/nuest/pluc_mozambique/) and 
2. extract two video files from the container showing the model result.

```bash
# 1.
docker run -it --name pluc_moz nuest/pluc_mozambique

# 2.
docker cp lu-moz:/pluc/movie_euSc-ave.mp4 movie_euSc-ave.mp4
docker cp lu-moz:/pluc/movie_landUse.mp4 movie_landUse.mp4
```

The image contains [Label Schema](http://label-schema.org) metadata, which you can [explore on MicroBadger](https://microbadger.com/images/nuest/pluc_mozambique). The images on Docker Hub have [tags](https://hub.docker.com/r/nuest/pluc_mozambique/tags/) matching the [respective git commit](https://github.com/nuest/PLUC_Mozambique/tree/5e5d91ef88b1bc39b0390c8a30fa2ba253749023) for each time they are build. To increase reproducibility it is recommended to always execute a specific tag.

You can use the following commands to

1. `run` a specific image tag (by default Docker uses the tag `latest`),
1. [remove](https://docs.docker.com/engine/reference/commandline/rm/) a container from a previous executions (must match name provided with `docker run --name ..`,
1. change the configuration by [mounting](https://docs.docker.com/engine/reference/commandline/run/#mount-volume--v-read-only) your own configuration file into the container as a volume (an edited copy of `model/Parameters.py` in this repository, or
1. [open a Bash shell](https://docs.docker.com/engine/reference/commandline/run/#options) in a [ephemeral container](https://docs.docker.com/engine/reference/run/#clean-up-rm) the container for debugging:

```bash
# 1.
docker run nuest/pluc_mozambique:5e5d91e

# 2.
docker rm pluc_moz

# 3.
docker run -it -v $(pwd)/my_params.py:/pluc/Parameters.py nuest/pluc_mozambique

# 4.
docker run -it --rm --entrypoint /bin/bash nuest/pluc_mozambique
```

### Build image locally and run it

```bash
docker build --tag my-pcraster-pluc .
docker run -it --rm my-pcraster-pluc
```
