# sim15 Staging Notes

## Purpose

`sim15` is staged as the next SS3 surface-extension program after `sim14`.

It extends the resolved surface from:
- `kappa = 0.04..0.08`

to:
- `kappa = 0.09, 0.10`

## Runtime

Use the same validated geometry runtime:
- native backend
- `Nx = 1024`
- `T_max = 2000`
- `IC0`
- `8` seeds
- `--jobs 8`
- `--native-threads 1`
- `--fast`

## Lower-edge files

- [sim15_lower_kappa_0p09.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim15_lower_kappa_0p09.json)
- [sim15_lower_kappa_0p10.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim15_lower_kappa_0p10.json)

## Upper-edge files

- [sim15_upper_kappa_0p09_coarse.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim15_upper_kappa_0p09_coarse.json)
- [sim15_upper_kappa_0p10_coarse.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim15_upper_kappa_0p10_coarse.json)

## Execution logic

1. Run lower-edge scans first.
2. Read the new lower brackets.
3. Run upper-edge coarse scans.
4. If a coarse scan brackets `SS3 -> SS2`, stage a local `0.001` refinement file.
5. If a coarse scan does not reach `SS2`, extend only that slice upward.
