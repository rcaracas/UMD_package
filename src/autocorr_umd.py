#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### Author : Razvan Caracas

import sys, getopt, os, time, subprocess
import umd_processes_fast as umdpf
import crystallography as cr

import numpy as np
import matplotlib.pyplot as plt


def extract_data(MyStructure, entity):
    """
    Extract necessary data from MyStructure.

    Parameters:
    - MyStructure: List of snapshot data
    - entity: Entity to extract data for (e.g., 'atoms', 'pressure', 'volume', 'stress')

    Returns:
    - extracted_data: List of extracted data for the specified entity
    """
    extracted_data = []
    for snapshot in MyStructure:
        if entity == 'atoms':
            extracted_data.append(snapshot.atoms)
        elif entity == 'pressure':
            extracted_data.append(snapshot.pressure)
        elif entity == 'volume':
            extracted_data.append(snapshot.volume)
        elif entity == 'stress':
            extracted_data.append(snapshot.stress)
        else:
            raise ValueError("Invalid entity. Choose from 'atoms', 'pressure', 'volume', or 'stress'.")
    return extracted_data

def autocorrelation(x):
    """
    Compute the autocorrelation of each array in a 6D matrix.

    Parameters:
    - x: 6D numpy array containing up to 6 arrays

    Returns:
    - autocorr: Autocorrelation matrices for each array
    """
    x = np.asarray(x)
    dim = x.ndim

    if dim != 6:
        raise ValueError("Input must be a 6D array.")

    autocorr = np.zeros_like(x)

    for idx in range(x.shape[0]):
        array = x[idx]
        mean = np.mean(array)
        corr = np.correlate(array - mean, array - mean, mode='full')
        autocorr[idx] = corr[len(array) - 1:]

    return autocorr

def perform_fft(autocorr_values):
    """
    Perform Fast Fourier Transform (FFT) on autocorrelation values.

    Parameters:
    - autocorr_values: 6D numpy array containing autocorrelation values

    Returns:
    - fft_values: FFT values for each array
    """
    fft_values = np.fft.fft(autocorr_values, axis=-1)
    return fft_values

# Main function
def main():
    UMDfile = 'OUTCAR.umd.dat'
    umdpf.headerumd()
    firststep = 0
    WindowSize = 1000
    Property = 0            # 0=visosity, 1=vibr from vels, 2=vibr from pos
    try:
        opts, arg = getopt.getopt(argv,"hf:i:t:w:r:)
    except getopt.GetoptError:
        print ('autocorr_umd.py -f <umdfile> -i <InitialStep> -t <Temperature> -w <WindowSize>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('autocorr_umd.py program to compute the auto-correlation function of various time-dependent values')
            print ('autocorr_umd.py -f <umdfile> -i <InitialStep> -t <Temperature> -w <WindowSize> -r <Property>')
            print (' default values: -f OUTCAR.umd.dat -i 0 -t 300 -w 1000')
            print('-r options:')
            print('0 : viscosity')
            print('1 : vibrational spectrum from atomic velocities')
            print('1 : vibrational spectrum from atomic positions')
            sys.exit()
        elif opt in ("-f"):
            UMDfile = str(arg)
        elif opt in ("-i"):
            firststep = int(arg)
        elif opt in ("-w"):
            WindowSize = int(arg)
        elif opt in ("-r"):
            Property = int(arg)
    if (os.path.isfile(UMDname)):
        print('The first ',firststep, 'timesteps will be discarded')
        MyCrystal = cr.Lattice()
        AllSnapshots = [cr.Lattice]
        if Property == 0:
            (MyCrystal,AllSnapshots,TimeStep,length)=umdpf.read_values(UMDfile,"StressTensor","line",1,firststep,laststep=None,cutoff="all",nCores=None )

    else:
        print ('the umdfile ',UMDname,' does not exist')
        sys.exit()



    # Example structure
    MyStructure = [...]  # Fill this with your actual data

    # Extract necessary data from MyStructure for different entities
    entity = 'atoms'  # Change this to 'pressure', 'volume', 'stress', or 'atoms'
    extracted_data = extract_data(MyStructure, entity)

    # Perform autocorrelation on the extracted data
    autocorr_values = autocorrelation(extracted_data)

    # Perform FFT on autocorrelation values
    fft_values = perform_fft(autocorr_values)

    # Plot autocorrelation
    plt.figure(figsize=(8, 6))

    plt.subplot(2, 1, 1)
    for idx in range(autocorr_values.shape[0]):
        plt.plot(autocorr_values[idx], label=f'Array {idx+1}')
    plt.title('Autocorrelation')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation Value')
    plt.legend()

    # Plot FFT of autocorrelation
    plt.subplot(2, 1, 2)
    for idx in range(fft_values.shape[0]):
        plt.plot(np.abs(fft_values[idx]), label=f'Array {idx+1}')
    plt.title('FFT of Autocorrelation')
    plt.xlabel('Frequency')
    plt.ylabel('FFT Value (Magnitude)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()