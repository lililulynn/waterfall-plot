# sdr_scanner.py

import numpy as np
import matplotlib.pyplot as plt
import time
import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from datetime import datetime

class Scanner:
    def __init__(self, sample_rate, initial_center_freq, freq_increment, max_center_freq, fft_size, num_rows):
        # Initialize parameters
        self.sample_rate = sample_rate
        self.initial_center_freq = initial_center_freq
        self.freq_increment = freq_increment
        self.max_center_freq = max_center_freq
        self.fft_size = fft_size
        self.num_rows = num_rows

        # Initialize SDR device
        self.sdr = SoapySDR.Device(dict(driver="airspy"))
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, self.sample_rate)
        self.sdr.setGain(SOAPY_SDR_RX, 0, "LNA", 10)
        self.sdr.setGain(SOAPY_SDR_RX, 0, "MIX", 7)
        self.sdr.setGain(SOAPY_SDR_RX, 0, "VGA", 4)

    def scan_frequency(self, center_freq):
        # Set the center frequency for scanning
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, center_freq)

        # Setup the stream
        rxStream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        self.sdr.activateStream(rxStream)
        time.sleep(0.1)

        # Read data
        num_samples = self.fft_size * self.num_rows  
        samples = []
        start_time = time.perf_counter()
        while len(samples) < num_samples:
            buff = np.array([0] * self.fft_size, np.complex64)
            sr = self.sdr.readStream(rxStream, [buff], len(buff))
            if sr.ret > 0:
                samples.extend(buff[:sr.ret])
        end_time = time.perf_counter()

        # Deactivate and close the stream
        self.sdr.deactivateStream(rxStream)
        self.sdr.closeStream(rxStream)

        # Return the samples and elapsed time
        elapsed_time = end_time - start_time
        return samples, elapsed_time

    def generate_spectrogram(self, samples, center_freq):
        # Create a spectrogram from the samples
        spectrogram = np.zeros((self.num_rows, self.fft_size))
        for i in range(self.num_rows):
            spectrogram[i, :] = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[i * self.fft_size:(i + 1) * self.fft_size]))) ** 2)

        # Return the spectrogram
        return spectrogram