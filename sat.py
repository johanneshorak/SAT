from bunch import Bunch
from objects.forcing import Forcing
from objects.horizon import Horizon
from objects.car import Car
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.cm as cm


# options
options = Bunch()
options["dx"]=0.001
options["model_dt"]=1.0
options["write_dt"]=60.0

# main files
forcing_file="./input/v-w-000_environment_26082008_1000-1145.csv"
horizon_file="./input/horizon_fct_vu-wien.csv"
car_file="./input/v-w-000_general.csv"
body_file="./input/v-w-000_body.csv"

forcing = Forcing(forcing_file)
horizon = Horizon(horizon_file)
car = Car(options, car_file, body_file)
car.initialize(20.0)

#print forcing.ds
#print horizon.ds
#print materials.ds
#print surfaces.ds


'''
fig, ax = plt.subplots(1, 1)	
ax.scatter(forcing_ds.index.values, forcing_ds.G.values)
ax.set_xlim([forcing_ds.index[0], forcing_ds.index[-1]])
plt.savefig('testplot.png')
plt.close()
'''
