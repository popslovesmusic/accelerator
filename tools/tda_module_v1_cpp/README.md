# TDA Module C++ (v2.3)

C++ port of the Betti-0 connected-component topology module.

## Scientific Rigor

- Computes 8-neighbor connected components for thresholded 2D fields.
- Emits count, max component size, mean component size, and active fraction.
- Includes built-in controls for empty, single-component, and two-component masks.

## Usage

```powershell
.\tda_module_v1_cpp\build_and_run.bat
```

For custom CSV grid input:

```powershell
.\tda_module_v1_cpp\tda_benchmark.exe --file grid.csv --threshold 0.5 --out outputs\tda
```
