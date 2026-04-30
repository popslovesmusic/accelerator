# Spectral Analysis C++ (v2.3)

C++ port of the spectral analysis layer for temporal signals and simple spatial grids.

## Scientific Rigor

- Emits recoverable `spectrum_report.json` with dominant modes.
- Removes temporal DC offset before spectral measurement.
- Computes total power and dominant mode concentration.
- Includes a sinusoid falsification/control case with known frequency.

## Usage

```powershell
.\spectral_analysis_v1_cpp\build_and_run.bat
```

For custom CSV input:

```powershell
.\spectral_analysis_v1_cpp\spectral_analysis_benchmark.exe --mode temporal --file path\metrics.csv --col order_parameter --out outputs\spectrum
```
