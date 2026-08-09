import json
import csv
import sys
import math
from pathlib import Path

def convert(json_path, csv_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    nx = data['dimensions']['N_x']
    ny = data['dimensions']['N_y']
    psi_real = data['psi_real']
    psi_imag = data['psi_imag']
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for y in range(ny):
            row = []
            for x in range(nx):
                idx = y * nx + x
                intensity = psi_real[idx]**2 + psi_imag[idx]**2
                row.append(intensity)
            writer.writerow(row)

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
