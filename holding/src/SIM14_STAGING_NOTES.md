# sim14 Staging Notes

## Purpose

`sim14` is staged as the next surface-expansion program after `sim13`.

It extends the now-closed local SS3 surface from:
- `kappa = 0.04, 0.05, 0.06`

to:
- `kappa = 0.07, 0.08`

## Runtime Assumptions

The staged configs preserve the validated runtime used in `sim12` and `sim13`:
- native backend
- `Nx = 1024`
- `T_max = 2000`
- `IC0` only for edge scans
- `8` seeds per point

Recommended command pattern:

```powershell
python -m src.batch_runner --config <config_path> --backend native --native-threads 1 --jobs 8 --fast --output-root <batch_dir>
```

## Lower-Edge Staging

- [sim14_lower_kappa_0p07.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim14_lower_kappa_0p07.json)
  - initial window: `lam = 0.058..0.072` step `0.001`

- [sim14_lower_kappa_0p08.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim14_lower_kappa_0p08.json)
  - initial window: `lam = 0.066..0.082` step `0.001`

These windows assume the monotone upward shift of `lambda_lower(kappa)` continues from `sim12`/`sim13`.

## Upper-Edge Staging

- [sim14_upper_kappa_0p07_coarse.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim14_upper_kappa_0p07_coarse.json)
  - initial window: `lam = 0.205..0.320` step `0.005`

- [sim14_upper_kappa_0p08_coarse.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim14_upper_kappa_0p08_coarse.json)
  - initial window: `lam = 0.255..0.380` step `0.005`

These are coarse search files only. After the first `SS2` point appears, the next step should be a local refinement file at step `0.001`, centered on the true bracket.

## Execution Logic

1. Run the lower-edge scans first.
2. Read off the new lower brackets.
3. Run the upper-edge coarse scans.
4. If a slice still does not hit `SS2`, extend only that slice upward.
5. If a slice brackets `SS3 -> SS2`, stage a refine file at `0.001` spacing for only that bracket.

## Expected Deliverables

- updated `lambda_lower(kappa)`
- updated `lambda_upper(kappa)`
- updated `band_width(kappa)`
- updated local surface table including `kappa = 0.07, 0.08`
