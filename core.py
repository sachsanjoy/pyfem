from __future__ import absolute_import, print_function
import numpy as np
import utils, fit
from utils import ExportDecorator, VerbosePrinter

__author__ = 'Kolja Glogowski, Wiebke Herzberg'
__maintainer__ = 'Kolja Glogowski'
__email__ = 'kolja@kis.uni-freiburg.de'
__license__ = 'MIT'
'''
def __init__(self, t, a, numin, numax, snr_width, ofac=6.0, hifreq=None,
                params=None, verbose=0):
    """
    Pysca(t, a, numin, numax, snr_width, ofac=6.0, hifreq=None)

    Parameters
    ----------
    t : array
        time values of the time series
    a : array
        amplitues of the time series
    numin : float
        minimum frequency value
    numax : float
        maximum frequency value
    snr_width : float
        frequency width around the extracted peak which is used for the
        signal-to-noise calculation
    ofac : float
        oversampling factor used for the Lomb-Scargle periodogram
    hifreq : None or float
        maximum frequency of the Lomb-Scargle periodogram; default: numax
    params : None or structured array
        custom parameters, e.g. from a previous run, default: None
    verbose : int
        verbose level from 0 (quiet) to 2 (verbose); default 0
    """
    self._t = np.asarray(t, dtype=np.float64)
    self._a = np.asarray(a, dtype=np.float64)
    if self._t.ndim != 1 or self._a.ndim != 1:
        raise ValueError('Input arrays must be 1d')
    elif len(self._t) != len(self._a):
        raise ValueError('Input arrays must have the same sizes')

    self._numin, self._numax = float(numin), float(numax)
    self._snr_width = float(snr_width) if snr_width else None
    self._ofac = float(ofac)
    self._hifreq = float(hifreq) if hifreq != None else self._numax
    self._verbose = int(verbose)
    self._vprint = VerbosePrinter(self._verbose)
    self._prev_ts = self._next_ts = None
    self._nu = self._orig_per = self._prev_per = self._next_per = None

    dnames = [ 'freq', 'amp', 'phase', 'noise', 'snr' ]
    if not self._snr_width:
        dnames = dnames[:3]
    if params != None and (dnames[0] in params.dtype.names):
        self._params = np.empty(
            len(params), dtype=[(dni, 'f8') for dni in dnames])
        for dni in dnames:
            if dni in params.dtype.names:
                self._params[dni] = params[dni]
            else:
                self._params[dni] = np.nan
    else:
        self._params = np.empty(0, dtype=[(dni, 'f8') for dni in dnames])
    self._params = self._params.view(np.recarray)

def _append_to_params(self, freq, amp, phase, noise=np.nan, snr=np.nan):
    a = np.empty(self._params.shape[0]+1, dtype=self._params.dtype)
    a[:-1] = self._params
    if len(a.dtype) == 3:
        a[-1] = (freq, amp, phase)
    else:
        a[-1] = (freq, amp, phase, noise, snr)
    self._params = a.view(np.recarray)

def _update_params(freq, amp, phase, noise=None, snr=None):
    a = np.empty(self._params.shape[0]+1, dtype=self._params.dtype)
    a = a.view(np.recarray)
    a.freq = freq
    a.amp = amp
    a.phase = phase
    if len(a.dtype) > 3:
        if noise != None:
            a.noise = noise
        else:
            a.noise.fill(np.nan)
        if snr != None:
            a.snr = snr
        else:
            a.snr.fill(np.nan)
    self._params = a

@property
def snr_width(self):
    return self._snr_width

@property
def ofac(self):
    return self._ofac

@property
def hifreq(self):
    return self._hifreq

@property
def t(self):
    return self._t

@property
def orig_ts(self):
    return self._a

@property
def prev_ts(self):
    return self._prev_ts

@property
def next_ts(self):
    return self._next_ts

#@property
#def _nuidx(self):
#    return self._nuidx

def nu():
    if nu == []:
        nu, orig_per = calc_periodogram(t,a)
        nuidx = (nu >= numin) & (nu <= numax)
    return nu

@property
def orig_periodogram(self):
    if self._orig_per == None:
        tmp = self.nu
        #assert (self._nu - self._orig_per).all()
    return self._orig_per

@property
def prev_periodogram(self):
    return self._prev_per

@property
def next_periodogram(self):
    return self._next_per

@property
def count(self):
    return len(self._params)

@property
def result(self):
    return self._params

def _find_highest_peak(nu, per, use_nuidx=True):
    if use_nuidx:
        # Limit the periodogram to selected frequency range.
        nu = nu[self._nuidx]
        per = per[self._nuidx]
    return utils.find_highest_peak(nu, per)

def step(t, a, fi, fn, n):   
    # There are already parameters, so we need to prewhiten the
    # original time series, in order to get the next periodogram;
    # in case any amplitudes or phases are missing or wrong, we
    # first perform a fit to the time series.
    amp = 1.0
    phase = 0.5
    new_amp, new_phase, ok, misc = fit.fit_timeseries(t,a,freq,amp,phase)
    
    if not ok:
        raise PyscaError('Harmonic fit failed [ier=%d]' % misc[3])
    
    new_ts = fit.prewhiten(t, a, freq, new_amp, new_phase)
    new_nu, new_per = self._calc_periodogram(self.t, new_ts)
    self._next_per = new_per
    self._next_ts = new_ts
    self.orig_periodogram
    
    # Select the next periodogram
    nu, per = self.nu, self.next_periodogram
    ##############
    # Find frequency of the highest peak in the current periodogram
    new_freq = np.r_[self._params.freq, self._find_highest_peak(nu, per)]
    vprint('Frequency #%d:' % len(new_freq), new_freq[-1], v=1)

    # Fit original time series using already extracted mode parameters
    vprint('Fitting time series...', v=2)
    new_amp, new_phase, ok, misc = fit.fit_timeseries(self.t,
        self.orig_ts, new_freq, self._params.amp, self._params.phase)
    if not ok:
        raise PyscaError('Harmonic fit failed for peak frequency %f' % (
            new_freq[-1]) + ' [ier=%d]' % misc[3])
    vprint('Freq: ', new_freq[-1], ', Amp: ', new_amp[-1], ', Phase: ',
            new_phase[-1], sep='', v=1)

    # Prewhiten the original time series using the new mode parameters
    vprint('Prewhitening...', v=2)
    new_ts = fit.prewhiten(self.t, self.orig_ts, new_freq, new_amp,
                            new_phase)

    # Compute new periodogram from the prewhitened time series
    new_nu, new_per = self._calc_periodogram(self.t, new_ts)

    # Compute noise for the last extracted frequency using the median
    if self.snr_width:
        noise = utils.median_noise_level(
            nu, new_per, new_freq[-1], self.snr_width)
        snr = new_amp[-1] / noise
        new_noise = np.r_[self._params.noise, noise]
        new_snr = np.r_[self._params.snr, snr]
        vprint('Noise: ', new_noise[-1], ', SNR: ',new_snr[-1],
                sep='', v=1)
    else:
        new_noise = new_snr = None

    # Update object data
    self._update_params(new_freq, new_amp, new_phase, new_noise, new_snr)
    self._prev_per = self._next_per
    self._prev_ts = self._next_ts
    self._next_per = new_per
    self._next_ts = new_ts

def check_term_conditions(amp_limit=None, snr_limit=None):
    """
    Check if the last extracted mode parameters are above the provided
    limits.

    Parameters
    ----------
    amp_limit : scalar
        amplitude limit; default: no limit
    snr_limit : scalar
        signal-to-noise limit; default: no limit

    Returns
    -------
    True, if the limits are met; otherwise False.
    """
    if len(self._params) == 0:
        return True
    amp_limit = float(amp_limit) if amp_limit != None else None
    snr_limit = float(snr_limit) if snr_limit != None else None
    if amp_limit != None and self._params.amp[-1] < amp_limit:
        return False
    if snr_limit != None and self._params.snr[-1] < snr_limit:
        return False
    return True

def run(t, a, fi, fn, n=1, amp_limit=None, snr_limit=None):
    """
    Parameters
    ----------
    n : int or None
        number of steps; default: no limit
    amp_limit : float or None
        amplitude limit (termination condition); default: no limit
    snr_limit : float or None
        signal-to-noise limit (termination condition); default: no limit

    Returns
    -------
        number of iterations
    """
    #n = int(n) if n != None else None
    #if n == None and amp_limit == None and snr_limit == None:
    #    raise ValueError('No termination condition specified')

    i = 0
    while True:
        #if n != None and i >= n:
        #    break
        #if not check_term_conditions(amp_limit, snr_limit):
        #    break
        step(t, a, fi, fn, n)
        #vprint(v=1)
        i += 1
    return i
'''
#error estimation using random Montecarlo method
def error_montec(t,a,numin,numax,mu,sigma,ofac,hifreq,nm=100):
    print('Performing Montecarlo error estimation...')
    imp_freq = np.zeros(1)
    for i in range(nm):
        # creating a random gaussian noise with the same dimension as the dataset from the noise levels of the data. 
        noise = np.random.normal(mu, sigma, len(t)) 
        a1 = a + noise
        nu, per = utils.compute_periodogram(t, a1, ofac,hifreq)
        nuidx = (nu >= numin) & (nu <= numax)
        use_nuidx = True
        if use_nuidx == True:
            # Limit the periodogram to selected frequency range.
            nu = nu[nuidx]
            per = per[nuidx]
        print('Finding highest peak...')
        new_freq = utils.find_highest_peak(nu, per)
        imp_freq = np.vstack((imp_freq,new_freq))
        #calculating mean estimation and standard error = std/sqrt(n)
        print(np.median(imp_freq[1:])/86400.0,np.std(imp_freq[1:])*86400)
        #print(np.mean(aa),np.sqrt(np.mean(abs(aa - np.mean(aa))**2)))
    #return new_nu

def pysca(t, a, numin, numax, snr_width,n, hifreq, ofac=6.0):
    print('Computing periodogram...')
    orig_nu, orig_per = utils.compute_periodogram(t, a, ofac,hifreq)
    print(orig_nu, orig_per)
    nuidx = (orig_nu >= numin) & (orig_nu <= numax)
    use_nuidx = True
    if use_nuidx == True:
        # Limit the periodogram to selected frequency range.
        nu = orig_nu[nuidx]
        per = orig_per[nuidx]
    print('Finding highest peak...')
    new_freq = utils.find_highest_peak(nu, per)
    print(new_freq)
    # Fit original time series using already extracted mode parameters
    print('Fitting time series...')
    amp, phase = 1, 0
    new_amp, new_phase, ok, misc = fit.fit_timeseries(t,a, new_freq, amp, phase)
    if not ok:
        raise PyscaError('Harmonic fit failed for peak frequency %f' % (
            new_freq[-1]) + ' [ier=%d]' % misc[3])
    print('Freq: ', new_freq, ', Amp: ', new_amp, ', Phase: ', new_phase)
    # Prewhiten the original time series using the new mode parameters
    print('Prewhitening...')
    new_ts = fit.prewhiten(t, a, new_freq, new_amp, new_phase)
    print(np.shape(new_ts))

    import matplotlib.pyplot as plt
    plt.plot(t,a,'-r')
    plt.plot(t,new_ts,'-g')
    plt.show()
    
    # Compute noise for the last extracted frequency using the median
    noise = utils.median_noise_level(nu, per, new_freq,snr_width)
    snr = new_amp / noise
    print('noise: ',noise,', snr:',snr)
    #error_montec(t,a,numin,numax,0,noise,ofac,hifreq,100)
    #new_noise = 
    #new_snr = 

def pysca_loop(t, a, numin, numax, snr_width,n, hifreq, ofac=6.0):
    new_ts = a
    pw_fq = np.zeros(1)
    pw_amp= np.zeros(1)
    pw_phase = np.zeros(1)
    pw_snr = np.zeros(1)
    pw_noise = np.zeros(1)

    for i in range(n):
        orig_nu, orig_per = utils.compute_periodogram(t, new_ts, ofac,hifreq)
        nuidx = (orig_nu >= numin) & (orig_nu <= numax)
        use_nuidx = True
        if use_nuidx == True:
            # Limit the periodogram to selected frequency range.
            nu = orig_nu[nuidx]
            per = orig_per[nuidx]
        new_freq = utils.find_highest_peak(nu, per)
        # Fit original time series using already extracted mode parameters
        amp, phase = 1, 0
        new_amp, new_phase, ok, misc = fit.fit_timeseries(t,a, new_freq, amp, phase)
        if not ok:
            raise PyscaError('Harmonic fit failed for peak frequency %f' % (
                new_freq[-1]) + ' [ier=%d]' % misc[3])
        # Prewhiten the original time series using the new mode parameters
        new_ts = fit.prewhiten(t, new_ts, new_freq, new_amp, new_phase)

        #import matplotlib.pyplot as plt
        #plt.plot(t,a,'-r')
        #plt.plot(t,new_ts,'-g')
        #plt.show()
        # Compute noise for the last extracted frequency using the median
        noise = utils.median_noise_level(nu, per, new_freq,snr_width)
        snr = new_amp / noise
        print(str(i)+') Freq: ', '%16.16f'%new_freq, ', Amp: ', '%16.16f'%new_amp[0], ', Phase: ', '%16.16f'%new_phase[0],', snr: ','%16.16f'%snr[0], ', noise: ','%16.16f'%noise)
        pw_fq = np.vstack((pw_fq,new_freq))
        pw_amp =  np.vstack((pw_amp,new_amp[0]))
        pw_phase =  np.vstack((pw_phase,new_phase[0]))
        pw_snr =  np.vstack((pw_snr,snr[0]))
        pw_noise =  np.vstack((pw_noise,noise))
        error_montec(t,a,numin,numax,0,noise,ofac,hifreq,)
    
    pw_data = np.column_stack((pw_fq[1:],pw_amp[1:]))
    pw_data = np.column_stack((pw_data,pw_phase[1:]))
    pw_data = np.column_stack((pw_data,pw_snr[1:]))
    pw_data = np.column_stack((pw_data,pw_noise[1:]))
    return pw_data
        
    error_montec(t,a,numin,numax,0,noise,ofac,hifreq,100)
    #new_noise = 
    #new_snr = 