# Simplified Automobile Thermodynamics
SAT is a model that calculates the time course of the cabin air temperature within a vehicle in dependence of three atmospheric parameters available at standard weather stations (air temperature at 2m, global radiation and wind speed). The model and underlying physics, as well as its evaluation with field experiments, were described in [Horak et al 2017](https://link.springer.com/article/10.1007/s00704-016-1861-3).

**note:**
(i) The model in Horak et al 2017 was originally implemented in C#. For this python3 reimplementation the code was structured more clearly and commented throughout. It reproduces the results from the paper, however a small error in the code was corrected that leads to slightly different results now (see commit history).
(ii) As of now the reimplementation it is not feature complete, I am currently working on a better implementation of how solar radiation transmitted through windows is handled. At the moment only vehicles without windows may be modelled (such as transport vans for instance). Furthermore, additionall to T2m, G and v_10m, the quantities H (diffuse radiation) and T_Gnd need to be present in the forcing files. An equation to estimate H from G is given in Horak et al 2017, while, as a first order approximation, TGnd may be approximated by T2m.

## Quickstart
1. Download the model
2. Make sure the requirements are satisfied (see section requirements)
3. Create a vehicle configuration
A vehicle is specified by two files.
3.1 The general information file contains the following fields:

   - code ... a shortcode to identify the vehicle
   - description ... a longer description
   - alpha ... the azimuthal orientation of the vehicle front in degree (0.. north, 90..west, 180.. south, 270.. east)
   - beta ... the vertical orientation of the vehicle front in degree (90..normal to ground, currently the only option)
   - l, w, h ... the dimensions of the vehicle in meters (length, width and height)

see as an example the definition file in [./example/car_nowindows_xmpl.csv](./example/car_nowindows_xmpl.csv). It specifies a transport van with shortname 'my_van' that is oriented south. It has the dimensions 2.4x1.9x1.3 m³. Note that the fact that the van is windowless is defined in the car_body definition file.

3.2 he car_body file contains details about how each of the 6 vehicle walls are made up.

wall ... integer id of the vehicle wall.  fixed values are: 1.. front, 2..floor, 3..left wall, 4..right wall, 5.. roof, 6..back wall left and right as seen when standing in front of the vehicle.
part ... walls may consist of multiple parts, e.g. half of it may be a window while the other half consists of a multi-layered structure. Numbering should start at 1.
a_eff ... specifies the relative area of the surface that a part occupies.
layer ... a part may consist of multiple layers, e.g. a steel outer layer, and an insulating layer on the inside. Numbering starts at the outhermost layer with 1 and increases in integer steps from there.
th ... specifies the thickness of the layer in meters
material ... the material the layer is made of. the material name and thermodynamic properties are specified in the file ./data/materials.csv
surface ... specifies the optical properties of the layers surface. These are only relevant if the layer is adjacent to the environment or the vehicle interior. The optical properties are specified in the file ./data/surfaces.csv

see as an example the car body definition file in [./example/car_body_nowindows_xmpl.csv](./example/car_body_nowindows_xmpl.csv). It specifies how each of the six walls of the vehicle are made up. Each consist of one part, and each of these parts are made up of two layers. One 1mm thick steel layer on the outside, and an insulating layer on the inside. The front side of the vehicle (wall 1) and its roof (wall 5) have a thicker insulation layer than the other walls (5cm compared to 1cm).

4) Create a forcing file
A forcing file contains the state of the atmosphere during the time the simulation is to be run.

datetime ... Time at which the variables have the respective values. Format YYYY-MM-DD HH:MM:SS, in between the model interpolates linearly to the model time step (usually 1 second).
T_A ... The air temperature at 2m in degree centigrade
G ... Global radiation in W/m²
H ... Diffuse radiation in W/m² (equation to estimate from G given in Horak et al 2017 - will be automatized in the feature if not defined here).
T_Gnd ... Ground temperature in degree centigrade. (As a first order approximation may use T_A, will be automatized in the feature)
v_10 ... wind speed at 10m height in m/s

Currently H and T_Gnd have to be specified, however, both can be estimated from T_A, G and v_10 as has been done in Horak et al 2017.

5) Create a scenario file
This is not necessary, the above information is enough to run the model from command line (while specifying the definition files and, e.g. initial temperature, duration of the model run, ...). A more convinient way to do so is to generate a scenario file that tells the model which definition files should be used for a model run and what values other parameters should have. See, for instance, the scenario file [./example/scenario_xmpl.opt](./example/scenario_xmpl.opt).

outpath ... path where the model output is stored
forcing_file ... path and filename of the forcing file
car_file ... path and filename of the general car information file
body_file ... path and filename of the car body file
date ... start model run for this date
time ... time model run for this time
duration ... time period to simulate in hours
T0 ... initial temperature of all car body components

the example file runs a simulation for the windowless transport van (my_car), for one hour, starting on the 26th of August in 2008 at 10:00. All car components are initialized at a temperature of 25 degree centigrade.

    run the model with python3 sat.py -o ./example/scenario_xmpl.opt

6) Model output
The model currently creates the output file sat_cabin_air.csv. It contains the time course of the cabin air temperature for the simulated period and lists the absolute and relative time at which it occurs.


## Problems?
If you run into any troubles or have questions, please don't hesitate to file a bug report and/or contact me! I'm happy to help you to get the model to run.

## Requirements
### System
The model was tested an run under Ubuntu 16. It requires *python 3.6* to run. It should work with windows systems as well, however, I have not tested it so far.

### Packages
- numpy
- scipy
- pandas
- bunch



## Introduction




