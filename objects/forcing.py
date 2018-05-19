from objects.reader_csv import Reader_CSV
from objects.sun import Sun
from datetime import datetime
from objects.environment import Environment
import pandas as pa
import numpy as np
import objects.utils as utils

class Forcing:

    reader = None

    
    # the variables required in the forcing data
    fields_required = [
        'datetime',
        'G',
        'T_A',
        'v_10',
    ]

    ds = None
    sun = None
    G = None
    Dh = None
    H = None
    T_A = None
    T_Gnd = None
    gamma = None
    psi = None
    v_1 = None

    def __init__(self, model_dt, csv_loc,  lon,  lat):
        self.reader = Reader_CSV(csv_loc, self.fields_required, 'forcing')
        self.ds = self.reader.load()

        # interpolate the forcing data to the model timestep
        # will later be saved to numpy arrays for faster access
        print('      interpolating...')

        new_dt = int(1000.0*model_dt)
        new_range = pa.date_range(self.ds.index.values[0], self.ds.index.values[-1], freq=str(new_dt)+'ms')

        self.ds = self.ds.reindex(new_range)
        self.ds = self.ds.interpolate(method='linear')

        if not ('H' in self.ds.columns):
            H_prescribed = False
            print('      H will be derived from G and gamma...')
        else:
            H_prescribed = True

        if not ('T_Gnd' in self.ds.columns):
            T_Gnd_prescribed = False
            print('      T_Gnd is approximated as T_A...')
        else:
            T_Gnd_prescribed = True

        utils.mwrite('      calculating additional quantities...')
        # calculate other quantities at forcing timestep
        n = len(self.ds.index)
        self.sun = Sun(lon, lat)

        gammas = np.zeros(n)
        psis = np.zeros(n)
        Dh = np.zeros(n)
        v_1	= np.zeros(n)

        if not H_prescribed:
            self.ds['H'] = np.zeros(n)

        if not T_Gnd_prescribed:
            # The T_Gnd data in Horak et al 2017 was calculated with a separate model. In the future this may
            # potentially be implemented here as well but as of now is not. Therefore, if T_Gnd is not supplied in
            # the forcing, it is approximated by T_A.
            self.ds['T_Gnd'] = self.ds['T_A']

        for i in range(0, len(self.ds.index.values)):
            dtime       = datetime.utcfromtimestamp((self.ds.ix[i].name - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))
            self.sun.set_datetime(dtime)

            gammas[i] = self.sun.gamma
            psis[i] = self.sun.psi

            if not H_prescribed:
                k_t = self.ds.ix[i].G / 1366.0            # clearness index
                self.ds.ix[i,'H'] = self.ds.ix[i].G * (1.400-1.749*k_t*0.177*np.sin(self.sun.gamma))

            Dh[i] = self.ds.ix[i].G-self.ds.ix[i].H
            v_1[i] = self.ds.ix[i].v_10*np.log(1.0/Environment.z0)/np.log(10.0/Environment.z0)

        self.ds['gamma'] = gammas
        self.ds['psi'] = psis
        self.ds['Dh'] = Dh
        self.ds['v_1'] = v_1

        # create numpy arrays from interpolated forcing data for faster access during main loop
        self.G = self.ds.G.values
        self.Dh = self.ds.Dh.values
        self.H = self.ds.H.values
        self.T_A = self.ds.T_A.values
        self.T_Gnd = self.ds.T_Gnd.values
        self.gamma = self.ds.gamma.values
        self.psi = self.ds.psi.values
        self.v_1 = self.ds.v_1.values

        print('    done...\n')

    # interpolates forcing to current timestep
    def values_at(self,  dtime):
        left = self.ds.asof(dtime)
        t = pa.Timedelta(dtime-left.datetime).seconds

        if t > 0:
            i   = self.ds.index.get_loc(left.datetime)
            ip1 = i+1

            if ip1 > len(self.ds.index):
                return left
            else:
                right = self.ds.iloc[ip1]

                timestep = pa.Timedelta(right.datetime-left.datetime).seconds    # current timestep of forcing
                slope = (right-left)/timestep

                result = left + slope*t
                return result
        else:
            return left




