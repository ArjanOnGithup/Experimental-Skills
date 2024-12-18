import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.interpolate import interp1d

def welch_psd(ibi_times, ibi_values, fs=4):
    """
    Analyzes the frequency domain of an Inter-Beat Interval (IBI) series using Welch's PSD method
    and visualizes the spectral power in VLF, LF, and HF bands.

    This function interpolates the IBI series onto a uniform time grid, calculates the Power Spectral
    Density (PSD) using Welch's method, and integrates the power in the physiologically relevant bands:
    VLF (0.003–0.04 Hz), LF (0.04–0.15 Hz), and HF (0.15–0.4 Hz). The results are plotted, highlighting
    these bands in different colors, and key measures are labeled on the plot.

    Parameters:
    -----------
    ibi_times : array-like
        Timestamps of the IBIs (in seconds), typically derived from the R-peak times of an ECG.
    ibi_values : array-like
        Inter-Beat Interval values (in seconds), i.e., the time between successive heartbeats.
    fs : int, optional
        Resampling frequency in Hz (default: 4 Hz). This should be at least 2x the HF upper limit (0.4 Hz)
        to satisfy the Nyquist criterion and ensure accurate PSD estimation.

    Returns:
    --------
    spectral_measures : dict
        A dictionary containing the following spectral measures:
        - 'VLF Power': Power in the Very Low Frequency band (0.003–0.04 Hz).
        - 'LF Power': Power in the Low Frequency band (0.04–0.15 Hz).
        - 'HF Power': Power in the High Frequency band (0.15–0.4 Hz).
        - 'LF/HF Ratio': Ratio of LF power to HF power, an indicator of sympathovagal balance.

    References:
    -----------
    - Task Force of the European Society of Cardiology and the North American Society of Pacing
      and Electrophysiology. "Heart rate variability: Standards of measurement, physiological
      interpretation, and clinical use." *Circulation* 93.5 (1996): 1043-1065.
    - Mulder, L. J. M., and van Roon, A. "Spectral Analysis of Heart Rate Variability." In *Tools and 
      Techniques for Stress Assessment and Management* (1998).

    Notes:
    ------
    - Welch's method is used for spectral estimation due to its robustness against noise and short epochs.
    - Interpolation ensures uniform sampling, which is a requirement for Fourier-based methods like Welch.
    - The LF/HF ratio is commonly used to assess autonomic nervous system regulation.
    """
    # 1. Interpolate IBI values onto a uniform time grid
    # Uniform time grid based on the start and end of the IBI times, sampled at 'fs' Hz
    time_uniform = np.arange(ibi_times[0], ibi_times[-1], 1/fs)  # Regular time grid at fs Hz
    
    # Linear interpolation of IBI values to match the uniform grid
    interp_func = interp1d(ibi_times, ibi_values, kind='linear', fill_value='extrapolate')
    ibi_resampled = interp_func(time_uniform)

    # 2. Compute the Power Spectral Density (PSD) using Welch's method
    # Welch's method parameters:
    # - nperseg: Segment size (256 samples at fs=4 Hz -> 64-second segments)
    # - noverlap: 50% overlap between segments (128 samples)
    # - window: Hamming window to minimize spectral leakage
    f, psd = welch(ibi_resampled, fs=fs, nperseg=256, noverlap=128, window='hamming')

    # 3. Define frequency bands of interest for HRV analysis
    vlf_band = (0.003, 0.04)  # Very Low Frequency (VLF)
    lf_band = (0.04, 0.15)    # Low Frequency (LF)
    hf_band = (0.15, 0.4)     # High Frequency (HF)

    # Helper function to compute power in a specified frequency range using numerical integration
    def band_power(frequencies, power_spectrum, band):
        """
        Computes the power within a specific frequency band using the trapezoidal rule.

        Parameters:
        - frequencies: array of frequency values.
        - power_spectrum: array of PSD values corresponding to the frequencies.
        - band: tuple (f_low, f_high) defining the frequency range.

        Returns:
        - Power within the specified band.
        """
        idx = np.logical_and(frequencies >= band[0], frequencies <= band[1])
        return np.trapz(power_spectrum[idx], frequencies[idx])  # Integrate PSD over the band

    # 4. Calculate power in each frequency band
    vlf_power = band_power(f, psd, vlf_band)
    lf_power = band_power(f, psd, lf_band)
    hf_power = band_power(f, psd, hf_band)
    lf_hf_ratio = lf_power / hf_power  # LF/HF Ratio (sympathovagal balance)

    # 5. Store spectral measures in a dictionary
    spectral_measures = {
        'VLF Power': vlf_power,
        'LF Power': lf_power,
        'HF Power': hf_power,
        'LF/HF Ratio': lf_hf_ratio
    }

    # 6. Create a graphical representation of the PSD with highlighted bands
    plt.figure(figsize=(10, 6))
    plt.plot(f, psd, color='black', linewidth=1.5, label='PSD Spectrum')

    # Highlight the VLF, LF, and HF bands with colored regions
    plt.fill_between(f, 0, psd, where=(f >= vlf_band[0]) & (f <= vlf_band[1]),
                     color='blue', alpha=0.3, label='VLF (0.003-0.04 Hz)')
    plt.fill_between(f, 0, psd, where=(f >= lf_band[0]) & (f <= lf_band[1]),
                     color='green', alpha=0.3, label='LF (0.04-0.15 Hz)')
    plt.fill_between(f, 0, psd, where=(f >= hf_band[0]) & (f <= hf_band[1]),
                     color='red', alpha=0.3, label='HF (0.15-0.4 Hz)')

    # Add plot labels and title
    plt.title('Power Spectral Density of IBI Series (Welch\'s Method)', fontsize=14)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Power Spectral Density (s²/Hz)', fontsize=12)
    plt.legend(loc='upper right')

    # Annotate the power values on the plot
    plt.text(0.02, max(psd)*0.9, f"VLF Power: {vlf_power:.4f}", color='blue', fontsize=10)
    plt.text(0.02, max(psd)*0.8, f"LF Power: {lf_power:.4f}", color='green', fontsize=10)
    plt.text(0.02, max(psd)*0.7, f"HF Power: {hf_power:.4f}", color='red', fontsize=10)
    plt.text(0.02, max(psd)*0.6, f"LF/HF Ratio: {lf_hf_ratio:.2f}", color='black', fontsize=10)

    # Display the plot
    plt.tight_layout()
    plt.show()

    return spectral_measures