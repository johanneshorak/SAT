import numpy as np

class Sun():

    datetime=None

    lon	= None
    lat	= None

    doy	= None
    x	= None

    woz = None
    zmin = None
    delta = None

    gamma = None
    psi = None

    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def to_string(self):
        return "doy={:3.2f}\tx={:3.2f}\twozh={:3.2f}\tzmin={:3.2f}\tdelta={:3.2f}\tpsi={:3.2f}\tgamma={:3.2f}".format(self.doy, self.x, self.wozh,  self.zmin, (180.0/np.pi)*self.delta, (180.0/np.pi)*self.psi, (180.0/np.pi)*self.gamma)

    # setting datetime updates all other variables!
    def set_datetime(self, dtime):
        self.datetime=dtime
        self.doy = dtime.timetuple().tm_yday
        self.x	 = self.doy*0.9856-2.72
        self.Zmin_update()
        self.woz_update()
        self.delta_update()
        self.gamma_update()
        self.psi_update()
        self.to_string()
        #print "{:2.4f}\t".


    def Zmin_update(self):
        term1 = -7.66*np.sin((np.pi/180.0)*self.x)
        term2b = (2.0*self.x+24.99+3.83*np.sin((np.pi/180.0)*self.x))
        term2a = -9.87*np.sin((np.pi/180.0)*term2b)

        zmin = term1+term2a

        self.zmin = zmin

        return zmin

    def gamma_update(self):
        term1 = np.sin(self.lat*(np.pi/180.0))*np.sin(self.delta)
        term2 = np.cos(self.lat*(np.pi/180.0))*np.cos(self.delta)*np.cos(self.woz_rad)
        gamma = np.arcsin(term1+term2)
        self.gamma = gamma
        return gamma

    def psi_update(self):
        term1 = np.sin(self.lat*(np.pi/180.0))*np.sin(self.gamma)-np.sin(self.delta)
        term2 = np.cos(self.lat*(np.pi/180.0))*np.cos(self.gamma)
        psi = np.arccos(term1/term2)
        if (self.wozh < 12):
            psi = psi*-1;

        psi = psi+np.pi  # 0 deg. is north in our coordinate system => add np.pi to transform to our CS.

        if psi > 360.0:
            psi = psi-360

        self.psi = psi
        return psi

    # true local time in hours
    def woz_update(self):
        hour = self.datetime.hour+self.datetime.minute/60.0

        wozh = hour-(15.0-self.lon)*4.0/60.0 + self.zmin/60.0

        self.wozh = wozh
        self.woz_deg = (wozh-12.0)*15.0
        self.woz_rad = (np.pi/180.0)*self.woz_deg

        return wozh


    # declination
    def delta_update(self):
        term1 = self.x-77.51+1.92*np.sin((np.pi/180.0)*self.x)
        term2 = 0.3978*np.sin((np.pi/180.0)*term1)
        delta = np.arcsin(term2)
        self.delta = delta

        return delta
