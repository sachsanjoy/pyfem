#Python2.7

#numpy '1.6.0'
#scipy '0.9.0'

#installation
#pip install numpy==1.6.0 & 1.11.1 for win
#pip install scipy==0.9.0 & 
#pip install pysca

#from pysca import Pysca
#from pysca.io import read_timeseries, write_params
import numpy as np
import sys
import core

def readARG():
    try:
        id = sys.argv[1] #file name
        fi = sys.argv[2] #initial frequency
        fn = sys.argv[3] #final frequency
        dn = sys.argv[4] #Signal to Noise calculation from +/- frequency range 
        n = sys.argv[5] #total number of frequencies to extraction
        return id,fi,fn,dn,n
    except:
        print('input parameter missing!')
readARG()
id = sys.argv[1]
fi = float(sys.argv[2])
fn = float(sys.argv[3])
dn = float(sys.argv[4])
n = int(sys.argv[5])
#t, a = read_timeseries('timeseries.fits')
dat = np.loadtxt(id)
t = dat[:,0]
a = dat[:,1]
p = core.pysca_loop(t, a, fi, fn, dn, n, fn, ofac=6.0)
#p.run(n)
#write_params(id+'.pysc', p.result, fmt='ascii', clobber=True)