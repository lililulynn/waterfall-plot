# main.py

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sdr_scanner import Scanner


def save_spectrogram(spectrograms_dir, spectrogram, center_freq, sample_rate):
    plt.figure()
    plt.imshow(spectrogram, aspect='auto', cmap='jet', extent=[center_freq - sample_rate/2, center_freq + sample_rate/2, 0, spectrogram.shape[0]])
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Time [s]")
    plt.colorbar(label="Power (dB)")
    plt.title(f"Center Frequency: {center_freq/1e6} MHz")
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_filename = os.path.join(spectrograms_dir, f'{current_time}_{center_freq/1e6}MHz.png')
    plt.savefig(image_filename)
    plt.close()

def main():
    samples_dir = 'samples'
    spectrograms_dir = 'spectrograms'
    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(spectrograms_dir, exist_ok=True)

    # Scan settings for 50-300MHz
    scanner = Scanner(10e6, 50e6, 5e6, 300e6, 1024, 500)
    all_samples =  []
    total_scan_time = 0
    center_freq = scanner.initial_center_freq
    
    while center_freq <= scanner.max_center_freq:
        # Scan the current frequency
        samples, elapsed_time = scanner.scan_frequency(center_freq)
        total_scan_time += elapsed_time

        # Generate and save the spectrogram for the current frequency
        spectrogram = scanner.generate_spectrogram(samples, center_freq)
        save_spectrogram(spectrograms_dir, spectrogram, center_freq, scanner.sample_rate)

        # Increment to the next frequency
        center_freq += scanner.freq_increment
        
    # Save the samples to a single.npy file
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    npy_filename = os.path.join(samples_dir, f'{current_time}.npy'})
    np.save(npy_filename, all_samples)

    print(f"Total scan time for all frequencies: {total_scan_time}s")

if __name__ == "__main__":
    main()