import numpy as np
from scipy.signal import welch, find_peaks

def compute_temporal_psd(signal, fs=1.0):
    """
    Computes the Power Spectral Density of a 1D signal.
    """
    if len(signal) < 32:
        return None, None
        
    f, psd = welch(signal, fs=fs, nperseg=min(len(signal), 256))
    return f, psd

def compute_spatial_power(grid):
    """
    Computes the 2D power spectrum of a 2D grid.
    """
    if grid.ndim != 2:
        return None
        
    # 2D FFT and shift zero-frequency component to the center
    f_transform = np.fft.fft2(grid)
    f_shift = np.fft.fftshift(f_transform)
    power_spectrum = np.abs(f_shift)**2
    
    return power_spectrum

def radial_profile(data, center=None):
    """
    Computes the radial average of a 2D array.
    """
    y, x = np.indices((data.shape))
    if not center:
        center = np.array([(y.max()-y.min())/2.0, (x.max()-x.min())/2.0])

    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    r = r.astype(int)

    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile

def detect_dominant_modes(f, power, n=5):
    """
    Finds the top n peaks in the spectrum.
    """
    peaks, properties = find_peaks(power, height=0)
    peak_heights = properties['peak_heights']
    
    # Sort by height
    top_indices = np.argsort(peak_heights)[-n:][::-1]
    
    modes = []
    for idx in top_indices:
        modes.append({
            "frequency": float(f[peaks[idx]]),
            "power": float(peak_heights[idx])
        })
    return modes
