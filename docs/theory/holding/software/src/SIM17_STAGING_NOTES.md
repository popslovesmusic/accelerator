# sim17 Staging Notes

## Purpose

`sim17` is staged as the shelf-resolution follow-up to `sim16`.

It does not extend to higher `kappa`. Instead, it resolves the new transition shelves that appeared at:
- `kappa = 0.11`
- `kappa = 0.12`

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

## Lower-shelf files

- [sim17_lower_shelf_kappa_0p11.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim17_lower_shelf_kappa_0p11.json)
- [sim17_lower_shelf_kappa_0p12.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim17_lower_shelf_kappa_0p12.json)

## Upper-shelf files

- [sim17_upper_shelf_kappa_0p11.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim17_upper_shelf_kappa_0p11.json)
- [sim17_upper_shelf_kappa_0p12.json](C:/Users/j/Documents/MPF/orientation/level2/src/sim17_upper_shelf_kappa_0p12.json)

## Execution logic

1. Run lower-shelf resolution batches.
2. Run upper-shelf resolution batches.
3. Summarize where `runaway`, `SS3`, `SS2`, and `other` occur at finer spacing.
4. Use that map to decide whether the shelf should be split into sub-regimes or treated as a continuous transition layer.
